#!/usr/bin/env python3
"""
Database cleanup utility - removes duplicate super_admin accounts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from init_db import initialize_database
from db.dbconn import db
from security import encrypt_data, decrypt_data

def cleanup_duplicate_super_admins():
    """Remove duplicate super_admin accounts, keeping only the first one"""
    
    print("Checking for duplicate super_admin accounts...")
    
    # Find all super_admin accounts
    query = "SELECT id, username, role FROM users WHERE role = 'super_admin'"
    results = db.execute_query(query)
    
    if len(results) <= 1:
        print(f"✅ Found {len(results)} super_admin account(s) - no cleanup needed.")
        return
    
    print(f"⚠️  Found {len(results)} super_admin accounts - cleaning up duplicates...")
    
    # Keep the first one, delete the rest
    keep_id = results[0][0]
    
    for result in results[1:]:
        duplicate_id = result[0]
        print(f"Deleting duplicate super_admin with ID: {duplicate_id}")
        
        delete_query = "DELETE FROM users WHERE id = ?"
        db.execute_non_query(delete_query, (duplicate_id,))
    
    print("✅ Cleanup complete!")
    
    # Verify cleanup
    remaining_query = "SELECT COUNT(*) FROM users WHERE role = 'super_admin'"
    count = db.execute_scalar(remaining_query)
    print(f"Super_admin accounts remaining: {count}")

def list_all_users():
    """List all users in the database for verification"""
    print("\n--- All Users in Database ---")
    
    query = "SELECT id, username, role, first_name, last_name FROM users"
    results = db.execute_query(query)
    
    if not results:
        print("No users found.")
        return
    
    print(f"{'ID':<5} {'Username':<15} {'Role':<15} {'Name':<25}")
    print("-" * 65)
    
    for result in results:
        try:
            username = decrypt_data(result[1])
            first_name = decrypt_data(result[3])
            last_name = decrypt_data(result[4])
            name = f"{first_name} {last_name}"
            
            print(f"{result[0]:<5} {username:<15} {result[2]:<15} {name:<25}")
        except Exception as e:
            print(f"{result[0]:<5} {'[encrypted]':<15} {result[2]:<15} {'[encrypted]':<25}")

if __name__ == "__main__":
    print("Urban Mobility Database Cleanup Utility")
    print("=" * 40)
    
    # Don't initialize database - just work with existing one
    # initialize_database()
    
    # Show current state
    list_all_users()
    
    # Clean up duplicates
    cleanup_duplicate_super_admins()
    
    # Show final state
    print("\n--- After Cleanup ---")
    list_all_users()
