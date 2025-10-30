from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db
from datetime import datetime, timedelta
import stripe
import os

subscription_bp = Blueprint('subscription', __name__)

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

# Pricing configuration
PRICING_TIERS = {
    'free': {
        'name': 'Free',
        'price': 0,
        'price_id': None,
        'max_listings': 3,
        'max_photos': 3,
        'transaction_fee': 0,  # NO FEES!
        'features': [
            'List up to 3 items',
            'Basic listing photos (3 per item)',
            'Standard search visibility',
            '✅ Full messaging access',
            '✅ Profile reviews (give & receive)',
            '✅ Basic rental contract template',
            '✅ 50% deposit option (recommended)',
            'Basic calendar management',
            'Secure payment processing',
            '7-day booking window',
            '✅ NO transaction fees',
            '✅ NO hidden costs'
        ]
    },
    'pro': {
        'name': 'Pro Owner',
        'price': 5.00,
        'price_monthly': 'price_pro_monthly',  # Replace with actual Stripe Price ID
        'price_yearly': 'price_pro_yearly',    # Replace with actual Stripe Price ID
        'max_listings': 999,  # Unlimited
        'max_photos': 10,
        'transaction_fee': 0,  # NO FEES!
        'features': [
            'Unlimited listings',
            'Priority search placement',
            'Up to 10 photos per item',
            'Advanced analytics dashboard',
            'Featured badge on all listings',
            'Flexible pricing (seasonal, weekly, monthly)',
            'Instant booking option',
            '30-day booking window',
            'Bulk editing tools',
            'Priority customer support',
            'Revenue insights and reports',
            'Promotional tools (discount codes)',
            '✅ NO transaction fees - keep 100% of your earnings',
            '✅ Premium rental contract templates',
            '✅ Contract customization tools',
            '✅ Damage protection documentation',
            '✅ Legal protection for both parties',
            '✅ Priority customer support'
        ]
    },
    'business': {
        'name': 'Business',
        'price': 20.00,
        'price_monthly': 'price_business_monthly',  # Replace with actual Stripe Price ID
        'price_yearly': 'price_business_yearly',    # Replace with actual Stripe Price ID
        'max_listings': 999,  # Unlimited
        'max_photos': 20,
        'transaction_fee': 0,  # NO FEES!
        'features': [
            'Everything in Pro, PLUS:',
            'Verified Business Badge',
            'Custom branding on listings',
            'Multi-user access (team accounts)',
            'API access for integrations',
            'Bulk import from CSV',
            'Advanced inventory management',
            'Automated pricing suggestions',
            'White-label booking widget',
            'Dedicated account manager',
            'Custom insurance options',
            'Priority placement in all searches',
            'Featured homepage placement',
            '✅ NO transaction fees - keep 100% of your earnings',
            '✅ Premium contract templates (customizable)',
            '✅ Liability waivers included',
            '✅ Insurance documentation support',
            '✅ Dispute resolution assistance',
            '✅ Legal consultation (1 hour/year)',
            '✅ Priority dispute resolution'
        ]
    }
}

@subscription_bp.route('/pricing', methods=['GET'])
def get_pricing():
    """Get pricing tiers and features"""
    return jsonify({
        'tiers': PRICING_TIERS
    }), 200

@subscription_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_subscription():
    """Get current user's subscription details"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    tier_info = PRICING_TIERS.get(user.subscription_tier, PRICING_TIERS['free'])
    
    return jsonify({
        'tier': user.subscription_tier,
        'status': user.subscription_status,
        'start_date': user.subscription_start_date.isoformat() if user.subscription_start_date else None,
        'end_date': user.subscription_end_date.isoformat() if user.subscription_end_date else None,
        'trial_ends_at': user.trial_ends_at.isoformat() if user.trial_ends_at else None,
        'features': tier_info['features'],
        'max_listings': tier_info['max_listings'],
        'max_photos': tier_info['max_photos'],
        'transaction_fee': tier_info['transaction_fee'],
        'stripe_subscription_id': user.stripe_subscription_id
    }), 200

@subscription_bp.route('/create-checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    """Create Stripe Checkout session for subscription"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    tier = data.get('tier')  # 'pro' or 'business'
    billing_period = data.get('billing_period', 'monthly')  # 'monthly' or 'yearly'
    
    if tier not in ['pro', 'business']:
        return jsonify({'error': 'Invalid tier'}), 400
    
    # Get the appropriate price ID
    price_key = f'price_{billing_period}'
    price_id = PRICING_TIERS[tier].get(price_key)
    
    if not price_id:
        return jsonify({'error': 'Price ID not configured'}), 500
    
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
                'price': price_id,
                'quantity': 1
            }],
            mode='subscription',
            success_url=f"{os.getenv('FRONTEND_URL', 'https://thewildshare.com')}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{os.getenv('FRONTEND_URL', 'https://thewildshare.com')}/pricing",
            metadata={
                'user_id': user.id,
                'tier': tier
            },
            subscription_data={
                'trial_period_days': 30,  # 30-day free trial
                'metadata': {
                    'user_id': user.id,
                    'tier': tier
                }
            }
        )
        
        return jsonify({
            'checkout_url': checkout_session.url,
            'session_id': checkout_session.id
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

@subscription_bp.route('/success', methods=['POST'])
@jwt_required()
def subscription_success():
    """Handle successful subscription creation"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    session_id = data.get('session_id')
    
    try:
        # Retrieve the checkout session
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid' or session.status == 'complete':
            subscription = stripe.Subscription.retrieve(session.subscription)
            
            # Update user subscription
            user.subscription_tier = session.metadata.get('tier', 'pro')
            user.stripe_subscription_id = subscription.id
            user.subscription_status = subscription.status
            user.subscription_start_date = datetime.fromtimestamp(subscription.current_period_start)
            user.subscription_end_date = datetime.fromtimestamp(subscription.current_period_end)
            
            # Set trial end date if in trial
            if subscription.status == 'trialing' and subscription.trial_end:
                user.trial_ends_at = datetime.fromtimestamp(subscription.trial_end)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Subscription activated successfully',
                'tier': user.subscription_tier,
                'status': user.subscription_status
            }), 200
        else:
            return jsonify({'error': 'Payment not completed'}), 400
            
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

@subscription_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel user's subscription"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user.stripe_subscription_id:
        return jsonify({'error': 'No active subscription'}), 400
    
    try:
        # Cancel at period end (don't cancel immediately)
        subscription = stripe.Subscription.modify(
            user.stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        user.subscription_status = 'canceled'
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription will be canceled at the end of the billing period',
            'end_date': user.subscription_end_date.isoformat() if user.subscription_end_date else None
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

@subscription_bp.route('/reactivate', methods=['POST'])
@jwt_required()
def reactivate_subscription():
    """Reactivate a canceled subscription"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user.stripe_subscription_id:
        return jsonify({'error': 'No subscription to reactivate'}), 400
    
    try:
        # Remove the cancellation
        subscription = stripe.Subscription.modify(
            user.stripe_subscription_id,
            cancel_at_period_end=False
        )
        
        user.subscription_status = subscription.status
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription reactivated successfully',
            'status': user.subscription_status
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

@subscription_bp.route('/portal', methods=['GET'])
@jwt_required()
def customer_portal():
    """Create Stripe Customer Portal session for managing subscription"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user.stripe_customer_id:
        return jsonify({'error': 'No Stripe customer found'}), 400
    
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=user.stripe_customer_id,
            return_url=f"{os.getenv('FRONTEND_URL', 'https://thewildshare.com')}/dashboard"
        )
        
        return jsonify({
            'portal_url': portal_session.url
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400

@subscription_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events for subscription updates"""
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
    if event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        user_id = subscription['metadata'].get('user_id')
        
        if user_id:
            user = User.query.get(int(user_id))
            if user:
                user.subscription_status = subscription['status']
                user.subscription_end_date = datetime.fromtimestamp(subscription['current_period_end'])
                db.session.commit()
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        user_id = subscription['metadata'].get('user_id')
        
        if user_id:
            user = User.query.get(int(user_id))
            if user:
                user.subscription_tier = 'free'
                user.subscription_status = 'canceled'
                user.stripe_subscription_id = None
                db.session.commit()
    
    elif event['type'] == 'customer.subscription.trial_will_end':
        subscription = event['data']['object']
        user_id = subscription['metadata'].get('user_id')
        
        if user_id:
            # TODO: Send email notification that trial is ending
            pass
    
    return jsonify({'status': 'success'}), 200

# Helper function to check if user has access to a feature
def has_feature_access(user, feature):
    """Check if user's subscription tier has access to a feature"""
    tier_info = PRICING_TIERS.get(user.subscription_tier, PRICING_TIERS['free'])
    
    # Check if subscription is active (or in trial)
    if user.subscription_tier != 'free':
        if user.subscription_status not in ['active', 'trialing']:
            # Subscription expired or canceled, downgrade to free
            return PRICING_TIERS['free']
    
    return tier_info

def get_transaction_fee(user):
    """Get the transaction fee percentage for user's tier"""
    tier_info = has_feature_access(user, 'transaction_fee')
    return tier_info.get('transaction_fee', 0.05)

def get_max_listings(user):
    """Get maximum number of listings for user's tier"""
    tier_info = has_feature_access(user, 'max_listings')
    return tier_info.get('max_listings', 3)

def get_max_photos(user):
    """Get maximum number of photos per listing for user's tier"""
    tier_info = has_feature_access(user, 'max_photos')
    return tier_info.get('max_photos', 3)

