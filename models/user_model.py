from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from db.dbconn import db
from security import encrypt_data, decrypt_data, hash_password, verify_password
from services.log_service import LogService
from utils.validators import InputValidator, ValidationError

@dataclass
class User:
    id: int
    username: str
    role: str
    first_name: str
    last_name: str
    registration_date: str
    password_hash: str = None

class UserModel:
    """User model with secure operations"""
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """Authenticate user login"""
        try:
            # Input validation
            username = InputValidator.sanitize_input(username)
            password = InputValidator.sanitize_input(password)
            
            if not username or not password:
                LogService.log_suspicious_activity(username, "Empty username or password in login attempt")
                return None
            
            # Handle hard-coded super admin
            if username.lower() == 'super_admin':
                if password == 'Admin_123?':
                    LogService.log_login_attempt('super_admin', True)
                    return User(
                        id=0,
                        username='super_admin',
                        role='super_admin',
                        first_name='Super',
                        last_name='Administrator',
                        registration_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                else:
                    LogService.log_login_attempt('super_admin', False, "Wrong password")
                    return None
            
            # Query encrypted database
            encrypted_username = encrypt_data(username.lower())
            query = "SELECT * FROM users WHERE username = ?"
            result = db.execute_query(query, (encrypted_username,))
            
            if not result:
                LogService.log_login_attempt(username, False, "Username not found")
                return None
            
            user_data = result[0]
            
            # Verify password
            if verify_password(password, user_data[2]):  # password_hash is at index 2
                # Decrypt user data
                decrypted_first_name = decrypt_data(user_data[4])
                decrypted_last_name = decrypt_data(user_data[5])
                
                user = User(
                    id=user_data[0],
                    username=username.lower(),
                    role=user_data[3],
                    first_name=decrypted_first_name,
                    last_name=decrypted_last_name,
                    registration_date=user_data[6]
                )
                
                LogService.log_login_attempt(username, True)
                return user
            else:
                LogService.log_login_attempt(username, False, "Wrong password")
                
                # Check for multiple failed attempts
                if LogService.detect_multiple_failed_logins(username):
                    LogService.log_suspicious_activity(
                        username, 
                        "Multiple failed login attempts detected",
                        "Possible brute force attack"
                    )
                
                return None
                
        except Exception as e:
            LogService.log_suspicious_activity(username, f"Login error: {str(e)}")
            return None
    
    @staticmethod
    def create_user(admin_user: User, username: str, password: str, role: str, 
                   first_name: str, last_name: str) -> bool:
        """Create new user account"""
        try:
            # Validate permissions
            if not UserModel._can_create_user(admin_user.role, role):
                raise ValidationError("Insufficient permissions to create this user role")
            
            # Validate inputs
            username = InputValidator.validate_username(username)
            password = InputValidator.validate_password(password)
            first_name = InputValidator.validate_name(first_name, "First name")
            last_name = InputValidator.validate_name(last_name, "Last name")
            
            if role not in ['system_admin', 'service_engineer']:
                raise ValidationError("Invalid role")
            
            # Check if username already exists
            encrypted_username = encrypt_data(username)
            existing_query = "SELECT COUNT(*) FROM users WHERE username = ?"
            if db.execute_scalar(existing_query, (encrypted_username,)) > 0:
                raise ValidationError("Username already exists")
            
            # Create user
            password_hash = hash_password(password)
            encrypted_first_name = encrypt_data(first_name)
            encrypted_last_name = encrypt_data(last_name)
            registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            query = """
            INSERT INTO users (username, password_hash, role, first_name, last_name, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            db.execute_non_query(query, (
                encrypted_username, password_hash, role,
                encrypted_first_name, encrypted_last_name, registration_date
            ))
            
            LogService.log_user_creation(admin_user.username, username, role)
            return True
            
        except Exception as e:
            LogService.log_suspicious_activity(admin_user.username, f"User creation failed: {str(e)}")
            raise e
    
    @staticmethod
    def update_user_password(current_user: User, new_password: str) -> bool:
        """Update user's own password"""
        try:
            new_password = InputValidator.validate_password(new_password)
            password_hash = hash_password(new_password)
            
            if current_user.username == 'super_admin':
                raise ValidationError("Cannot change super admin password")
            
            encrypted_username = encrypt_data(current_user.username)
            query = "UPDATE users SET password_hash = ? WHERE username = ?"
            
            rows_affected = db.execute_non_query(query, (password_hash, encrypted_username))
            
            if rows_affected > 0:
                LogService.log_activity(current_user.username, "Password updated")
                return True
            
            return False
            
        except Exception as e:
            LogService.log_suspicious_activity(current_user.username, f"Password update failed: {str(e)}")
            raise e
    
    @staticmethod
    def reset_user_password(admin_user: User, target_username: str, new_password: str) -> bool:
        """Admin reset user password"""
        try:
            # Validate permissions
            if admin_user.role not in ['super_admin', 'system_admin']:
                raise ValidationError("Insufficient permissions")
            
            new_password = InputValidator.validate_password(new_password)
            target_username = InputValidator.sanitize_input(target_username).lower()
            
            if target_username == 'super_admin':
                raise ValidationError("Cannot reset super admin password")
            
            password_hash = hash_password(new_password)
            encrypted_username = encrypt_data(target_username)
            
            query = "UPDATE users SET password_hash = ? WHERE username = ?"
            rows_affected = db.execute_non_query(query, (password_hash, encrypted_username))
            
            if rows_affected > 0:
                LogService.log_password_reset(admin_user.username, target_username)
                return True
            
            return False
            
        except Exception as e:
            LogService.log_suspicious_activity(admin_user.username, f"Password reset failed: {str(e)}")
            raise e
    
    @staticmethod
    def get_all_users(admin_user: User) -> List[User]:
        """Get all users (admin only)"""
        try:
            if admin_user.role not in ['super_admin', 'system_admin']:
                raise ValidationError("Insufficient permissions")
            
            query = "SELECT * FROM users"
            results = db.execute_query(query)
            
            users = []
            for result in results:
                user = User(
                    id=result[0],
                    username=decrypt_data(result[1]),
                    role=result[3],
                    first_name=decrypt_data(result[4]),
                    last_name=decrypt_data(result[5]),
                    registration_date=result[6]
                )
                users.append(user)
            
            LogService.log_activity(admin_user.username, "Viewed user list")
            return users
            
        except Exception as e:
            LogService.log_suspicious_activity(admin_user.username, f"Get users failed: {str(e)}")
            raise e
    
    @staticmethod
    def delete_user(admin_user: User, target_username: str) -> bool:
        """Delete user account"""
        try:
            # Validate permissions
            if not UserModel._can_delete_user(admin_user.role, target_username):
                raise ValidationError("Insufficient permissions")
            
            target_username = InputValidator.sanitize_input(target_username).lower()
            
            if target_username == 'super_admin':
                raise ValidationError("Cannot delete super admin")
            
            encrypted_username = encrypt_data(target_username)
            query = "DELETE FROM users WHERE username = ?"
            
            rows_affected = db.execute_non_query(query, (encrypted_username,))
            
            if rows_affected > 0:
                LogService.log_user_deletion(admin_user.username, target_username)
                return True
            
            return False
            
        except Exception as e:
            LogService.log_suspicious_activity(admin_user.username, f"User deletion failed: {str(e)}")
            raise e
    
    @staticmethod
    def update_user_profile(admin_user: User, target_username: str, first_name: str, last_name: str) -> bool:
        """Update user profile"""
        try:
            # Validate inputs
            first_name = InputValidator.validate_name(first_name, "First name")
            last_name = InputValidator.validate_name(last_name, "Last name")
            target_username = InputValidator.sanitize_input(target_username).lower()
            
            # Check permissions
            if admin_user.username != target_username and admin_user.role not in ['super_admin', 'system_admin']:
                raise ValidationError("Insufficient permissions")
            
            encrypted_username = encrypt_data(target_username)
            encrypted_first_name = encrypt_data(first_name)
            encrypted_last_name = encrypt_data(last_name)
            
            query = "UPDATE users SET first_name = ?, last_name = ? WHERE username = ?"
            rows_affected = db.execute_non_query(query, (
                encrypted_first_name, encrypted_last_name, encrypted_username
            ))
            
            if rows_affected > 0:
                LogService.log_activity(admin_user.username, f"Updated profile for {target_username}")
                return True
            
            return False
            
        except Exception as e:
            LogService.log_suspicious_activity(admin_user.username, f"Profile update failed: {str(e)}")
            raise e
    
    @staticmethod
    def _can_create_user(admin_role: str, target_role: str) -> bool:
        """Check if admin can create user with target role"""
        if admin_role == 'super_admin':
            return target_role in ['system_admin', 'service_engineer']
        elif admin_role == 'system_admin':
            return target_role == 'service_engineer'
        return False
    
    @staticmethod
    def _can_delete_user(admin_role: str, target_username: str) -> bool:
        """Check if admin can delete target user"""
        if target_username == 'super_admin':
            return False
        
        if admin_role == 'super_admin':
            return True
        elif admin_role == 'system_admin':
            # System admin can only delete service engineers
            encrypted_username = encrypt_data(target_username)
            query = "SELECT role FROM users WHERE username = ?"
            result = db.execute_query(query, (encrypted_username,))
            if result:
                return result[0][0] == 'service_engineer'
        
        return False