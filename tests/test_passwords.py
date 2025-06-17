#!/usr/bin/env python3
"""
Test different password formats
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user_model import UserModel

def test_passwords():
    print("Testing different password formats for super_admin...")
    
    passwords_to_test = [
        'Admin_123',
        'Admin_123?',
        'admin_123?',
        'ADMIN_123?'
    ]
    
    for password in passwords_to_test:
        print(f"Testing password: '{password}'")
        user = UserModel.authenticate_user('super_admin', password)
        if user:
            print(f"✅ SUCCESS with password: '{password}'")
        else:
            print(f"❌ FAILED with password: '{password}'")
        print()

if __name__ == "__main__":
    test_passwords()
