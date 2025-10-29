#!/usr/bin/env python3
"""
Database initialization script
Creates all tables and the admin user
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db
from models.user import User
from models.equipment import Equipment
from models.booking import Booking
from models.message import Message

def init_database():
    """Initialize database with tables and admin user"""
    with app.app_context():
        print("Creating database tables...")
        
        # Create all tables
        db.create_all()
        print("✓ Tables created")
        
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@thewildshare.com').first()
        
        if not admin:
            print("Creating admin user...")
            admin = User(
                email='admin@thewildshare.com',
                first_name='Admin',
                last_name='User',
                phone='555-0000',
                user_type='both',
                is_admin=True
            )
            admin.set_password('!!WildShare01!!')
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created (admin@thewildshare.com / !!WildShare01!!)")
        else:
            # Make sure existing admin has is_admin set
            if not admin.is_admin:
                print("Updating existing admin user...")
                admin.is_admin = True
                db.session.commit()
                print("✓ Admin user updated")
            else:
                print("✓ Admin user already exists")
        
        print("\n✅ Database initialization completed!")

if __name__ == '__main__':
    init_database()

