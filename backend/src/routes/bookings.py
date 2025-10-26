from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models.user import db, User
from src.models.equipment import Equipment
from src.models.booking import Booking
from src.routes.verification import can_rent_equipment, calculate_trust_level
from src.utils.email_notifications import send_booking_confirmation_email, send_new_booking_notification_email

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    """Create a new booking"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['equipment_id', 'start_date', 'end_date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Get equipment
    equipment = Equipment.query.get(data['equipment_id'])
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    if not equipment.is_available:
        return jsonify({'error': 'Equipment is not available'}), 400
    
    # Check renter's trust level
    renter = User.query.get(user_id)
    can_rent, trust_message = can_rent_equipment(renter, equipment.daily_price)
    
    if not can_rent:
        return jsonify({
            'error': 'Trust level insufficient',
            'message': trust_message,
            'trust_level': renter.trust_level,
            'equipment_price': equipment.daily_price
        }), 403
    
    # Parse dates
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Validate dates
    if start_date >= end_date:
        return jsonify({'error': 'End date must be after start date'}), 400
    
    if start_date < datetime.now().date():
        return jsonify({'error': 'Start date cannot be in the past'}), 400
    
    # Check for conflicting bookings
    conflicting_bookings = Booking.query.filter(
        Booking.equipment_id == data['equipment_id'],
        Booking.status.in_(['pending', 'confirmed', 'active']),
        Booking.start_date <= end_date,
        Booking.end_date >= start_date
    ).first()
    
    if conflicting_bookings:
        return jsonify({'error': 'Equipment is already booked for these dates'}), 400
    
    # Calculate costs
    total_days = (end_date - start_date).days
    daily_rate = equipment.daily_price
    total_cost = total_days * daily_rate
    deposit_amount = total_cost * 0.5  # 50% deposit
    
    # Create booking
    new_booking = Booking(
        equipment_id=data['equipment_id'],
        renter_id=user_id,
        start_date=start_date,
        end_date=end_date,
        total_days=total_days,
        daily_rate=daily_rate,
        total_cost=total_cost,
        deposit_amount=deposit_amount,
        status='pending'
    )
    
    db.session.add(new_booking)
    db.session.commit()
    
    # Send email notifications
    try:
        owner = User.query.get(equipment.owner_id)
        send_booking_confirmation_email(new_booking, equipment, renter, owner)
        send_new_booking_notification_email(new_booking, equipment, renter, owner)
    except Exception as e:
        print(f"Error sending booking emails: {e}")
    
    return jsonify({
        'message': 'Booking created successfully',
        'booking': new_booking.to_dict()
    }), 201

@bookings_bp.route('/bookings/<int:booking_id>', methods=['GET'])
@jwt_required()
def get_booking(booking_id):
    """Get a specific booking"""
    user_id = int(get_jwt_identity())
    booking = Booking.query.get(booking_id)
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Check if user is the renter or equipment owner
    if booking.renter_id != user_id and booking.equipment.owner_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(booking.to_dict()), 200

@bookings_bp.route('/my-bookings', methods=['GET'])
@jwt_required()
def get_my_bookings():
    """Get all bookings for the current user (as renter)"""
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(renter_id=user_id).all()
    
    return jsonify([booking.to_dict() for booking in bookings]), 200

@bookings_bp.route('/equipment/<int:equipment_id>/bookings', methods=['GET'])
@jwt_required()
def get_equipment_bookings(equipment_id):
    """Get all bookings for a specific equipment (owner only)"""
    user_id = int(get_jwt_identity())
    equipment = Equipment.query.get(equipment_id)
    
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    # Check if user is the owner
    if equipment.owner_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    bookings = Booking.query.filter_by(equipment_id=equipment_id).all()
    
    return jsonify([booking.to_dict() for booking in bookings]), 200

@bookings_bp.route('/bookings/<int:booking_id>/status', methods=['PUT'])
@jwt_required()
def update_booking_status(booking_id):
    """Update booking status (owner can confirm, renter can cancel)"""
    user_id = int(get_jwt_identity())
    booking = Booking.query.get(booking_id)
    
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    data = request.get_json()
    new_status = data.get('status')
    
    if not new_status:
        return jsonify({'error': 'Status is required'}), 400
    
    # Check permissions
    is_owner = booking.equipment.owner_id == user_id
    is_renter = booking.renter_id == user_id
    
    if not (is_owner or is_renter):
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Validate status transitions
    if new_status == 'confirmed' and is_owner and booking.status == 'pending':
        booking.status = 'confirmed'
    elif new_status == 'cancelled' and is_renter and booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
    elif new_status == 'active' and is_owner and booking.status == 'confirmed':
        booking.status = 'active'
    elif new_status == 'completed' and is_owner and booking.status == 'active':
        booking.status = 'completed'
        
        # Update renter's trust level
        renter = User.query.get(booking.renter_id)
        if renter:
            completed_count = Booking.query.filter_by(
                renter_id=booking.renter_id,
                status='completed'
            ).count()
            
            renter.completed_rentals = completed_count
            renter.trust_level = calculate_trust_level(
                completed_count,
                renter.is_identity_verified or renter.is_credit_checked
            )
    else:
        return jsonify({'error': 'Invalid status transition'}), 400
    
    db.session.commit()
    
    return jsonify({
        'message': 'Booking status updated successfully',
        'booking': booking.to_dict()
    }), 200

