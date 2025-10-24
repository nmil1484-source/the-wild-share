from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from src.models.user import db, User

auth_bp = Blueprint('auth', __name__)
# Using werkzeug for password hashing

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Hash password
    password_hash = generate_password_hash(data['password'])
    
    # Create new user
    new_user = User(
        email=data['email'],
        password_hash=password_hash,
        first_name=data['first_name'],
        last_name=data['last_name'],
        phone=data.get('phone'),
        user_type=data.get('user_type', 'renter')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    # Create access token with string identity
    access_token = create_access_token(identity=str(new_user.id))
    
    return jsonify({
        'message': 'User registered successfully',
        'access_token': access_token,
        'user': new_user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate required fields
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Find user
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Create access token with string identity
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update allowed fields
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'user_type' in data:
        user.user_type = data['user_type']
    if 'profile_image_url' in data:
        user.profile_image_url = data['profile_image_url']
    if 'bio' in data:
        user.bio = data['bio']
    if 'address' in data:
        user.address = data['address']
    if 'city' in data:
        user.city = data['city']
    if 'state' in data:
        user.state = data['state']
    if 'zip_code' in data:
        user.zip_code = data['zip_code']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profile updated successfully',
        'user': user.to_dict()
    }), 200

@auth_bp.route('/delete-account', methods=['DELETE'])
@jwt_required()
def delete_account():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Delete the user (cascade will delete related equipment and bookings)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Account deleted successfully'
    }), 200






# Password Reset Functionality
import secrets
from datetime import datetime, timedelta

# Store password reset tokens temporarily (in production, use Redis or database)
password_reset_tokens = {}

@auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    """Request a password reset token"""
    data = request.get_json()
    
    if 'email' not in data:
        return jsonify({'error': 'Email is required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        # Don't reveal if email exists or not (security best practice)
        return jsonify({
            'message': 'If an account with that email exists, a password reset link has been sent.'
        }), 200
    
    # Generate secure reset token
    reset_token = secrets.token_urlsafe(32)
    
    # Store token with expiration (15 minutes)
    password_reset_tokens[reset_token] = {
        'user_id': user.id,
        'email': user.email,
        'expires_at': datetime.utcnow() + timedelta(minutes=15)
    }
    
    # In production, send email with reset link
    # For now, return the token (for testing)
    reset_link = f"https://www.thewildshare.com/reset-password?token={reset_token}"
    
    # TODO: Send email with reset_link
    # For development, we'll return it in the response
    return jsonify({
        'message': 'If an account with that email exists, a password reset link has been sent.',
        'reset_link': reset_link,  # Remove this in production
        'token': reset_token  # Remove this in production
    }), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token"""
    data = request.get_json()
    
    if 'token' not in data or 'new_password' not in data:
        return jsonify({'error': 'Token and new password are required'}), 400
    
    token = data['token']
    new_password = data['new_password']
    
    # Validate password strength
    if len(new_password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400
    
    # Check if token exists and is valid
    if token not in password_reset_tokens:
        return jsonify({'error': 'Invalid or expired reset token'}), 400
    
    token_data = password_reset_tokens[token]
    
    # Check if token has expired
    if datetime.utcnow() > token_data['expires_at']:
        del password_reset_tokens[token]
        return jsonify({'error': 'Reset token has expired'}), 400
    
    # Find user and update password
    user = User.query.get(token_data['user_id'])
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Update password
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    
    # Delete used token
    del password_reset_tokens[token]
    
    return jsonify({
        'message': 'Password reset successful. You can now log in with your new password.'
    }), 200

@auth_bp.route('/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """Verify if a reset token is valid"""
    data = request.get_json()
    
    if 'token' not in data:
        return jsonify({'error': 'Token is required'}), 400
    
    token = data['token']
    
    if token not in password_reset_tokens:
        return jsonify({'valid': False, 'error': 'Invalid or expired token'}), 200
    
    token_data = password_reset_tokens[token]
    
    if datetime.utcnow() > token_data['expires_at']:
        del password_reset_tokens[token]
        return jsonify({'valid': False, 'error': 'Token has expired'}), 200
    
    return jsonify({
        'valid': True,
        'email': token_data['email']
    }), 200

