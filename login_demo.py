#!/usr/bin/env python3
"""
Test script to demonstrate Urban Mobility login functionality
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from init_db import initialize_database
from models.user_model import UserModel
from services.auth_service import AuthService

def test_login():
    print("🛴 URBAN MOBILITY - LOGIN TEST")
    print("=" * 50)
    
    # Initialize database
    print("Initializing database...")
    initialize_database()
    
    print("\n✅ Database initialized successfully!")
    print("\nTesting super_admin login...")
    
    # Test authentication directly
    user = UserModel.authenticate_user('super_admin', 'Admin_123?')
    if user:
        print(f"✅ Direct authentication successful!")
        print(f"   Username: {user.username}")
        print(f"   Role: {user.role}")
        print(f"   Name: {user.first_name} {user.last_name}")
    else:
        print("❌ Direct authentication failed!")
    
    print("\n" + "=" * 50)
    print("LOGIN CREDENTIALS FOR TESTING:")
    print("Username: super_admin")
    print("Password: Admin_123?")
    print("=" * 50)
    
    print("\nStarting interactive login...")
    print("(Password will be visible for testing)")
    
    # Test interactive login
    auth = AuthService()
    user = auth.login_user()
    
    if user:
        print(f"\n🎉 Login successful! Welcome, {user.first_name}!")
        auth.logout_user()
    else:
        print("\n❌ Login failed!")

if __name__ == "__main__":
    test_login()
