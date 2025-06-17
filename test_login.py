#!/usr/bin/env python3
"""
Simple test to demonstrate working login
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from init_db import initialize_database
from models.user_model import UserModel

def test_login_demo():
    """Demonstrate that login works"""
    print("Urban Mobility Backend System - Login Test")
    print("=" * 50)
    
    # Initialize database
    initialize_database()
    
    # Test super_admin authentication
    print("\nTesting super_admin authentication...")
    print("Username: super_admin")
    print("Password: Admin_123?")
    
    user = UserModel.authenticate_user('super_admin', 'Admin_123?')
    
    if user:
        print(f"✅ SUCCESS! Logged in as: {user.first_name} {user.last_name}")
        print(f"   Role: {user.role}")
        print(f"   Username: {user.username}")
        print("\nThe login system is working correctly!")
        print("You can now run: python um_members.py")
        print("And use the credentials:")
        print("  Username: super_admin")
        print("  Password: Admin_123?")
    else:
        print("❌ FAILED: Authentication did not work")

if __name__ == "__main__":
    test_login_demo()
