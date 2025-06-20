from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from core.db.dbconn import db
from security import encrypt_data, decrypt_data, hash_password, verify_password, encrypt_username_deterministic
from core.services.log_service import LogService
from core.utils.validators import InputValidator, ValidationError

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
            encrypted_username = encrypt_username_deterministic(username.lower())
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
    
    # Add a new column for encrypted username if it doesn't exist
    @staticmethod
    def ensure_username_enc_column():
        try:
            db.execute_non_query("ALTER TABLE users ADD COLUMN username_enc TEXT", ())
        except Exception:
            pass  # Column may already exist

    @staticmethod
    def get_all_users(admin_user: User) -> list:
        """List all users (show real username using encrypted column)"""
        UserModel.ensure_username_enc_column()
        try:
            if admin_user.role not in ['super_admin', 'system_admin']:
                raise ValidationError("Insufficient permissions")
            query = "SELECT id, username_enc, role, first_name, last_name, registration_date FROM users"
            results = db.execute_query(query)
            users = []
            for result in results:
                try:
                    display_username = decrypt_data(result[1]) if result[1] else f"user_{result[0]}"
                    user = User(
                        id=result[0],
                        username=display_username,
                        role=result[2],
                        first_name=decrypt_data(result[3]),
                        last_name=decrypt_data(result[4]),
                        registration_date=result[5]
                    )
                    users.append(user)
                except Exception as e:
                    print(f"Warning: Skipping user id={result[0]} due to decryption error: {e}")
            LogService.log_activity(admin_user.username, "Viewed user list")
            return users
        except Exception as e:
            LogService.log_suspicious_activity(admin_user.username, f"User list failed: {str(e)}")
            raise e
    
    @staticmethod
    def create_user(admin_user: User, username: str, password: str, role: str, 
                   first_name: str, last_name: str) -> bool:
        UserModel.ensure_username_enc_column()
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
            encrypted_username = encrypt_username_deterministic(username)
            existing_query = "SELECT COUNT(*) FROM users WHERE username = ?"
            if db.execute_scalar(existing_query, (encrypted_username,)) > 0:
                raise ValidationError("Username already exists")
            
            # Create user
            password_hash = hash_password(password)
            encrypted_first_name = encrypt_data(first_name)
            encrypted_last_name = encrypt_data(last_name)
            registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Store encrypted username for display
            encrypted_username_enc = encrypt_data(username)
            
            query = """
            INSERT INTO users (username, username_enc, password_hash, role, first_name, last_name, registration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            db.execute_non_query(query, (
                encrypted_username, encrypted_username_enc, password_hash, role,
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
            
            encrypted_username = encrypt_username_deterministic(current_user.username)
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
            encrypted_username = encrypt_username_deterministic(target_username)
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
    def get_all_users(admin_user: User) -> list:
        """List all users (show real username using encrypted column)"""
        UserModel.ensure_username_enc_column()
        try:
            if admin_user.role not in ['super_admin', 'system_admin']:
                raise ValidationError("Insufficient permissions")
            query = "SELECT id, username_enc, role, first_name, last_name, registration_date FROM users"
            results = db.execute_query(query)
            users = []
            for result in results:
                try:
                    display_username = decrypt_data(result[1]) if result[1] else f"user_{result[0]}"
                    user = User(
                        id=result[0],
                        username=display_username,
                        role=result[2],
                        first_name=decrypt_data(result[3]),
                        last_name=decrypt_data(result[4]),
                        registration_date=result[5]
                    )
                    users.append(user)
                except Exception as e:
                    print(f"Warning: Skipping user id={result[0]} due to decryption error: {e}")
            LogService.log_activity(admin_user.username, "Viewed user list")
            return users
        except Exception as e:
            LogService.log_suspicious_activity(admin_user.username, f"User list failed: {str(e)}")
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
            
            encrypted_username = encrypt_username_deterministic(target_username)
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

            # Check permissions (robust, role-based)
            # Fetch target user's role
            encrypted_target_username = encrypt_username_deterministic(target_username)
            target_user_row = db.execute_query("SELECT role FROM users WHERE username = ?", (encrypted_target_username,))
            if not target_user_row:
                raise ValidationError("Target user does not exist")
            target_role = target_user_row[0][0]

            # Permission logic:
            # - super_admin can update anyone
            # - system_admin can update themselves and service_engineers
            # - service_engineer can only update themselves
            if admin_user.role == 'super_admin':
                pass  # can update anyone
            elif admin_user.role == 'system_admin':
                if target_role == 'system_admin' and admin_user.username != target_username:
                    raise ValidationError("System admin can only update themselves or service engineers")
                if target_role == 'super_admin':
                    raise ValidationError("Cannot update super admin")
            elif admin_user.role == 'service_engineer':
                if admin_user.username != target_username:
                    raise ValidationError("Service engineer can only update their own profile")
            else:
                raise ValidationError("Insufficient permissions")

            # Use deterministic encryption for username lookup
            encrypted_username = encrypt_username_deterministic(target_username)
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
    def username_exists(username: str) -> bool:
        """Check if a username already exists in the database (case-insensitive, encrypted)"""
        encrypted_username = encrypt_data(username.lower())
        query = "SELECT COUNT(*) FROM users WHERE username = ?"
        count = db.execute_scalar(query, (encrypted_username,))
        return count > 0
    
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
            encrypted_username = encrypt_username_deterministic(target_username)
            query = "SELECT role FROM users WHERE username = ?"
            result = db.execute_query(query, (encrypted_username,))
            if result:
                return result[0][0] == 'service_engineer'
        
        return False
    
    @staticmethod
    def delete_user_by_id(admin_user: User, user_id: int) -> bool:
        """Delete user account by user ID (admin action)"""
        try:
            # Fetch target user info
            user_row = db.execute_query("SELECT username, role FROM users WHERE id = ?", (user_id,))
            if not user_row:
                raise ValidationError("Target user does not exist")
            target_username, target_role = user_row[0]
            # Prevent deleting super_admin
            if target_username == encrypt_username_deterministic('super_admin'):
                raise ValidationError("Cannot delete super admin")
            # Permission check
            if admin_user.role == 'super_admin':
                pass
            elif admin_user.role == 'system_admin':
                if target_role != 'service_engineer':
                    raise ValidationError("System admin can only delete service engineers")
            else:
                raise ValidationError("Insufficient permissions")
            # Delete
            rows_affected = db.execute_non_query("DELETE FROM users WHERE id = ?", (user_id,))
            if rows_affected > 0:
                LogService.log_user_deletion(admin_user.username, f"id={user_id}")
                return True
            return False
        except Exception as e:
            LogService.log_suspicious_activity(admin_user.username, f"User deletion by id failed: {str(e)}")
            raise e
    
    @staticmethod
    def update_user_profile_by_id(admin_user: User, user_id: int, first_name: str, last_name: str) -> bool:
        """Update user profile by user ID (admin action)"""
        try:
            # Validate inputs
            first_name = InputValidator.validate_name(first_name, "First name")
            last_name = InputValidator.validate_name(last_name, "Last name")
            # Fetch target user info
            user_row = db.execute_query("SELECT username, role FROM users WHERE id = ?", (user_id,))
            if not user_row:
                raise ValidationError("Target user does not exist")
            target_username, target_role = user_row[0]
            # Permission logic (same as update_user_profile)
            if admin_user.role == 'super_admin':
                pass
            elif admin_user.role == 'system_admin':
                if target_role == 'system_admin' and admin_user.username != target_username:
                    raise ValidationError("System admin can only update themselves or service engineers")
                if target_role == 'super_admin':
                    raise ValidationError("Cannot update super admin")
            elif admin_user.role == 'service_engineer':
                if admin_user.username != target_username:
                    raise ValidationError("Service engineer can only update their own profile")
            else:
                raise ValidationError("Insufficient permissions")
            encrypted_first_name = encrypt_data(first_name)
            encrypted_last_name = encrypt_data(last_name)
            query = "UPDATE users SET first_name = ?, last_name = ? WHERE id = ?"
            rows_affected = db.execute_non_query(query, (
                encrypted_first_name, encrypted_last_name, user_id
            ))
            if rows_affected > 0:
                LogService.log_activity(admin_user.username, f"Updated profile for id={user_id}")
                return True
            return False
        except Exception as e:
            LogService.log_suspicious_activity(admin_user.username, f"Profile update by id failed: {str(e)}")
            raise e
    
    @staticmethod
    def reset_user_password_by_id(admin_user: User, user_id: int, new_password: str) -> bool:
        """Reset user password by user ID (admin action)"""
        try:
            # Validate password
            InputValidator.validate_password(new_password)
            # Fetch target user info
            user_row = db.execute_query("SELECT username, role FROM users WHERE id = ?", (user_id,))
            if not user_row:
                raise ValidationError("Target user does not exist")
            target_username, target_role = user_row[0]
            # Permission logic (same as update/delete)
            if admin_user.role == 'super_admin':
                pass
            elif admin_user.role == 'system_admin':
                if target_role == 'system_admin' and admin_user.username != target_username:
                    raise ValidationError("System admin can only reset their own or service engineer passwords")
                if target_role == 'super_admin':
                    raise ValidationError("Cannot reset super admin password")
            elif admin_user.role == 'service_engineer':
                if admin_user.username != target_username:
                    raise ValidationError("Service engineer can only reset their own password")
            else:
                raise ValidationError("Insufficient permissions")
            password_hash = hash_password(new_password)
            query = "UPDATE users SET password_hash = ? WHERE id = ?"
            rows_affected = db.execute_non_query(query, (password_hash, user_id))
            if rows_affected > 0:
                LogService.log_activity(admin_user.username, f"Reset password for id={user_id}")
                return True
            return False
        except Exception as e:
            LogService.log_suspicious_activity(admin_user.username, f"Password reset by id failed: {str(e)}")
            raise e