# Urban Mobility Backend System - Testing Guide

## Quick Test Instructions

### 1. System Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python um_members.py
```

### 2. Login Test
**Credentials:**
- Username: `super_admin`
- Password: `Admin_123?` (note the question mark!)

### 3. Feature Testing

#### User Management (Super Admin only)
1. Login as super_admin
2. Go to "User Management"
3. Create a new System Administrator
4. Create a new Service Engineer
5. Test login with the new accounts

#### Traveller Management
1. Add a new traveller with sample data:
   - First Name: John
   - Last Name: Doe  
   - Birthday: 1990-01-15
   - Gender: male
   - Street: Coolsingel
   - House Number: 123
   - Zip Code: 3011AD
   - City: Rotterdam
   - Email: john.doe@example.com
   - Phone: 12345678 (system adds +31-6- prefix)
   - License: AB1234567

2. Search for the traveller
3. Update traveller information
4. View traveller details

#### Scooter Management
1. Add a new scooter:
   - Brand: Segway
   - Model: Ninebot E45
   - Serial: ABC1234567890
   - Top Speed: 25
   - Battery: 2500
   - Current SoC: 80
   - Min SoC: 20
   - Max SoC: 100
   - Latitude: 51.9225
   - Longitude: 4.47917
   - Mileage: 0

2. Search for scooters
3. Update scooter information (test role restrictions for Service Engineers)
4. View scooter details

#### Backup System (Admin roles only)
1. Create a backup
2. List available backups
3. Generate restore code (Super Admin only)
4. Test restore functionality

#### Logging System
1. Perform various operations
2. View system logs (Admin roles only)
3. Check for suspicious activity detection

### 4. Security Testing

#### Input Validation
Test with invalid inputs:
- Invalid email formats
- Wrong zip code format (should be XXXXXX)
- Invalid phone numbers
- SQL injection attempts in search fields
- Null bytes in inputs

#### Authentication Security
- Test with wrong passwords (triggers suspicious activity)
- Test with empty credentials
- Test role-based access restrictions

#### Data Encryption
1. Check database file with external SQLite browser
2. Verify that sensitive data is encrypted
3. Check that passwords are hashed (not visible)

### 5. Expected Behavior

#### Valid Operations
- ✅ All menu options work correctly
- ✅ Data validation prevents invalid inputs
- ✅ Role restrictions are enforced
- ✅ All activities are logged
- ✅ Sensitive data is encrypted in database

#### Security Features
- ✅ SQL injection attempts are blocked
- ✅ Invalid inputs are rejected with clear error messages
- ✅ Multiple failed logins are flagged as suspicious
- ✅ Unauthorized access attempts are logged
- ✅ Database contains encrypted data (not readable)

### 6. Sample Test Data

#### Test Traveller
```
First Name: Alice
Last Name: Johnson
Birthday: 1985-06-20
Gender: female
Street: Witte de Withstraat
House Number: 45
Zip Code: 3012BK
City: Rotterdam
Email: alice.johnson@example.com
Phone: 87654321
License: CD9876543
```

#### Test Scooter
```
Brand: NIU
Model: NGT Sport
Serial: XYZ9876543210
Top Speed: 45
Battery: 3500
Current SoC: 65
Min SoC: 15
Max SoC: 95
Latitude: 51.9244
Longitude: 4.4777
Mileage: 1250
```

### 7. Troubleshooting

#### Common Issues
- **Login fails**: Make sure password includes the `?` character
- **Database errors**: Check if `data/` directory exists
- **Import errors**: Verify all dependencies are installed
- **Permission errors**: Check file permissions for database and key files

#### Debug Mode
For debugging, you can run individual test files:
```bash
python debug_auth.py       # Test authentication
python test_complete_login.py  # Test complete login flow
```

### 8. Assignment Requirements Checklist

- ✅ Console-based interface implemented
- ✅ SQLite database with encrypted sensitive data
- ✅ Role-based access control (3 roles)
- ✅ Input validation (whitelist approach)
- ✅ SQL injection protection (parameterized queries)
- ✅ Password hashing (bcrypt)
- ✅ Data encryption (Fernet)
- ✅ Activity logging with encryption
- ✅ Suspicious activity detection
- ✅ Backup and restore system
- ✅ Hard-coded super admin account
- ✅ User-friendly interface with clear instructions

The system is ready for demonstration and meets all assignment requirements!
