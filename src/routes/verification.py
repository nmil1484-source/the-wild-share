from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models.user import db, User
from src.models.booking import Booking

verification_bp = Blueprint('verification', __name__)

# Trust level thresholds
TRUST_LEVELS = {
    'new': {'min_rentals': 0, 'max_price': 100, 'label': 'New Renter'},
    'bronze': {'min_rentals': 1, 'max_price': 200, 'label': 'Bronze'},
    'silver': {'min_rentals': 4, 'max_price': 500, 'label': 'Silver'},
    'gold': {'min_rentals': 11, 'max_price': 999999, 'label': 'Gold'}
}

def calculate_trust_level(completed_rentals, is_verified=False):
    """Calculate trust level based on completed rentals"""
    if is_verified:
        return 'gold'  # Verified users get gold immediately
    
    if completed_rentals >= 11:
        return 'gold'
    elif completed_rentals >= 4:
        return 'silver'
    elif completed_rentals >= 1:
        return 'bronze'
    else:
        return 'new'

def can_rent_equipment(user, equipment_price):
    """Check if user's trust level allows renting this equipment"""
    trust_info = TRUST_LEVELS.get(user.trust_level, TRUST_LEVELS['new'])
    
    # Verified or credit-checked users can rent anything
    if user.is_identity_verified or user.is_credit_checked:
        return True, None
    
    # Check price limit for trust level
    if equipment_price > trust_info['max_price']:
        return False, f"Your trust level ({trust_info['label']}) limits rentals to ${trust_info['max_price']}/day. This item is ${equipment_price}/day. Complete more rentals or verify your identity to unlock higher-value items."
    
    return True, None

@verification_bp.route('/trust-info', methods=['GET'])
@jwt_required()
def get_trust_info():
    """Get current user's trust level and requirements"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    current_level = TRUST_LEVELS.get(user.trust_level, TRUST_LEVELS['new'])
    
    # Calculate next level
    next_level = None
    if user.trust_level == 'new':
        next_level = {'level': 'bronze', 'rentals_needed': 1 - user.completed_rentals}
    elif user.trust_level == 'bronze':
        next_level = {'level': 'silver', 'rentals_needed': 4 - user.completed_rentals}
    elif user.trust_level == 'silver':
        next_level = {'level': 'gold', 'rentals_needed': 11 - user.completed_rentals}
    
    return jsonify({
        'trust_level': user.trust_level,
        'trust_label': current_level['label'],
        'completed_rentals': user.completed_rentals,
        'max_daily_price': current_level['max_price'],
        'is_verified': user.is_identity_verified or user.is_credit_checked,
        'next_level': next_level,
        'benefits': {
            'new': 'Rent items up to $100/day',
            'bronze': 'Rent items up to $200/day (1+ completed rentals)',
            'silver': 'Rent items up to $500/day (4+ completed rentals)',
            'gold': 'Rent any item (11+ completed rentals or verified)',
            'verified': 'Rent any item immediately (identity or credit check)'
        }
    }), 200

@verification_bp.route('/verify-identity', methods=['POST'])
@jwt_required()
def verify_identity():
    """
    Initiate identity verification process
    In production, integrate with Stripe Identity or Plaid
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    verification_type = data.get('type', 'identity')  # identity or credit
    
    # In production, integrate with verification service
    # For now, return instructions
    
    if verification_type == 'credit':
        return jsonify({
            'message': 'Credit check initiated',
            'instructions': 'To enable credit checks, integrate with Plaid or Stripe Identity',
            'status': 'pending',
            'verification_url': 'https://stripe.com/docs/identity',
            'note': 'This is a placeholder. In production, this would redirect to verification service.'
        }), 200
    else:
        return jsonify({
            'message': 'Identity verification initiated',
            'instructions': 'Upload government ID and take selfie',
            'status': 'pending',
            'verification_url': 'https://stripe.com/docs/identity',
            'note': 'This is a placeholder. In production, this would redirect to Stripe Identity.'
        }), 200

@verification_bp.route('/verify-identity/complete', methods=['POST'])
@jwt_required()
def complete_verification():
    """
    Complete verification (webhook from verification service)
    In production, this would be called by Stripe/Plaid webhook
    """
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    verification_type = data.get('type', 'identity')
    
    # Mark user as verified
    if verification_type == 'credit':
        user.is_credit_checked = True
    else:
        user.is_identity_verified = True
    
    user.verification_date = datetime.utcnow()
    
    # Upgrade to gold level immediately
    user.trust_level = 'gold'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Verification completed successfully',
        'trust_level': 'gold',
        'can_rent_any_item': True
    }), 200

@verification_bp.route('/update-trust-level', methods=['POST'])
def update_trust_level_webhook():
    """
    Update user trust level after booking completion
    Called internally when booking is marked as completed
    """
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Count completed rentals
    completed_count = Booking.query.filter_by(
        renter_id=user_id,
        status='completed'
    ).count()
    
    user.completed_rentals = completed_count
    
    # Calculate new trust level
    new_level = calculate_trust_level(
        completed_count,
        user.is_identity_verified or user.is_credit_checked
    )
    
    old_level = user.trust_level
    user.trust_level = new_level
    
    db.session.commit()
    
    level_upgraded = old_level != new_level
    
    return jsonify({
        'message': 'Trust level updated',
        'old_level': old_level,
        'new_level': new_level,
        'completed_rentals': completed_count,
        'level_upgraded': level_upgraded
    }), 200

@verification_bp.route('/check-rental-eligibility', methods=['POST'])
@jwt_required()
def check_rental_eligibility():
    """Check if user can rent a specific equipment"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    equipment_price = data.get('daily_price')
    
    if not equipment_price:
        return jsonify({'error': 'daily_price required'}), 400
    
    can_rent, message = can_rent_equipment(user, float(equipment_price))
    
    return jsonify({
        'can_rent': can_rent,
        'message': message,
        'user_trust_level': user.trust_level,
        'user_max_price': TRUST_LEVELS[user.trust_level]['max_price'],
        'equipment_price': equipment_price,
        'suggestion': 'Complete more rentals or verify your identity to unlock this item.' if not can_rent else None
    }), 200

@verification_bp.route('/trust-levels', methods=['GET'])
def get_trust_levels():
    """Get information about all trust levels"""
    return jsonify({
        'levels': [
            {
                'level': 'new',
                'label': 'New Renter',
                'min_rentals': 0,
                'max_daily_price': 100,
                'description': 'Start small and build your reputation'
            },
            {
                'level': 'bronze',
                'label': 'Bronze',
                'min_rentals': 1,
                'max_daily_price': 200,
                'description': 'Complete 1 rental to unlock'
            },
            {
                'level': 'silver',
                'label': 'Silver',
                'min_rentals': 4,
                'max_daily_price': 500,
                'description': 'Complete 4 rentals to unlock'
            },
            {
                'level': 'gold',
                'label': 'Gold',
                'min_rentals': 11,
                'max_daily_price': 999999,
                'description': 'Complete 11 rentals or verify identity'
            },
            {
                'level': 'verified',
                'label': 'Verified',
                'min_rentals': 0,
                'max_daily_price': 999999,
                'description': 'Pass identity or credit check to unlock immediately'
            }
        ]
    }), 200

