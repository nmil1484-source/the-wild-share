#!/usr/bin/env python3
"""
Script to update backend CORS configuration to allow Vercel domain
Usage: python3 update_cors_for_vercel.py <vercel_url>
Example: python3 update_cors_for_vercel.py https://the-wild-share-abc123.vercel.app
"""

import sys
import os

def update_cors(vercel_url):
    """Update main.py to allow CORS from Vercel domain"""
    
    # Remove trailing slash if present
    vercel_url = vercel_url.rstrip('/')
    
    main_py_path = '/home/ubuntu/wild-share-deploy/backend/src/main.py'
    
    # Read current content
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    # Find and replace the CORS line
    old_cors = 'CORS(app, resources={r"/api/*": {"origins": "*"}})'
    new_cors = f'''CORS(app, resources={{
    r"/api/*": {{
        "origins": [
            "{vercel_url}",
            "https://thewildshare.com",
            "http://localhost:5173",
            "http://localhost:3000"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }}
}})'''
    
    if old_cors in content:
        updated_content = content.replace(old_cors, new_cors)
        
        # Write back
        with open(main_py_path, 'w') as f:
            f.write(updated_content)
        
        print(f"✅ Updated CORS configuration in {main_py_path}")
        print(f"✅ Added Vercel domain: {vercel_url}")
        print("\nNext steps:")
        print("1. Commit and push changes to GitHub")
        print("2. Railway will automatically redeploy the backend")
        print("3. Wait 2-3 minutes for Railway deployment")
        print("4. Test the site!")
        return True
    else:
        print(f"⚠️  Could not find CORS line to replace")
        print(f"Current CORS configuration may have already been updated")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 update_cors_for_vercel.py <vercel_url>")
        print("Example: python3 update_cors_for_vercel.py https://the-wild-share-abc123.vercel.app")
        sys.exit(1)
    
    vercel_url = sys.argv[1]
    
    if not vercel_url.startswith('http'):
        print("Error: URL must start with http:// or https://")
        sys.exit(1)
    
    update_cors(vercel_url)

