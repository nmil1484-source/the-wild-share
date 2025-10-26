from .user import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False, unique=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Renter who left review
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Owner being reviewed
    
    # Ratings (1-5 stars)
    equipment_rating = db.Column(db.Integer, nullable=False)  # Rating for the equipment
    owner_rating = db.Column(db.Integer, nullable=False)  # Rating for the owner
    
    # Review text
    equipment_review = db.Column(db.Text)  # Optional text review for equipment
    owner_review = db.Column(db.Text)  # Optional text review for owner
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    booking = db.relationship('Booking', backref='review')
    equipment = db.relationship('Equipment', backref='reviews')
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviews_given')
    reviewee = db.relationship('User', foreign_keys=[reviewee_id], backref='reviews_received')
    
    def __repr__(self):
        return f'<Review {self.id} for Equipment {self.equipment_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'equipment_id': self.equipment_id,
            'reviewer_id': self.reviewer_id,
            'reviewee_id': self.reviewee_id,
            'equipment_rating': self.equipment_rating,
            'owner_rating': self.owner_rating,
            'equipment_review': self.equipment_review,
            'owner_review': self.owner_review,
            'reviewer_name': f"{self.reviewer.first_name} {self.reviewer.last_name}" if self.reviewer else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

