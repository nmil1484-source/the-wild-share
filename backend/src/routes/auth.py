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
    
    # Debug logging
    user_dict = user.to_dict()
    print(f"DEBUG LOGIN: User {user.email} - is_admin in dict: {user_dict.get('is_admin')}")
    print(f"DEBUG LOGIN: User object is_admin: {user.is_admin}")
    print(f"DEBUG LOGIN: Full user dict: {user_dict}")
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user_dict
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Debug: Force check is_admin attribute
    user_dict = user.to_dict()
    print(f"DEBUG /me: User {user.email} - is_admin in dict: {user_dict.get('is_admin')}")
    print(f"DEBUG /me: User object is_admin attr: {user.is_admin}")
    print(f"DEBUG /me: Dict keys: {list(user_dict.keys())}")
    
    return jsonify(user_dict), 200

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

