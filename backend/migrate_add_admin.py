#!/usr/bin/env python3
"""
Migration script to add is_admin and is_banned columns to users table
Run this once to update the production database schema
"""
import os
import sys
from sqlalchemy import create_engine, text

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("ERROR: DATABASE_URL environment variable not set")
    sys.exit(1)

# Create engine
engine = create_engine(DATABASE_URL)

try:
    with engine.connect() as conn:
        # Check if is_admin column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='is_admin'
        """))
        
        if result.fetchone() is None:
            print("Adding is_admin column to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("✓ Added is_admin column")
        else:
            print("✓ is_admin column already exists")
        
        # Check if is_banned column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='is_banned'
        """))
        
        if result.fetchone() is None:
            print("Adding is_banned column to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT FALSE"))
            conn.commit()
            print("✓ Added is_banned column")
        else:
            print("✓ is_banned column already exists")
        
        # Check if ban_reason column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='ban_reason'
        """))
        
        if result.fetchone() is None:
            print("Adding ban_reason column to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN ban_reason TEXT"))
            conn.commit()
            print("✓ Added ban_reason column")
        else:
            print("✓ ban_reason column already exists")
        
        # Set admin@thewildshare.com as admin
        print("Setting admin@thewildshare.com as admin...")
        result = conn.execute(text("""
            UPDATE users 
            SET is_admin = TRUE 
            WHERE email = 'admin@thewildshare.com'
        """))
        conn.commit()
        print(f"✓ Updated {result.rowcount} user(s)")
        
    print("\n✅ Migration completed successfully!")
    
except Exception as e:
    print(f"❌ Migration failed: {e}")
    sys.exit(1)

