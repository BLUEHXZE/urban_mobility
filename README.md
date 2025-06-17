# Urban Mobility Backend System

A secure backend administration system for Urban Mobility's electric scooter sharing service.

## Features

### Security Features
- **Input Validation**: Comprehensive whitelisting-based validation for all user inputs
- **SQL Injection Protection**: Parameterized queries throughout the application
- **Encryption**: Sensitive data encrypted in database using Fernet symmetric encryption
- **Password Security**: Bcrypt hashing for all passwords, no plaintext storage
- **Logging**: All activities logged with suspicious activity detection
- **Role-based Access Control**: Three user roles with specific permissions

### User Roles
1. **Super Administrator** (Hard-coded: `super_admin` / `Admin_123?`)
   - Full system access
   - Can create/manage System Administrators
   - Direct backup restore capability
   - Generate restore codes for System Administrators

2. **System Administrator**
   - Manage Service Engineers
   - Full scooter and traveller management
   - System backup and restore (with codes)
   - View system logs

3. **Service Engineer**
   - Update scooter information (limited fields)
   - View scooter details
   - Search scooters

### Data Management
- **Travellers**: Personal information with encrypted sensitive data
- **Scooters**: Fleet management with GPS tracking and maintenance records
- **System Logs**: Encrypted activity logs with suspicious activity flagging
- **Backup/Restore**: Secure backup system with one-time restore codes

## Installation

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python um_members.py
   ```

## Security Implementation

### Input Validation
- Whitelisting approach for all inputs
- Null-byte protection
- Length and format validation
- Regular expression patterns for structured data

### Encryption
- AES encryption via Fernet for sensitive database fields
- Bcrypt for password hashing
- Secure key storage in separate file

### Logging
- All user activities logged
- Suspicious activity detection (multiple failed logins, etc.)
- Encrypted log storage

### Access Control
- Role-based permissions
- Session management
- Audit trails for all operations

## Database Schema

- **users**: System users with encrypted names
- **travellers**: Customer data with encrypted PII
- **scooters**: Fleet information
- **logs**: Encrypted activity logs
- **restore_codes**: One-time backup restore codes

## Assignment Compliance

This system meets all requirements for the Software Quality final assignment:
- ✅ Secure authentication and authorization
- ✅ Comprehensive input validation
- ✅ SQL injection protection
- ✅ Encrypted sensitive data storage
- ✅ Activity logging and monitoring
- ✅ Backup and restore functionality
- ✅ Role-based access control
- ✅ Console-based user interface

## Usage

1. Start the application
2. Login with credentials (Super Admin: `super_admin` / `Admin_123?`)
3. Navigate through menus based on your role
4. All activities are automatically logged

## File Structure

```
urban_mobility/
├── um_members.py          # Main application entry point
├── init_db.py            # Database initialization
├── security.py           # Encryption and hashing utilities
├── requirements.txt      # Python dependencies
├── data/                 # Database and key storage
├── db/                   # Database connection utilities
├── models/               # Data models
├── services/             # Business logic services
├── utils/                # Validation utilities
└── backups/              # System backups
```