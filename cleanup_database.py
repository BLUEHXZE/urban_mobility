#!/usr/bin/env python3
"""
Database cleanup utility - removes duplicate users (by username)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db.dbconn import db
from security import encrypt_data, decrypt_data

def cleanup_duplicate_users():
    """Remove duplicate users by username, keeping only the first occurrence of each username"""
    
    print("Checking for duplicate users by username...")
    
    # Get all users (id, username, role)
    query = "SELECT id, username, role FROM users ORDER BY id ASC"
    results = db.execute_query(query)
    
    seen_usernames = set()
    duplicates = []
    
    for row in results:
        user_id = row[0]
        enc_username = row[1]
        
        try:
            username = decrypt_data(enc_username)
        except Exception:
            username = enc_username  # fallback if decryption fails
        
        if username in seen_usernames:
            duplicates.append(user_id)
        else:
            seen_usernames.add(username)
    
    if not duplicates:
        print("✅ No duplicate users found.")
        return
    
    print(f"⚠️  Found {len(duplicates)} duplicate user(s) - cleaning up...")
    
    for dup_id in duplicates:
        print(f"Deleting duplicate user with ID: {dup_id}")
        
        delete_query = "DELETE FROM users WHERE id = ?"
        db.execute_non_query(delete_query, (dup_id,))
    
    print("✅ Duplicate user cleanup complete!")
    # Reset AUTOINCREMENT sequence if only one user remains
    remaining_query = "SELECT COUNT(*) FROM users"
    count = db.execute_scalar(remaining_query)
    print(f"Users remaining: {count}")
    if count == 1:
        print("Resetting AUTOINCREMENT sequence for users table to 1...")
        db.execute_non_query("UPDATE sqlite_sequence SET seq = 1 WHERE name = 'users'")
        print("Sequence reset. Next user will have id=2.")

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
    
    # Show current state
    list_all_users()
    
    # Clean up all duplicate users
    cleanup_duplicate_users()
    
    # Show final state
    print("\n--- After Cleanup ---")
    list_all_users()
