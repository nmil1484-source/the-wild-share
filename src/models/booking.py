from src.models.user import db
from datetime import datetime

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False)
    renter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_days = db.Column(db.Integer, nullable=False)
    daily_rate = db.Column(db.Float, nullable=False)
    total_cost = db.Column(db.Float, nullable=False)
    deposit_amount = db.Column(db.Float, nullable=False)  # 50% of total_cost
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, active, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('Payment', backref='booking', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Booking {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'equipment_id': self.equipment_id,
            'renter_id': self.renter_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'total_days': self.total_days,
            'daily_rate': self.daily_rate,
            'total_cost': self.total_cost,
            'deposit_amount': self.deposit_amount,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'equipment': self.equipment.to_dict() if self.equipment else None,
            'renter': self.renter.to_dict() if self.renter else None
        }

