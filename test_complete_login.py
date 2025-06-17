#!/usr/bin/env python3
"""
Quick test of the complete login process
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from init_db import initialize_database
from models.user_model import UserModel

def test_complete_login():
    print("Testing complete login process...")
    
    # Initialize database
    initialize_database()
    
    # Test super_admin authentication with correct password
    print("Testing super_admin login with correct password...")
    try:
        user = UserModel.authenticate_user('super_admin', 'Admin_123?')
        if user:
            print(f"✅ Success! Logged in as: {user.username}")
            print(f"Role: {user.role}")
            print(f"Name: {user.first_name} {user.last_name}")
            print(f"Registration: {user.registration_date}")
        else:
            print("❌ Authentication failed")
    except Exception as e:
        print(f"❌ Exception during authentication: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_complete_login()
