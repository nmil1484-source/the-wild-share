#!/usr/bin/env python3
"""
Promote user to admin - Standalone script
Can be run directly on Railway or locally with DATABASE_URL
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

def promote_to_admin(email):
    """Promote a user to admin status"""
    
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        return False
    
    # Fix Railway's postgres:// to postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        # Connect to database
        print(f"🔌 Connecting to database...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if user exists
        print(f"🔍 Looking for user: {email}")
        cursor.execute("SELECT id, email, is_admin FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ User not found: {email}")
            cursor.close()
            conn.close()
            return False
        
        print(f"✅ Found user: {user['email']}")
        print(f"   Current admin status: {user['is_admin']}")
        
        if user['is_admin']:
            print(f"ℹ️  User is already an admin!")
            cursor.close()
            conn.close()
            return True
        
        # Promote to admin
        print(f"⬆️  Promoting user to admin...")
        cursor.execute(
            "UPDATE users SET is_admin = TRUE WHERE email = %s",
            (email,)
        )
        conn.commit()
        
        # Verify the change
        cursor.execute("SELECT is_admin FROM users WHERE email = %s", (email,))
        updated_user = cursor.fetchone()
        
        if updated_user['is_admin']:
            print(f"✅ SUCCESS! User {email} is now an admin!")
            cursor.close()
            conn.close()
            return True
        else:
            print(f"❌ Failed to promote user")
            cursor.close()
            conn.close()
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    # Email to promote
    EMAIL_TO_PROMOTE = "nmil1484@gmail.com"
    
    print("=" * 60)
    print("🔐 The Wild Share - Admin Promotion Script")
    print("=" * 60)
    print(f"Target email: {EMAIL_TO_PROMOTE}")
    print()
    
    success = promote_to_admin(EMAIL_TO_PROMOTE)
    
    print()
    print("=" * 60)
    if success:
        print("✅ Admin promotion completed successfully!")
        print(f"   {EMAIL_TO_PROMOTE} now has admin access")
        print()
        print("🎯 Next steps:")
        print("   1. Log out and log back in to refresh your session")
        print("   2. Navigate to the admin dashboard")
        print("   3. Verify you can see admin features")
    else:
        print("❌ Admin promotion failed")
        print("   Please check the error messages above")
    print("=" * 60)

