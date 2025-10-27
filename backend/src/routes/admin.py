from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..models.user import User
from ..models.equipment import Equipment
from ..models.booking import Booking
from ..models.message import Message
from ..models.review import Review
from ..models.identity_verification import IdentityVerification
from ..models.booking import db

admin_bp = Blueprint('admin', __name__)

# Admin secret key - change this to something secure!
ADMIN_SECRET = "wildshare_admin_reset_2024"

@admin_bp.route('/api/admin/reset-database', methods=['POST'])
def reset_database():
    """
    DANGER: This endpoint deletes ALL data from the database!
    Requires admin secret key for security.
    """
    # Get the secret from request
    data = request.get_json()
    secret = data.get('secret', '')
    
    # Verify admin secret
    if secret != ADMIN_SECRET:
        return jsonify({'error': 'Unauthorized - Invalid admin secret'}), 403
    
    try:
        # Delete all data in correct order (to avoid foreign key constraints)
        deleted_counts = {}
        
        # 1. Delete reviews (depends on bookings and users)
        review_count = Review.query.delete()
        deleted_counts['reviews'] = review_count
        
        # 2. Delete messages (depends on users and equipment)
        message_count = Message.query.delete()
        deleted_counts['messages'] = message_count
        
        # 3. Delete bookings (depends on users and equipment)
        booking_count = Booking.query.delete()
        deleted_counts['bookings'] = booking_count
        
        # 4. Delete equipment (depends on users)
        equipment_count = Equipment.query.delete()
        deleted_counts['equipment'] = equipment_count
        
        # 5. Delete identity verifications (depends on users)
        verification_count = IdentityVerification.query.delete()
        deleted_counts['identity_verifications'] = verification_count
        
        # 6. Delete users (no dependencies)
        user_count = User.query.delete()
        deleted_counts['users'] = user_count
        
        # Commit all deletions
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Database reset successfully!',
            'deleted': deleted_counts,
            'total_deleted': sum(deleted_counts.values())
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': f'Failed to reset database: {str(e)}'
        }), 500

@admin_bp.route('/api/admin/stats', methods=['GET'])
def get_stats():
    """
    Get current database statistics
    """
    try:
        stats = {
            'users': User.query.count(),
            'equipment': Equipment.query.count(),
            'bookings': Booking.query.count(),
            'messages': Message.query.count(),
            'reviews': Review.query.count(),
            'identity_verifications': IdentityVerification.query.count()
        }
        
        return jsonify({
            'success': True,
            'stats': stats,
            'total_records': sum(stats.values())
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Failed to get stats: {str(e)}'
        }), 500

