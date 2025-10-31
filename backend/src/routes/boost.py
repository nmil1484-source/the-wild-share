from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from src.models.equipment import Equipment
from datetime import datetime, timedelta
import stripe
import os

boost_bp = Blueprint('boost', __name__)

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Boost pricing
BOOST_PRICING = {
    'boost_7_days': {
        'name': 'Boost 7 Days',
        'price': 2.99,
        'duration_days': 7,
        'description': 'Feature your listing at the top of search results for 7 days',
        'price_id': 'price_boost_7_days'  # Replace with actual Stripe Price ID
    },
    'boost_30_days': {
        'name': 'Boost 30 Days',
        'price': 9.99,
        'duration_days': 30,
        'description': 'Feature your listing at the top of search results for 30 days',
        'price_id': 'price_boost_30_days'  # Replace with actual Stripe Price ID
    },
    'homepage_featured': {
        'name': 'Homepage Featured',
        'price': 19.99,
        'duration_days': 7,
        'description': 'Feature your listing on the homepage carousel for 7 days',
        'price_id': 'price_homepage_featured'  # Replace with actual Stripe Price ID
    }
}

@boost_bp.route('/pricing', methods=['GET'])
def get_boost_pricing():
    """Get boost pricing options"""
    return jsonify({
        'pricing': BOOST_PRICING
    }), 200

@boost_bp.route('/purchase', methods=['POST'])
@jwt_required()
def purchase_boost():
    """Create Stripe checkout session for boost purchase"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    equipment_id = data.get('equipment_id')
    boost_type = data.get('boost_type')  # 'boost_7_days', 'boost_30_days', 'homepage_featured'
    
    if not equipment_id or not boost_type:
        return jsonify({'error': 'Missing equipment_id or boost_type'}), 400
    
    if boost_type not in BOOST_PRICING:
        return jsonify({'error': 'Invalid boost type'}), 400
    
    # Verify equipment exists and belongs to user
    equipment = Equipment.query.get(equipment_id)
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    if equipment.owner_id != user_id:
        return jsonify({'error': 'You can only boost your own equipment'}), 403
    
    boost_info = BOOST_PRICING[boost_type]
    
    try:
        # Create or retrieve Stripe customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}",
                metadata={'user_id': user.id}
            )
            user.stripe_customer_id = customer.id
            db.session.commit()
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=user.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': int(boost_info['price'] * 100),  # Convert to cents
                    'product_data': {
                        'name': boost_info['name'],
                        'description': boost_info['description'],
                    },
                },
                'quantity': 1
            }],
            mode='payment',
            success_url=f"{os.getenv('FRONTEND_URL', 'https://thewildshare.com')}/boost/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('FRONTEND_URL', 'https://thewildshare.com')}/equipment",
            metadata={
                'user_id': user.id,
                'equipment_id': equipment_id,
                'boost_type': boost_type
            }
        )
        
        return jsonify({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

@boost_bp.route('/success', methods=['POST'])
@jwt_required()
def boost_success():
    """Handle successful boost purchase"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    session_id = data.get('session_id')
    
    try:
        # Retrieve the checkout session
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            equipment_id = int(session.metadata.get('equipment_id'))
            boost_type = session.metadata.get('boost_type')
            
            equipment = Equipment.query.get(equipment_id)
            if not equipment:
                return jsonify({'error': 'Equipment not found'}), 404
            
            boost_info = BOOST_PRICING[boost_type]
            duration_days = boost_info['duration_days']
            
            # Apply the boost
            if boost_type == 'homepage_featured':
                equipment.is_homepage_featured = True
                equipment.homepage_featured_expires_at = datetime.utcnow() + timedelta(days=duration_days)
            else:
                equipment.is_boosted = True
                equipment.boost_expires_at = datetime.utcnow() + timedelta(days=duration_days)
            
            equipment.total_boosts_purchased += 1
            db.session.commit()
            
            return jsonify({
                'message': 'Boost activated successfully',
                'equipment': equipment.to_dict(),
                'expires_at': equipment.boost_expires_at.isoformat() if equipment.boost_expires_at else equipment.homepage_featured_expires_at.isoformat()
            }), 200
        else:
            return jsonify({'error': 'Payment not completed'}), 400
            
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

@boost_bp.route('/status/<int:equipment_id>', methods=['GET'])
def get_boost_status(equipment_id):
    """Get boost status for an equipment"""
    equipment = Equipment.query.get(equipment_id)
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    now = datetime.utcnow()
    
    # Check if boosts have expired
    if equipment.is_boosted and equipment.boost_expires_at and equipment.boost_expires_at < now:
        equipment.is_boosted = False
        equipment.boost_expires_at = None
        db.session.commit()
    
    if equipment.is_homepage_featured and equipment.homepage_featured_expires_at and equipment.homepage_featured_expires_at < now:
        equipment.is_homepage_featured = False
        equipment.homepage_featured_expires_at = None
        db.session.commit()
    
    return jsonify({
        'is_boosted': equipment.is_boosted,
        'boost_expires_at': equipment.boost_expires_at.isoformat() if equipment.boost_expires_at else None,
        'is_homepage_featured': equipment.is_homepage_featured,
        'homepage_featured_expires_at': equipment.homepage_featured_expires_at.isoformat() if equipment.homepage_featured_expires_at else None,
        'total_boosts_purchased': equipment.total_boosts_purchased
    }), 200

@boost_bp.route('/webhook', methods=['POST'])
def boost_webhook():
    """Handle Stripe webhook events for boost purchases"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        if session.payment_status == 'paid' and session.metadata:
            equipment_id = int(session.metadata.get('equipment_id'))
            boost_type = session.metadata.get('boost_type')
            
            equipment = Equipment.query.get(equipment_id)
            if equipment and boost_type in BOOST_PRICING:
                boost_info = BOOST_PRICING[boost_type]
                duration_days = boost_info['duration_days']
                
                # Apply the boost
                if boost_type == 'homepage_featured':
                    equipment.is_homepage_featured = True
                    equipment.homepage_featured_expires_at = datetime.utcnow() + timedelta(days=duration_days)
                else:
                    equipment.is_boosted = True
                    equipment.boost_expires_at = datetime.utcnow() + timedelta(days=duration_days)
                
                equipment.total_boosts_purchased += 1
                db.session.commit()
    
    return jsonify({'status': 'success'}), 200

# Helper function to check and expire old boosts
def expire_old_boosts():
    """Expire boosts that have passed their expiration date"""
    now = datetime.utcnow()
    
    # Expire regular boosts
    expired_boosts = Equipment.query.filter(
        Equipment.is_boosted == True,
        Equipment.boost_expires_at < now
    ).all()
    
    for equipment in expired_boosts:
        equipment.is_boosted = False
        equipment.boost_expires_at = None
    
    # Expire homepage featured
    expired_featured = Equipment.query.filter(
        Equipment.is_homepage_featured == True,
        Equipment.homepage_featured_expires_at < now
    ).all()
    
    for equipment in expired_featured:
        equipment.is_homepage_featured = False
        equipment.homepage_featured_expires_at = None
    
    if expired_boosts or expired_featured:
        db.session.commit()
    
    return len(expired_boosts) + len(expired_featured)

