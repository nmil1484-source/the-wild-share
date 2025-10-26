from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from src.models.booking import Booking

availability_bp = Blueprint('availability', __name__)

@availability_bp.route('/equipment/<int:equipment_id>/blocked-dates', methods=['GET'])
def get_blocked_dates(equipment_id):
    """Get all blocked dates for an equipment item"""
    # Get all confirmed, active, or pending bookings
    bookings = Booking.query.filter(
        Booking.equipment_id == equipment_id,
        Booking.status.in_(['pending', 'confirmed', 'active'])
    ).all()
    
    # Generate list of blocked dates
    blocked_dates = []
    for booking in bookings:
        current_date = booking.start_date
        while current_date <= booking.end_date:
            blocked_dates.append(current_date.isoformat())
            current_date += timedelta(days=1)
    
    return jsonify({
        'equipment_id': equipment_id,
        'blocked_dates': blocked_dates
    }), 200


@availability_bp.route('/equipment/<int:equipment_id>/check-availability', methods=['POST'])
def check_availability(equipment_id):
    """Check if equipment is available for given dates"""
    data = request.get_json()
    
    if 'start_date' not in data or 'end_date' not in data:
        return jsonify({'error': 'start_date and end_date are required'}), 400
    
    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    # Check for conflicting bookings
    conflicting_bookings = Booking.query.filter(
        Booking.equipment_id == equipment_id,
        Booking.status.in_(['pending', 'confirmed', 'active']),
        Booking.start_date <= end_date,
        Booking.end_date >= start_date
    ).first()
    
    is_available = conflicting_bookings is None
    
    return jsonify({
        'equipment_id': equipment_id,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'is_available': is_available,
        'message': 'Available' if is_available else 'Equipment is already booked for these dates'
    }), 200

