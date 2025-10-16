from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(20))
    user_type = db.Column(db.String(20), default='renter')  # owner, renter, both
    profile_image_url = db.Column(db.String(255))
    
    # Stripe Connect fields for equipment owners
    stripe_account_id = db.Column(db.String(255))  # Stripe Connect account ID
    stripe_onboarding_complete = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    equipment = db.relationship('Equipment', backref='owner', lazy=True, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='renter', lazy=True, foreign_keys='Booking.renter_id')

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'user_type': self.user_type,
            'profile_image_url': self.profile_image_url,
            'stripe_account_id': self.stripe_account_id,
            'stripe_onboarding_complete': self.stripe_onboarding_complete,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

