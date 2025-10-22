from src.models.user import db
from datetime import datetime

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)  # rental, deposit, refund
    amount = db.Column(db.Float, nullable=False)
    stripe_payment_id = db.Column(db.String(255))
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Payment {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'booking_id': self.booking_id,
            'payment_type': self.payment_type,
            'amount': self.amount,
            'stripe_payment_id': self.stripe_payment_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

