from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User
from src.models.equipment import Equipment
from src.models.booking import Booking
from src.models.payment import Payment
from sqlalchemy import func, and_
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/owner-stats', methods=['GET'])
@jwt_required()
def get_owner_stats():
    """Get comprehensive stats for equipment owner"""
    user_id = int(get_jwt_identity())
    
    # Get all equipment owned by user
    equipment_list = Equipment.query.filter_by(owner_id=user_id).all()
    equipment_ids = [eq.id for eq in equipment_list]
    
    if not equipment_ids:
        return jsonify({
            'total_equipment': 0,
            'total_bookings': 0,
            'total_earnings': 0,
            'pending_earnings': 0,
            'active_rentals': 0,
            'completed_rentals': 0,
            'average_rating': 0,
            'total_reviews': 0,
            'equipment_performance': [],
            'recent_bookings': [],
            'earnings_by_month': []
        }), 200
    
    # Get all bookings for owner's equipment
    all_bookings = Booking.query.filter(Booking.equipment_id.in_(equipment_ids)).all()
    
    # Calculate total earnings (90% of rental cost after platform fee)
    completed_bookings = [b for b in all_bookings if b.status == 'completed']
    total_earnings = sum(b.total_cost * 0.9 for b in completed_bookings)
    
    # Calculate pending earnings (confirmed and active bookings)
    pending_bookings = [b for b in all_bookings if b.status in ['confirmed', 'active']]
    pending_earnings = sum(b.total_cost * 0.9 for b in pending_bookings)
    
    # Count active and completed rentals
    active_rentals = len([b for b in all_bookings if b.status == 'active'])
    completed_rentals = len(completed_bookings)
    
    # Calculate average rating across all equipment
    ratings = [eq.average_rating for eq in equipment_list if eq.average_rating > 0]
    average_rating = sum(ratings) / len(ratings) if ratings else 0
    
    # Count total reviews
    from src.models.review import Review
    total_reviews = Review.query.filter(Review.equipment_id.in_(equipment_ids)).count()
    
    # Equipment performance
    equipment_performance = []
    for eq in equipment_list:
        eq_bookings = [b for b in all_bookings if b.equipment_id == eq.id]
        eq_completed = [b for b in eq_bookings if b.status == 'completed']
        eq_earnings = sum(b.total_cost * 0.9 for b in eq_completed)
        
        equipment_performance.append({
            'equipment_id': eq.id,
            'equipment_name': eq.name,
            'total_bookings': len(eq_bookings),
            'completed_bookings': len(eq_completed),
            'total_earnings': round(eq_earnings, 2),
            'average_rating': eq.average_rating,
            'daily_price': eq.daily_price
        })
    
    # Sort by earnings
    equipment_performance.sort(key=lambda x: x['total_earnings'], reverse=True)
    
    # Recent bookings (last 10)
    recent_bookings = sorted(all_bookings, key=lambda x: x.created_at, reverse=True)[:10]
    recent_bookings_data = []
    for booking in recent_bookings:
        equipment = Equipment.query.get(booking.equipment_id)
        renter = User.query.get(booking.renter_id)
        recent_bookings_data.append({
            'booking_id': booking.id,
            'equipment_name': equipment.name if equipment else 'Unknown',
            'renter_name': f"{renter.first_name} {renter.last_name}" if renter else 'Unknown',
            'start_date': booking.start_date.isoformat() if booking.start_date else None,
            'end_date': booking.end_date.isoformat() if booking.end_date else None,
            'total_cost': booking.total_cost,
            'owner_earnings': round(booking.total_cost * 0.9, 2),
            'status': booking.status,
            'created_at': booking.created_at.isoformat() if booking.created_at else None
        })
    
    # Earnings by month (last 12 months)
    earnings_by_month = []
    current_date = datetime.now()
    for i in range(12):
        month_start = (current_date - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_bookings = [
            b for b in completed_bookings 
            if b.created_at and month_start <= b.created_at.replace(tzinfo=None) <= month_end
        ]
        month_earnings = sum(b.total_cost * 0.9 for b in month_bookings)
        
        earnings_by_month.append({
            'month': month_start.strftime('%Y-%m'),
            'month_name': month_start.strftime('%B %Y'),
            'earnings': round(month_earnings, 2),
            'bookings_count': len(month_bookings)
        })
    
    earnings_by_month.reverse()  # Oldest to newest
    
    return jsonify({
        'total_equipment': len(equipment_list),
        'total_bookings': len(all_bookings),
        'total_earnings': round(total_earnings, 2),
        'pending_earnings': round(pending_earnings, 2),
        'active_rentals': active_rentals,
        'completed_rentals': completed_rentals,
        'average_rating': round(average_rating, 1),
        'total_reviews': total_reviews,
        'equipment_performance': equipment_performance,
        'recent_bookings': recent_bookings_data,
        'earnings_by_month': earnings_by_month
    }), 200


@dashboard_bp.route('/dashboard/equipment-bookings', methods=['GET'])
@jwt_required()
def get_equipment_bookings():
    """Get all bookings for owner's equipment"""
    user_id = int(get_jwt_identity())
    
    # Get all equipment owned by user
    equipment_list = Equipment.query.filter_by(owner_id=user_id).all()
    equipment_ids = [eq.id for eq in equipment_list]
    
    if not equipment_ids:
        return jsonify([]), 200
    
    # Get all bookings
    bookings = Booking.query.filter(Booking.equipment_id.in_(equipment_ids)).order_by(Booking.created_at.desc()).all()
    
    bookings_data = []
    for booking in bookings:
        equipment = Equipment.query.get(booking.equipment_id)
        renter = User.query.get(booking.renter_id)
        
        bookings_data.append({
            **booking.to_dict(),
            'equipment_name': equipment.name if equipment else 'Unknown',
            'renter_name': f"{renter.first_name} {renter.last_name}" if renter else 'Unknown',
            'renter_email': renter.email if renter else None,
            'renter_phone': renter.phone if renter else None,
            'owner_earnings': round(booking.total_cost * 0.9, 2)
        })
    
    return jsonify(bookings_data), 200

