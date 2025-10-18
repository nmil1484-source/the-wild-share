from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User
from src.models.equipment import Equipment

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/equipment', methods=['GET'])
def get_all_equipment():
    """Get all available equipment, optionally filtered by category"""
    category = request.args.get('category')
    
    query = Equipment.query
    
    if category and category != 'all':
        query = query.filter_by(category=category)
    
    equipment_list = query.filter_by(is_available=True).all()
    
    return jsonify([item.to_dict() for item in equipment_list]), 200

@equipment_bp.route('/equipment/<int:equipment_id>', methods=['GET'])
def get_equipment(equipment_id):
    """Get a specific equipment item"""
    equipment = Equipment.query.get(equipment_id)
    
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    return jsonify(equipment.to_dict()), 200

@equipment_bp.route('/equipment', methods=['POST'])
@jwt_required()
def create_equipment():
    """Create a new equipment listing (owner only)"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user is an owner
    if user.user_type not in ['owner', 'both']:
        return jsonify({'error': 'Only equipment owners can create listings'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'description', 'category', 'daily_price']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Create new equipment
    new_equipment = Equipment(
        owner_id=user_id,
        name=data['name'],
        description=data['description'],
        category=data['category'],
        daily_price=float(data['daily_price']),
        weekly_price=float(data['weekly_price']) if data.get('weekly_price') else None,
        monthly_price=float(data['monthly_price']) if data.get('monthly_price') else None,
        capacity_spec=data.get('capacity_spec'),
        image_url=data.get('image_url'),
        is_available=data.get('is_available', True)
    )
    
    db.session.add(new_equipment)
    db.session.commit()
    
    return jsonify({
        'message': 'Equipment created successfully',
        'equipment': new_equipment.to_dict()
    }), 201

@equipment_bp.route('/equipment/<int:equipment_id>', methods=['PUT'])
@jwt_required()
def update_equipment(equipment_id):
    """Update an equipment listing (owner only)"""
    user_id = get_jwt_identity()
    equipment = Equipment.query.get(equipment_id)
    
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    # Check if user is the owner
    if equipment.owner_id != user_id:
        return jsonify({'error': 'You can only update your own equipment'}), 403
    
    data = request.get_json()
    
    # Update allowed fields
    if 'name' in data:
        equipment.name = data['name']
    if 'description' in data:
        equipment.description = data['description']
    if 'category' in data:
        equipment.category = data['category']
    if 'daily_price' in data:
        equipment.daily_price = float(data['daily_price'])
    if 'weekly_price' in data:
        equipment.weekly_price = float(data['weekly_price']) if data['weekly_price'] else None
    if 'monthly_price' in data:
        equipment.monthly_price = float(data['monthly_price']) if data['monthly_price'] else None
    if 'capacity_spec' in data:
        equipment.capacity_spec = data['capacity_spec']
    if 'image_url' in data:
        equipment.image_url = data['image_url']
    if 'is_available' in data:
        equipment.is_available = data['is_available']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Equipment updated successfully',
        'equipment': equipment.to_dict()
    }), 200

@equipment_bp.route('/equipment/<int:equipment_id>', methods=['DELETE'])
@jwt_required()
def delete_equipment(equipment_id):
    """Delete an equipment listing (owner only)"""
    user_id = get_jwt_identity()
    equipment = Equipment.query.get(equipment_id)
    
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    # Check if user is the owner
    if equipment.owner_id != user_id:
        return jsonify({'error': 'You can only delete your own equipment'}), 403
    
    db.session.delete(equipment)
    db.session.commit()
    
    return jsonify({'message': 'Equipment deleted successfully'}), 200

@equipment_bp.route('/my-equipment', methods=['GET'])
@jwt_required()
def get_my_equipment():
    """Get all equipment owned by the current user"""
    user_id = get_jwt_identity()
    equipment_list = Equipment.query.filter_by(owner_id=user_id).all()
    
    return jsonify([item.to_dict() for item in equipment_list]), 200

