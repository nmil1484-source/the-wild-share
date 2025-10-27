from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models.user import db, User
from src.models.equipment import Equipment
from src.models.booking import Booking
from src.models.message import Message
from src.models.payment import Payment

admin_mod_bp = Blueprint('admin_moderation', __name__)

def admin_required(fn):
    """Decorator to require admin privileges"""
    @jwt_required()
    def wrapper(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        
        return fn(*args, **kwargs)
    
    wrapper.__name__ = fn.__name__
    return wrapper

# ==================== DASHBOARD STATS ====================

@admin_mod_bp.route('/admin/dashboard/stats', methods=['GET'])
@admin_required
def get_dashboard_stats():
    """Get overall platform statistics for admin dashboard"""
    try:
        total_users = User.query.count()
        total_equipment = Equipment.query.count()
        total_bookings = Booking.query.count()
        pending_equipment = Equipment.query.filter_by(approval_status='pending').count()
        approved_equipment = Equipment.query.filter_by(approval_status='approved').count()
        banned_users = User.query.filter_by(is_banned=True).count()
        
        # Recent activity
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_equipment = Equipment.query.order_by(Equipment.created_at.desc()).limit(5).all()
        recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'total_equipment': total_equipment,
                'total_bookings': total_bookings,
                'pending_equipment': pending_equipment,
                'approved_equipment': approved_equipment,
                'banned_users': banned_users
            },
            'recent_activity': {
                'users': [u.to_dict() for u in recent_users],
                'equipment': [e.to_dict() for e in recent_equipment],
                'bookings': [b.to_dict() for b in recent_bookings]
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== USER MANAGEMENT ====================

@admin_mod_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users with optional filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        is_banned = request.args.get('is_banned', None)
        
        query = User.query
        
        # Apply filters
        if search:
            query = query.filter(
                (User.email.ilike(f'%{search}%')) |
                (User.first_name.ilike(f'%{search}%')) |
                (User.last_name.ilike(f'%{search}%'))
            )
        
        if is_banned is not None:
            query = query.filter_by(is_banned=(is_banned == 'true'))
        
        # Paginate
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'users': [u.to_dict() for u in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_mod_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user_details():
    """Get detailed information about a specific user"""
    try:
        user_id = request.view_args['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's equipment and bookings
        equipment = Equipment.query.filter_by(owner_id=user_id).all()
        bookings = Booking.query.filter_by(renter_id=user_id).all()
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'equipment': [e.to_dict() for e in equipment],
            'bookings': [b.to_dict() for b in bookings]
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_mod_bp.route('/admin/users/<int:user_id>/ban', methods=['POST'])
@admin_required
def ban_user():
    """Ban a user"""
    try:
        user_id = request.view_args['user_id']
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.is_admin:
            return jsonify({'error': 'Cannot ban admin users'}), 403
        
        user.is_banned = True
        user.ban_reason = data.get('reason', 'No reason provided')
        user.banned_at = datetime.utcnow()
        user.banned_by = current_user_id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User {user.email} has been banned'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_mod_bp.route('/admin/users/<int:user_id>/unban', methods=['POST'])
@admin_required
def unban_user():
    """Unban a user"""
    try:
        user_id = request.view_args['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_banned = False
        user.ban_reason = None
        user.banned_at = None
        user.banned_by = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User {user.email} has been unbanned'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_mod_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user():
    """Delete a user and all their data"""
    try:
        user_id = request.view_args['user_id']
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user.is_admin:
            return jsonify({'error': 'Cannot delete admin users'}), 403
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User {user.email} has been deleted'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== EQUIPMENT MODERATION ====================

@admin_mod_bp.route('/admin/equipment', methods=['GET'])
@admin_required
def get_all_equipment():
    """Get all equipment with optional filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', None)  # pending, approved, rejected
        search = request.args.get('search', '')
        
        query = Equipment.query
        
        # Apply filters
        if status:
            query = query.filter_by(approval_status=status)
        
        if search:
            query = query.filter(
                (Equipment.name.ilike(f'%{search}%')) |
                (Equipment.description.ilike(f'%{search}%'))
            )
        
        # Paginate
        pagination = query.order_by(Equipment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'equipment': [e.to_dict() for e in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_mod_bp.route('/admin/equipment/<int:equipment_id>/approve', methods=['POST'])
@admin_required
def approve_equipment():
    """Approve an equipment listing"""
    try:
        equipment_id = request.view_args['equipment_id']
        current_user_id = get_jwt_identity()
        
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            return jsonify({'error': 'Equipment not found'}), 404
        
        equipment.approval_status = 'approved'
        equipment.approved_by = current_user_id
        equipment.approved_at = datetime.utcnow()
        equipment.rejection_reason = None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Equipment "{equipment.name}" has been approved'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_mod_bp.route('/admin/equipment/<int:equipment_id>/reject', methods=['POST'])
@admin_required
def reject_equipment():
    """Reject an equipment listing"""
    try:
        equipment_id = request.view_args['equipment_id']
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            return jsonify({'error': 'Equipment not found'}), 404
        
        equipment.approval_status = 'rejected'
        equipment.approved_by = current_user_id
        equipment.approved_at = datetime.utcnow()
        equipment.rejection_reason = data.get('reason', 'No reason provided')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Equipment "{equipment.name}" has been rejected'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_mod_bp.route('/admin/equipment/<int:equipment_id>', methods=['DELETE'])
@admin_required
def delete_equipment():
    """Delete an equipment listing"""
    try:
        equipment_id = request.view_args['equipment_id']
        equipment = Equipment.query.get(equipment_id)
        
        if not equipment:
            return jsonify({'error': 'Equipment not found'}), 404
        
        db.session.delete(equipment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Equipment "{equipment.name}" has been deleted'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==================== BOOKING MANAGEMENT ====================

@admin_mod_bp.route('/admin/bookings', methods=['GET'])
@admin_required
def get_all_bookings():
    """Get all bookings"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        pagination = Booking.query.order_by(Booking.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'bookings': [b.to_dict() for b in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

