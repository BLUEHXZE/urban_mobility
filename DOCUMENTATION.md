# Urban Mobility Backend System

## Overview
This is a secure backend system for Urban Mobility, a shared electric scooter service. The system provides secure admin interface with role-based access control, comprehensive logging, and data encryption.

## Features

### Security Features
- **Encrypted Data Storage**: All sensitive data (usernames, traveller information, logs) is encrypted using Fernet encryption
- **Password Hashing**: Passwords are hashed using bcrypt with salt
- **SQL Injection Protection**: All database queries use parameterized statements
- **Input Validation**: Comprehensive whitelist-based input validation
- **Role-based Access Control**: Three user roles with specific permissions
- **Activity Logging**: All user activities are logged with suspicious activity detection
- **Backup & Restore**: Secure backup system with one-time restore codes

### User Roles
1. **Super Administrator** (hard-coded: username=`super_admin`, password=`Admin_123?`)
   - Full system control
   - Can manage System Administrators
   - Can create/restore backups directly
   - Can generate restore codes for System Administrators

2. **System Administrator**
   - Can manage Service Engineers and Travellers
   - Can manage scooters (full CRUD)
   - Can create backups and restore using codes from Super Admin
   - Can view system logs

3. **Service Engineer**
   - Can manage Travellers (full CRUD)
   - Can update limited scooter information (SoC, location, status, mileage, maintenance)
   - Cannot add/delete scooters

### Data Management
- **Travellers**: Complete customer information with encrypted PII
- **Scooters**: Fleet management with location tracking and maintenance records
- **Users**: Admin user management with encrypted profiles
- **Logs**: Comprehensive activity logging with encryption
- **Backups**: Secure system backup and restore functionality

## Installation & Setup

### Requirements
```
bcrypt==4.0.1
cryptography==41.0.0
```

### Installation
1. Install Python 3.11 or higher
2. Install dependencies: `pip install -r requirements.txt`
3. Run the application: `python um_members.py`

## Usage

### Login
- Username: `super_admin`
- Password: `Admin_123?`

### Main Menu Options
After login, you'll see different menu options based on your role:

#### Super Administrator Menu
- User Management (create/update/delete System Admins and Service Engineers)
- Traveller Management (full CRUD operations)
- Scooter Management (full CRUD operations)
- System Logs (view all activities and suspicious events)
- Backup Management (create backups, generate restore codes)
- Profile Management

#### System Administrator Menu
- User Management (manage Service Engineers only)
- Traveller Management (full CRUD operations)
- Scooter Management (full CRUD operations)
- System Logs (view activities)
- Backup Management (create backups, restore with codes)
- Profile Management

#### Service Engineer Menu
- Traveller Management (full CRUD operations)
- Scooter Management (limited updates only)
- Profile Management

## Security Implementation

### Input Validation
- Whitelisting approach for all inputs
- Format validation (usernames, passwords, emails, phone numbers, etc.)
- SQL injection prevention through parameterized queries
- Null byte protection
- Length and range validation

### Encryption
- Symmetric encryption using Fernet (AES 128)
- Encrypted fields: usernames, names, addresses, emails, phone numbers, logs
- Secure key storage in separate file

### Authentication & Authorization
- bcrypt password hashing with automatic salt generation
- Role-based access control with centralized permission checking
- Session management
- Failed login attempt tracking and suspicious activity detection

### Logging
- All user activities logged with timestamps
- Encrypted log storage
- Suspicious activity flagging
- Automatic detection of brute force attempts

## Database Schema

### Tables
- `users`: Admin user accounts (encrypted)
- `travellers`: Customer information (encrypted PII)
- `scooters`: Fleet management data
- `logs`: Activity logs (encrypted)
- `restore_codes`: One-time backup restore codes

## File Structure
```
urban_mobility/
├── um_members.py          # Main application entry point
├── init_db.py            # Database initialization
├── security.py           # Encryption and hashing utilities
├── requirements.txt      # Python dependencies
├── db/
│   └── dbconn.py         # Database connection utilities
├── models/
│   ├── user_model.py     # User data model and operations
│   ├── traveller_model.py # Traveller data model and operations
│   └── scooter_model.py  # Scooter data model and operations
├── services/
│   ├── auth_service.py   # Authentication and session management
│   ├── log_service.py    # Logging service
│   ├── backup_service.py # Backup and restore functionality
│   ├── scooter_service.py # Scooter management operations
│   ├── traveller_service.py # Traveller management operations
│   └── user_management_service.py # User management operations
├── utils/
│   └── validators.py     # Input validation utilities
└── data/
    ├── urban_mobility.db # SQLite database
    └── encryption.key    # Encryption key (auto-generated)
```

## Testing

### Test Accounts
- **Super Admin**: username=`super_admin`, password=`Admin_123?`

### Sample Test Data
The system includes validation for:
- Dutch postal codes (DDDDXX format)
- Mobile phone numbers (+31-6-xxxxxxxx format)
- Driving license numbers (XXDDDDDDD or XDDDDDDDD format)
- Rotterdam region GPS coordinates
- Email addresses and other standard formats

## Assignment Compliance

This system meets all requirements of the Software Quality assignment:

### Learning Objectives
✅ **LO1**: Applied knowledge of input validation, SQL injection prevention, and cryptography
✅ **LO2**: Understood common coding mistakes and implemented secure practices
✅ **LO3**: Implemented secure communication with database subsystem
✅ **LO4**: Built a secure system against various user input attacks

### Technical Requirements
✅ **Console Interface**: User-friendly console-based interface
✅ **SQLite Database**: Local database storage with encrypted sensitive data
✅ **Role-based Access**: Three user roles with appropriate permissions
✅ **Input Validation**: Comprehensive whitelist-based validation
✅ **SQL Injection Protection**: Parameterized queries throughout
✅ **Encryption**: Sensitive data encrypted with symmetric algorithm
✅ **Password Security**: Hashed passwords, no plaintext storage
✅ **Logging**: Comprehensive encrypted activity logging
✅ **Backup System**: Secure backup and restore with one-time codes

### Security Measures
✅ **Authentication**: Secure login with attempt limiting
✅ **Authorization**: Role-based access control
✅ **Data Protection**: Encryption of sensitive data
✅ **Audit Trail**: Complete activity logging
✅ **Input Sanitization**: Protection against injection attacks
✅ **Error Handling**: Secure error handling without information disclosure

## Development Notes
- Developed using Python 3.11
- Follows secure coding best practices
- Implements defense in depth security model
- Uses industry-standard encryption and hashing libraries
- Comprehensive error handling and input validation
