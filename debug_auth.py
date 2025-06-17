#!/usr/bin/env python3
"""
Debug authentication test
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from init_db import initialize_database
from models.user_model import UserModel

def test_auth():
    print("Testing authentication...")
    
    # Initialize database
    initialize_database()
    
    # Test super_admin authentication
    print("Testing super_admin login...")
    try:
        user = UserModel.authenticate_user('super_admin', 'Admin_123?')
        if user:
            print(f"✅ Success! Logged in as: {user.username}, Role: {user.role}")
            print(f"Name: {user.first_name} {user.last_name}")
        else:
            print("❌ Authentication failed")
    except Exception as e:
        print(f"❌ Exception during authentication: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auth()
