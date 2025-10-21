from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import stripe
import os
from src.models.user import db, User
from src.models.booking import Booking
from src.models.payment import Payment
from src.models.equipment import Equipment

payments_bp = Blueprint('payments', __name__)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_placeholder')

PLATFORM_COMMISSION_RATE = 0.12  # 12% platform commission

@payments_bp.route('/create-payment-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    """Create a Stripe payment intent for a booking with platform commission"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    booking_id = data.get('booking_id')
    if not booking_id:
        return jsonify({'error': 'booking_id is required'}), 400
    
    # Get booking
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Check if user is the renter
    if booking.renter_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get equipment owner
    equipment = Equipment.query.get(booking.equipment_id)
    owner = User.query.get(equipment.owner_id)
    
    # Check if owner has completed Stripe onboarding
    if not owner.stripe_account_id or not owner.stripe_onboarding_complete:
        return jsonify({
            'error': 'Equipment owner has not completed payment setup',
            'message': 'The owner needs to connect their bank account before accepting bookings'
        }), 400
    
    # Calculate amounts
    total_amount = booking.total_cost + booking.deposit_amount
    platform_fee = booking.total_cost * PLATFORM_COMMISSION_RATE
    owner_payout = booking.total_cost - platform_fee
    
    try:
        # Create Stripe payment intent with destination charge (Stripe Connect)
        # This charges the customer and automatically splits the payment
        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),  # Stripe uses cents
            currency='usd',
            application_fee_amount=int(platform_fee * 100),  # Platform commission
            transfer_data={
                'destination': owner.stripe_account_id,  # Owner's Connect account
            },
            metadata={
                'booking_id': booking_id,
                'renter_id': user_id,
                'owner_id': owner.id,
                'rental_cost': booking.total_cost,
                'deposit_amount': booking.deposit_amount,
                'platform_fee': platform_fee,
                'owner_payout': owner_payout
            }
        )
        
        # Create payment records
        rental_payment = Payment(
            booking_id=booking_id,
            payment_type='rental',
            amount=booking.total_cost,
            stripe_payment_id=intent.id,
            status='pending'
        )
        
        deposit_payment = Payment(
            booking_id=booking_id,
            payment_type='deposit',
            amount=booking.deposit_amount,
            stripe_payment_id=intent.id,
            status='pending'
        )
        
        db.session.add(rental_payment)
        db.session.add(deposit_payment)
        db.session.commit()
        
        return jsonify({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id,
            'total_amount': total_amount,
            'rental_cost': booking.total_cost,
            'deposit_amount': booking.deposit_amount,
            'platform_fee': platform_fee,
            'owner_receives': owner_payout,
            'breakdown': {
                'rental_cost': booking.total_cost,
                'platform_commission_12_percent': platform_fee,
                'owner_payout_88_percent': owner_payout,
                'deposit_held': booking.deposit_amount
            }
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({
            'error': 'Payment processing error',
            'message': str(e),
            'note': 'To enable payments, configure your Stripe API key in environment variables'
        }), 500

@payments_bp.route('/confirm-payment', methods=['POST'])
@jwt_required()
def confirm_payment():
    """Confirm payment completion"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    payment_intent_id = data.get('payment_intent_id')
    if not payment_intent_id:
        return jsonify({'error': 'payment_intent_id is required'}), 400
    
    # Find payments with this intent ID
    payments = Payment.query.filter_by(stripe_payment_id=payment_intent_id).all()
    
    if not payments:
        return jsonify({'error': 'Payment not found'}), 404
    
    # Update payment status
    for payment in payments:
        payment.status = 'completed'
    
    # Update booking status to confirmed
    booking = Booking.query.get(payments[0].booking_id)
    if booking:
        booking.status = 'confirmed'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Payment confirmed successfully',
        'note': 'Owner will receive their payout (88% of rental cost) automatically to their bank account',
        'booking': booking.to_dict() if booking else None
    }), 200

@payments_bp.route('/confirm-return', methods=['POST'])
@jwt_required()
def confirm_return():
    """Owner confirms equipment returned in good condition and refunds deposit"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    booking_id = data.get('booking_id')
    equipment_condition = data.get('condition', 'good')  # good, damaged
    damage_cost = data.get('damage_cost', 0)  # Amount to deduct from deposit if damaged
    
    if not booking_id:
        return jsonify({'error': 'booking_id is required'}), 400
    
    # Get booking
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Check if user is the equipment owner
    if booking.equipment.owner_id != user_id:
        return jsonify({'error': 'Only equipment owner can confirm return'}), 403
    
    # Check if booking is active or confirmed
    if booking.status not in ['confirmed', 'active']:
        return jsonify({'error': 'Booking must be active to confirm return'}), 400
    
    # Find deposit payment
    deposit_payment = Payment.query.filter_by(
        booking_id=booking_id,
        payment_type='deposit',
        status='completed'
    ).first()
    
    if not deposit_payment:
        return jsonify({'error': 'Deposit payment not found'}), 404
    
    try:
        refund_amount = deposit_payment.amount
        
        # If equipment is damaged, deduct damage cost from deposit
        if equipment_condition == 'damaged' and damage_cost > 0:
            damage_cost = min(damage_cost, deposit_payment.amount)  # Can't exceed deposit
            refund_amount = deposit_payment.amount - damage_cost
            
            # Create damage charge record
            damage_payment = Payment(
                booking_id=booking_id,
                payment_type='damage_charge',
                amount=damage_cost,
                stripe_payment_id=deposit_payment.stripe_payment_id,
                status='completed'
            )
            db.session.add(damage_payment)
        
        # Refund the remaining deposit (or full deposit if no damage)
        if refund_amount > 0:
            refund = stripe.Refund.create(
                payment_intent=deposit_payment.stripe_payment_id,
                amount=int(refund_amount * 100)
            )
            
            # Create refund payment record
            refund_payment = Payment(
                booking_id=booking_id,
                payment_type='refund',
                amount=refund_amount,
                stripe_payment_id=refund.id,
                status='completed'
            )
            db.session.add(refund_payment)
        
        # Update deposit payment status
        deposit_payment.status = 'refunded' if refund_amount == deposit_payment.amount else 'partially_refunded'
        
        # Update booking status to completed
        booking.status = 'completed'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Equipment return confirmed successfully',
            'deposit_refunded': refund_amount,
            'damage_charge': damage_cost if equipment_condition == 'damaged' else 0,
            'equipment_condition': equipment_condition,
            'note': 'Deposit has been automatically refunded to the renter'
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({
            'error': 'Refund processing error',
            'message': str(e)
        }), 500

@payments_bp.route('/refund-deposit', methods=['POST'])
@jwt_required()
def refund_deposit():
    """Legacy endpoint - redirects to confirm_return"""
    return confirm_return()

@payments_bp.route('/bookings/<int:booking_id>/payments', methods=['GET'])
@jwt_required()
def get_booking_payments(booking_id):
    """Get all payments for a booking with detailed breakdown"""
    user_id = int(get_jwt_identity())
    
    # Get booking
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Check if user is the renter or equipment owner
    if booking.renter_id != user_id and booking.equipment.owner_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    payments = Payment.query.filter_by(booking_id=booking_id).all()
    
    # Calculate breakdown
    platform_fee = booking.total_cost * PLATFORM_COMMISSION_RATE
    owner_payout = booking.total_cost - platform_fee
    
    return jsonify({
        'payments': [payment.to_dict() for payment in payments],
        'breakdown': {
            'total_rental_cost': booking.total_cost,
            'platform_commission_12_percent': round(platform_fee, 2),
            'owner_receives_88_percent': round(owner_payout, 2),
            'deposit_amount': booking.deposit_amount
        }
    }), 200

@payments_bp.route('/my-earnings', methods=['GET'])
@jwt_required()
def get_my_earnings():
    """Get earnings summary for equipment owner"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user or user.user_type not in ['owner', 'both']:
        return jsonify({'error': 'Only equipment owners can view earnings'}), 403
    
    # Get all completed bookings for this owner's equipment
    from sqlalchemy import func
    
    earnings = db.session.query(
        func.sum(Booking.total_cost).label('total_revenue'),
        func.count(Booking.id).label('total_bookings')
    ).join(Equipment).filter(
        Equipment.owner_id == user_id,
        Booking.status == 'completed'
    ).first()
    
    total_revenue = earnings.total_revenue or 0
    total_bookings = earnings.total_bookings or 0
    platform_fees = total_revenue * PLATFORM_COMMISSION_RATE
    net_earnings = total_revenue - platform_fees
    
    return jsonify({
        'total_bookings': total_bookings,
        'gross_revenue': round(total_revenue, 2),
        'platform_fees_12_percent': round(platform_fees, 2),
        'net_earnings_88_percent': round(net_earnings, 2),
        'stripe_account_connected': user.stripe_onboarding_complete,
        'note': 'Earnings are automatically transferred to your bank account within 2-7 business days'
    }), 200

