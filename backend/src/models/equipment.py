from src.models.user import db
from datetime import datetime
import json

class Equipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # bikes, water, camping, power, gear
    daily_price = db.Column(db.Float, nullable=False)
    weekly_price = db.Column(db.Float, nullable=True)
    monthly_price = db.Column(db.Float, nullable=True)
    capacity_spec = db.Column(db.String(50))
    image_url = db.Column(db.String(255))  # Legacy single image
    image_urls = db.Column(db.Text)  # JSON array of multiple image URLs
    location = db.Column(db.String(255))  # City, State or full address
    is_available = db.Column(db.Boolean, default=True)
    average_rating = db.Column(db.Float, default=0.0)  # Average rating from reviews
    
    # Moderation fields
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='equipment', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Equipment {self.name}>'

    def to_dict(self, include_full_owner=False):
        # Public owner info (safe to show on listings)
        owner_info = None
        if self.owner:
            if include_full_owner:
                owner_info = self.owner.to_dict()
            else:
                # Only show safe public info
                first_name = self.owner.first_name or 'User'
                last_initial = self.owner.last_name[0] + '.' if self.owner.last_name else ''
                owner_info = {
                    'id': self.owner.id,
                    'name': f"{first_name} {last_initial}",
                    'profile_image_url': self.owner.profile_image_url,
                    'trust_level': self.owner.trust_level,
                    'is_identity_verified': self.owner.is_identity_verified,
                    'member_since': self.owner.created_at.isoformat() if self.owner.created_at else None
                }
        
        return {
            'id': self.id,
            'owner_id': self.owner_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'daily_price': self.daily_price,
            'weekly_price': self.weekly_price,
            'monthly_price': self.monthly_price,
            'capacity_spec': self.capacity_spec,
            'image_url': self.image_url,
            'image_urls': json.loads(self.image_urls) if self.image_urls else ([self.image_url] if self.image_url else []),
            'location': self.location,
            'is_available': self.is_available,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'owner': owner_info
        }

