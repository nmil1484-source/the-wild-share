from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import db, User
from src.models.equipment import Equipment
from src.models.booking import Booking
from src.models.review import Review

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/bookings/<int:booking_id>/review', methods=['POST'])
@jwt_required()
def create_review(booking_id):
    """Create a review for a completed booking"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['equipment_rating', 'owner_rating']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    # Validate ratings (1-5)
    if not (1 <= data['equipment_rating'] <= 5) or not (1 <= data['owner_rating'] <= 5):
        return jsonify({'error': 'Ratings must be between 1 and 5'}), 400
    
    # Get booking
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Check if user is the renter
    if booking.renter_id != user_id:
        return jsonify({'error': 'Only the renter can review this booking'}), 403
    
    # Check if booking is completed
    if booking.status != 'completed':
        return jsonify({'error': 'Can only review completed bookings'}), 400
    
    # Check if review already exists
    existing_review = Review.query.filter_by(booking_id=booking_id).first()
    if existing_review:
        return jsonify({'error': 'Review already exists for this booking'}), 400
    
    # Get equipment and owner
    equipment = Equipment.query.get(booking.equipment_id)
    
    # Create review
    new_review = Review(
        booking_id=booking_id,
        equipment_id=booking.equipment_id,
        reviewer_id=user_id,
        reviewee_id=equipment.owner_id,
        equipment_rating=data['equipment_rating'],
        owner_rating=data['owner_rating'],
        equipment_review=data.get('equipment_review', ''),
        owner_review=data.get('owner_review', '')
    )
    
    db.session.add(new_review)
    db.session.commit()
    
    # Update equipment average rating
    update_equipment_rating(booking.equipment_id)
    
    # Update owner average rating
    update_owner_rating(equipment.owner_id)
    
    return jsonify({
        'message': 'Review submitted successfully',
        'review': new_review.to_dict()
    }), 201


@reviews_bp.route('/equipment/<int:equipment_id>/reviews', methods=['GET'])
def get_equipment_reviews(equipment_id):
    """Get all reviews for an equipment item"""
    equipment = Equipment.query.get(equipment_id)
    if not equipment:
        return jsonify({'error': 'Equipment not found'}), 404
    
    reviews = Review.query.filter_by(equipment_id=equipment_id).order_by(Review.created_at.desc()).all()
    
    return jsonify({
        'reviews': [review.to_dict() for review in reviews],
        'average_rating': equipment.average_rating,
        'total_reviews': len(reviews)
    }), 200


@reviews_bp.route('/users/<int:user_id>/reviews', methods=['GET'])
def get_user_reviews(user_id):
    """Get all reviews for a user (as owner)"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    reviews = Review.query.filter_by(reviewee_id=user_id).order_by(Review.created_at.desc()).all()
    
    # Calculate average owner rating
    if reviews:
        avg_rating = sum(r.owner_rating for r in reviews) / len(reviews)
    else:
        avg_rating = 0
    
    return jsonify({
        'reviews': [review.to_dict() for review in reviews],
        'average_rating': round(avg_rating, 1),
        'total_reviews': len(reviews)
    }), 200


@reviews_bp.route('/my-reviews', methods=['GET'])
@jwt_required()
def get_my_reviews():
    """Get all reviews written by the current user"""
    user_id = int(get_jwt_identity())
    
    reviews = Review.query.filter_by(reviewer_id=user_id).order_by(Review.created_at.desc()).all()
    
    return jsonify([review.to_dict() for review in reviews]), 200


@reviews_bp.route('/bookings/<int:booking_id>/can-review', methods=['GET'])
@jwt_required()
def can_review_booking(booking_id):
    """Check if user can review a booking"""
    user_id = int(get_jwt_identity())
    
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Check if user is the renter
    if booking.renter_id != user_id:
        return jsonify({'can_review': False, 'reason': 'Not your booking'}), 200
    
    # Check if booking is completed
    if booking.status != 'completed':
        return jsonify({'can_review': False, 'reason': 'Booking not completed'}), 200
    
    # Check if review already exists
    existing_review = Review.query.filter_by(booking_id=booking_id).first()
    if existing_review:
        return jsonify({'can_review': False, 'reason': 'Already reviewed'}), 200
    
    return jsonify({'can_review': True}), 200


def update_equipment_rating(equipment_id):
    """Update the average rating for an equipment item"""
    reviews = Review.query.filter_by(equipment_id=equipment_id).all()
    
    if reviews:
        avg_rating = sum(r.equipment_rating for r in reviews) / len(reviews)
        equipment = Equipment.query.get(equipment_id)
        equipment.average_rating = round(avg_rating, 1)
        db.session.commit()


def update_owner_rating(owner_id):
    """Update the average rating for an owner"""
    reviews = Review.query.filter_by(reviewee_id=owner_id).all()
    
    if reviews:
        avg_rating = sum(r.owner_rating for r in reviews) / len(reviews)
        owner = User.query.get(owner_id)
        # Store in a new field if needed, or just calculate on-the-fly
        db.session.commit()

