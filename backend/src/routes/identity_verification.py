from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import stripe
import os
from datetime import datetime

from ..models.user import db, User
from ..models.identity_verification import IdentityVerification

identity_verification_bp = Blueprint('identity_verification', __name__)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

@identity_verification_bp.route('/identity/create-verification-session', methods=['POST'])
@jwt_required()
def create_verification_session():
    """Create a Stripe Identity verification session"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user already has a pending or verified session
        existing_verification = IdentityVerification.query.filter_by(
            user_id=user_id
        ).filter(
            IdentityVerification.status.in_(['pending', 'verified'])
        ).first()
        
        if existing_verification and existing_verification.status == 'verified':
            return jsonify({'error': 'User is already verified'}), 400
        
        # Create Stripe Identity verification session
        verification_session = stripe.identity.VerificationSession.create(
            type='document',
            metadata={
                'user_id': str(user_id),
                'email': user.email
            },
            options={
                'document': {
                    'allowed_types': ['driving_license', 'passport', 'id_card'],
                    'require_live_capture': True,
                    'require_matching_selfie': True
                }
            }
        )
        
        # Save verification record to database
        verification = IdentityVerification(
            user_id=user_id,
            stripe_verification_session_id=verification_session.id,
            status='pending',
            verification_type='document'
        )
        db.session.add(verification)
        db.session.commit()
        
        return jsonify({
            'session_id': verification_session.id,
            'client_secret': verification_session.client_secret,
            'url': verification_session.url,
            'status': verification_session.status
        }), 200
        
    except stripe.error.StripeError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@identity_verification_bp.route('/identity/verification-status', methods=['GET'])
@jwt_required()
def get_verification_status():
    """Get the current verification status for the user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get the most recent verification
        verification = IdentityVerification.query.filter_by(
            user_id=user_id
        ).order_by(IdentityVerification.created_at.desc()).first()
        
        if not verification:
            return jsonify({
                'is_verified': False,
                'status': 'not_started',
                'verification': None
            }), 200
        
        # If status is pending, check with Stripe for updates
        if verification.status == 'pending':
            try:
                stripe_session = stripe.identity.VerificationSession.retrieve(
                    verification.stripe_verification_session_id
                )
                
                # Update local status if it changed
                if stripe_session.status != verification.status:
                    verification.status = stripe_session.status
                    
                    if stripe_session.status == 'verified':
                        verification.verified_at = datetime.utcnow()
                        user.is_identity_verified = True
                        user.verification_date = datetime.utcnow()
                        
                        # Extract verification details if available
                        if stripe_session.verified_outputs:
                            verification.verified_name = stripe_session.verified_outputs.get('first_name', '') + ' ' + stripe_session.verified_outputs.get('last_name', '')
                            if stripe_session.verified_outputs.get('dob'):
                                dob = stripe_session.verified_outputs['dob']
                                verification.verified_dob = datetime(dob['year'], dob['month'], dob['day']).date()
                    
                    db.session.commit()
                    
            except stripe.error.StripeError as e:
                print(f"Error checking Stripe verification status: {e}")
        
        return jsonify({
            'is_verified': user.is_identity_verified,
            'status': verification.status,
            'verification': verification.to_dict() if verification else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@identity_verification_bp.route('/identity/webhook', methods=['POST'])
def identity_webhook():
    """Handle Stripe Identity webhook events"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get('STRIPE_IDENTITY_WEBHOOK_SECRET')
    
    if not webhook_secret:
        print("Warning: STRIPE_IDENTITY_WEBHOOK_SECRET not set")
        return jsonify({'error': 'Webhook secret not configured'}), 500
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'identity.verification_session.verified':
        session = event['data']['object']
        handle_verification_success(session)
    elif event['type'] == 'identity.verification_session.requires_input':
        session = event['data']['object']
        handle_verification_requires_input(session)
    elif event['type'] == 'identity.verification_session.canceled':
        session = event['data']['object']
        handle_verification_canceled(session)
    
    return jsonify({'status': 'success'}), 200


def handle_verification_success(session):
    """Handle successful verification"""
    try:
        verification = IdentityVerification.query.filter_by(
            stripe_verification_session_id=session['id']
        ).first()
        
        if verification:
            verification.status = 'verified'
            verification.verified_at = datetime.utcnow()
            
            # Update user verification status
            user = User.query.get(verification.user_id)
            if user:
                user.is_identity_verified = True
                user.verification_date = datetime.utcnow()
            
            # Extract verification details
            if session.get('verified_outputs'):
                outputs = session['verified_outputs']
                verification.verified_name = outputs.get('first_name', '') + ' ' + outputs.get('last_name', '')
                if outputs.get('dob'):
                    dob = outputs['dob']
                    verification.verified_dob = datetime(dob['year'], dob['month'], dob['day']).date()
            
            if session.get('last_verification_report'):
                report = session['last_verification_report']
                if report.get('document'):
                    doc = report['document']
                    verification.document_type = doc.get('type')
                    verification.document_country = doc.get('issuing_country')
            
            db.session.commit()
            print(f"Verification successful for user {verification.user_id}")
    except Exception as e:
        print(f"Error handling verification success: {e}")
        db.session.rollback()


def handle_verification_requires_input(session):
    """Handle verification that requires additional input"""
    try:
        verification = IdentityVerification.query.filter_by(
            stripe_verification_session_id=session['id']
        ).first()
        
        if verification:
            verification.status = 'requires_input'
            db.session.commit()
            print(f"Verification requires input for user {verification.user_id}")
    except Exception as e:
        print(f"Error handling verification requires input: {e}")
        db.session.rollback()


def handle_verification_canceled(session):
    """Handle canceled verification"""
    try:
        verification = IdentityVerification.query.filter_by(
            stripe_verification_session_id=session['id']
        ).first()
        
        if verification:
            verification.status = 'canceled'
            db.session.commit()
            print(f"Verification canceled for user {verification.user_id}")
    except Exception as e:
        print(f"Error handling verification canceled: {e}")
        db.session.rollback()

