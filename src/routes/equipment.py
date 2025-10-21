from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User
from src.models.equipment import Equipment
from sqlalchemy import or_, and_, func

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/equipment', methods=['GET'])
def get_all_equipment():
    """
    Get all available equipment with advanced filtering and search
    
    Query Parameters:
    - search: Search in name, description, capacity_spec
    - category: Filter by category
    - min_price: Minimum daily price
    - max_price: Maximum daily price
    - city: Filter by owner's city
    - state: Filter by owner's state
    - sort_by: price_asc, price_desc, newest, oldest
    - limit: Number of results (default 50)
    - offset: Pagination offset (default 0)
    """
    
    # Start with base query for available equipment
    query = Equipment.query.filter_by(is_available=True)
    
    # Search functionality
    search_term = request.args.get('search', '').strip()
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                Equipment.name.ilike(search_pattern),
                Equipment.description.ilike(search_pattern),
                Equipment.capacity_spec.ilike(search_pattern),
                Equipment.category.ilike(search_pattern)
            )
        )
    
    # Category filter
    category = request.args.get('category')
    if category and category != 'all':
        query = query.filter_by(category=category)
    
    # Price filters
    min_price = request.args.get('min_price', type=float)
    if min_price is not None:
        query = query.filter(Equipment.daily_price >= min_price)
    
    max_price = request.args.get('max_price', type=float)
    if max_price is not None:
        query = query.filter(Equipment.daily_price <= max_price)
    
    # Location filters (requires joining with User table)
    city = request.args.get('city')
    state = request.args.get('state')
    
    if city or state:
        query = query.join(User, Equipment.owner_id == User.id)
        if city:
            query = query.filter(User.city.ilike(f"%{city}%"))
        if state:
            query = query.filter(User.state.ilike(f"%{state}%"))
    
    # Sorting
    sort_by = request.args.get('sort_by', 'newest')
    if sort_by == 'price_asc':
        query = query.order_by(Equipment.daily_price.asc())
    elif sort_by == 'price_desc':
        query = query.order_by(Equipment.daily_price.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Equipment.created_at.asc())
    else:  # newest (default)
        query = query.order_by(Equipment.created_at.desc())
    
    # Pagination
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    # Get total count before pagination
    total_count = query.count()
    
    # Apply pagination
    equipment_list = query.limit(limit).offset(offset).all()
    
    # Return results with metadata
    return jsonify({
        'equipment': [item.to_dict() for item in equipment_list],
        'total_count': total_count,
        'limit': limit,
        'offset': offset,
        'has_more': (offset + limit) < total_count
    }), 200

@equipment_bp.route('/equipment/search', methods=['GET'])
def search_equipment():
    """
    Dedicated search endpoint with autocomplete support
    Returns matching equipment names and categories
    """
    search_term = request.args.get('q', '').strip()
    
    if not search_term or len(search_term) < 2:
        return jsonify({'suggestions': []}), 200
    
    search_pattern = f"%{search_term}%"
    
    # Search in equipment names
    equipment_matches = Equipment.query.filter(
        Equipment.is_available == True,
        Equipment.name.ilike(search_pattern)
    ).limit(10).all()
    
    suggestions = []
    for item in equipment_matches:
        suggestions.append({
            'type': 'equipment',
            'id': item.id,
            'name': item.name,
            'category': item.category,
            'price': item.daily_price,
            'image_url': item.image_url
        })
    
    return jsonify({'suggestions': suggestions}), 200

@equipment_bp.route('/equipment/filters', methods=['GET'])
def get_filter_options():
    """
    Get available filter options (categories, price range, locations)
    Useful for building filter UI
    """
    
    # Get all unique categories
    categories = db.session.query(Equipment.category).filter(
        Equipment.is_available == True
    ).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    # Get price range
    price_stats = db.session.query(
        func.min(Equipment.daily_price).label('min_price'),
        func.max(Equipment.daily_price).label('max_price'),
        func.avg(Equipment.daily_price).label('avg_price')
    ).filter(Equipment.is_available == True).first()
    
    # Get available locations (cities and states)
    locations = db.session.query(
        User.city, User.state
    ).join(Equipment, Equipment.owner_id == User.id).filter(
        Equipment.is_available == True,
        User.city.isnot(None),
        User.state.isnot(None)
    ).distinct().all()
    
    cities = list(set([loc.city for loc in locations if loc.city]))
    states = list(set([loc.state for loc in locations if loc.state]))
    
    return jsonify({
        'categories': sorted(categories),
        'price_range': {
            'min': float(price_stats.min_price) if price_stats.min_price else 0,
            'max': float(price_stats.max_price) if price_stats.max_price else 1000,
            'avg': float(price_stats.avg_price) if price_stats.avg_price else 100
        },
        'locations': {
            'cities': sorted(cities),
            'states': sorted(states)
        }
    }), 200

@equipment_bp.route('/equipment/<int:equipment_id>', methods=['GET'])
def get_equipment(equipment_id):
    """Get a specific equipment item with owner details"""
    equipment = Equipment.query.get(equipment_id)
    
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    # Get equipment data
    equipment_data = equipment.to_dict()
    
    # Add owner information
    owner = User.query.get(equipment.owner_id)
    if owner:
        equipment_data['owner'] = {
            'id': owner.id,
            'name': f"{owner.first_name} {owner.last_name}",
            'profile_image_url': owner.profile_image_url,
            'bio': owner.bio,
            'city': owner.city,
            'state': owner.state,
            'phone': owner.phone if owner.phone else None,
            'member_since': owner.created_at.isoformat() if owner.created_at else None
        }
    
    return jsonify(equipment_data), 200

@equipment_bp.route('/equipment', methods=['POST'])
@jwt_required()
def create_equipment():
    """Create a new equipment listing (owner only)"""
    user_id = int(get_jwt_identity())
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
        location=data.get('location'),
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
    user_id = int(get_jwt_identity())
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
    if 'location' in data:
        equipment.location = data['location']
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
    user_id = int(get_jwt_identity())
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
    user_id = int(get_jwt_identity())
    equipment_list = Equipment.query.filter_by(owner_id=user_id).all()
    
    return jsonify([item.to_dict() for item in equipment_list]), 200

