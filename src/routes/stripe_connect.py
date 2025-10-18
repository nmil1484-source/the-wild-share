from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import stripe
import os
from src.models.user import db, User

stripe_connect_bp = Blueprint('stripe_connect', __name__)

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_placeholder')

PLATFORM_COMMISSION_RATE = 0.12  # 12% commission

@stripe_connect_bp.route('/create-connect-account', methods=['POST'])
@jwt_required()
def create_connect_account():
    """Create a Stripe Connect account for an equipment owner"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user is an owner
    if user.user_type not in ['owner', 'both']:
        return jsonify({'error': 'Only equipment owners can create Connect accounts'}), 403
    
    # Check if user already has a Stripe account
    if user.stripe_account_id:
        return jsonify({
            'message': 'Connect account already exists',
            'account_id': user.stripe_account_id,
            'onboarding_complete': user.stripe_onboarding_complete
        }), 200
    
    try:
        # Create Stripe Connect Express account
        account = stripe.Account.create(
            type='express',
            country='US',
            email=user.email,
            capabilities={
                'card_payments': {'requested': True},
                'transfers': {'requested': True},
            },
            business_type='individual',
            business_profile={
                'name': f"{user.first_name} {user.last_name}",
                'product_description': 'Outdoor equipment rental',
            }
        )
        
        # Save account ID to user
        user.stripe_account_id = account.id
        db.session.commit()
        
        return jsonify({
            'message': 'Connect account created successfully',
            'account_id': account.id
        }), 201
        
    except stripe.error.StripeError as e:
        return jsonify({
            'error': 'Failed to create Connect account',
            'message': str(e)
        }), 500

@stripe_connect_bp.route('/create-onboarding-link', methods=['POST'])
@jwt_required()
def create_onboarding_link():
    """Create an onboarding link for owner to complete Stripe setup"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user.stripe_account_id:
        return jsonify({'error': 'No Connect account found. Create one first.'}), 400
    
    data = request.get_json()
   refresh_url = data.get('refresh_url', 'https://www.thewildshare.com')
return_url = data.get('return_url', 'https://www.thewildshare.com')
    
    try:
        # Create account link for onboarding
        account_link = stripe.AccountLink.create(
            account=user.stripe_account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type='account_onboarding',
        )
        
        return jsonify({
            'onboarding_url': account_link.url
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({
            'error': 'Failed to create onboarding link',
            'message': str(e)
        }), 500

@stripe_connect_bp.route('/check-onboarding-status', methods=['GET'])
@jwt_required()
def check_onboarding_status():
    """Check if owner has completed Stripe onboarding"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.stripe_account_id:
        return jsonify({
            'onboarding_complete': False,
            'has_account': False
        }), 200
    
    try:
        # Retrieve account details from Stripe
        account = stripe.Account.retrieve(user.stripe_account_id)
        
        # Check if charges and payouts are enabled
        charges_enabled = account.charges_enabled
        payouts_enabled = account.payouts_enabled
        details_submitted = account.details_submitted
        
        onboarding_complete = charges_enabled and payouts_enabled and details_submitted
        
        # Update user record
        if onboarding_complete != user.stripe_onboarding_complete:
            user.stripe_onboarding_complete = onboarding_complete
            db.session.commit()
        
        return jsonify({
            'onboarding_complete': onboarding_complete,
            'has_account': True,
            'charges_enabled': charges_enabled,
            'payouts_enabled': payouts_enabled,
            'details_submitted': details_submitted
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({
            'error': 'Failed to check onboarding status',
            'message': str(e)
        }), 500

@stripe_connect_bp.route('/dashboard-link', methods=['POST'])
@jwt_required()
def create_dashboard_link():
    """Create a link to Stripe Express Dashboard for owner to manage their account"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or not user.stripe_account_id:
        return jsonify({'error': 'No Connect account found'}), 404
    
    try:
        # Create login link to Stripe Express Dashboard
        login_link = stripe.Account.create_login_link(user.stripe_account_id)
        
        return jsonify({
            'dashboard_url': login_link.url
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({
            'error': 'Failed to create dashboard link',
            'message': str(e)
        }), 500

