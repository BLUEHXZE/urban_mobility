import sqlite3
import os
from datetime import datetime
from security import hash_password, encrypt_data

def initialize_database(db_path="data/urban_mobility.db"):
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('super_admin', 'system_admin', 'service_engineer')),
        first_name TEXT,
        last_name TEXT,
        registration_date TEXT NOT NULL
    );
    """)

    # Create scooters table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scooters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        serial_number TEXT UNIQUE NOT NULL,
        top_speed INTEGER,
        battery_capacity INTEGER,
        soc INTEGER,
        soc_min INTEGER,
        soc_max INTEGER,
        latitude REAL,
        longitude REAL,
        out_of_service BOOLEAN DEFAULT 0,
        mileage INTEGER,
        last_maintenance_date TEXT,
        in_service_date TEXT NOT NULL
    );
    """)

    # Create travellers table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS travellers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        birthday TEXT NOT NULL,
        gender TEXT CHECK(gender IN ('male', 'female')) NOT NULL,
        street_name TEXT,
        house_number TEXT,
        zip_code TEXT CHECK(length(zip_code) = 6),
        city TEXT,
        email TEXT,
        mobile_phone TEXT,
        driving_license_number TEXT UNIQUE,
        registration_date TEXT NOT NULL
    );
    """)

    # Create logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        username TEXT,
        activity_description TEXT NOT NULL,
        additional_info TEXT,
        suspicious BOOLEAN DEFAULT 0
    );
    """)

    # Create restore codes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS restore_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        system_admin_username TEXT NOT NULL,
        backup_filename TEXT NOT NULL,
        used BOOLEAN DEFAULT 0,
        created_at TEXT NOT NULL
    );
    """)

    conn.commit()
      # Insert hard-coded super admin if not exists
    encrypted_username_check = encrypt_data('super_admin')
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (encrypted_username_check,))
    if cursor.fetchone()[0] == 0:
        encrypted_username = encrypt_data('super_admin')
        password_hash = hash_password('Admin_123?')
        encrypted_first_name = encrypt_data('Super')
        encrypted_last_name = encrypt_data('Administrator')
        registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
        INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (encrypted_username, password_hash, 'super_admin', encrypted_first_name, encrypted_last_name, registration_date))
        
        conn.commit()
        print("Super admin account created.")
    else:
        print("Super admin account already exists.")
    
    conn.close()
if __name__ == "__main__":
    initialize_database()
    print("Database created successfully.")
