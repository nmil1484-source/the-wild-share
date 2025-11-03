#!/usr/bin/env python3
"""
Script to make a user an admin
"""
import os
import sys
from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    sys.exit(1)

# Email to make admin
email = sys.argv[1] if len(sys.argv) > 1 else 'admin2@thewildshare.com'

# Create engine
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Set user as admin
        print(f"Setting {email} as admin...")
        result = conn.execute(text("""
            UPDATE users 
            SET is_admin = TRUE 
            WHERE email = :email
        """), {"email": email})
        conn.commit()
        
        if result.rowcount > 0:
            print(f"✅ Successfully made {email} an admin!")
        else:
            print(f"❌ User {email} not found in database")
            sys.exit(1)
        
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)

