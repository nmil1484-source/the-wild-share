from .user import db
from datetime import datetime

class IdentityVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stripe_verification_session_id = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, verified, failed, canceled
    verification_type = db.Column(db.String(50), default='document')  # document, id_number
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    # Verification details from Stripe
    document_type = db.Column(db.String(50), nullable=True)  # passport, drivers_license, id_card
    document_country = db.Column(db.String(10), nullable=True)
    verified_name = db.Column(db.String(255), nullable=True)
    verified_dob = db.Column(db.Date, nullable=True)
    
    def __repr__(self):
        return f'<IdentityVerification {self.id} - User {self.user_id} - {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'verification_type': self.verification_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'document_type': self.document_type,
            'document_country': self.document_country
        }

