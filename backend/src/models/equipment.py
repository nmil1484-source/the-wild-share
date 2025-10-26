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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='equipment', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Equipment {self.name}>'

    def to_dict(self):
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
            'owner': self.owner.to_dict() if self.owner else None
        }

