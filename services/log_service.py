import os
from datetime import datetime
from typing import Optional
from db.dbconn import db
from security import encrypt_data

class LogService:
    """Secure logging service with encryption"""
    
    @staticmethod
    def log_activity(username: Optional[str], description: str, additional_info: str = "", suspicious: bool = False):
        """Log user activity to encrypted database"""
        try:
            current_date = datetime.now().strftime('%Y-%m-%d')
            current_time = datetime.now().strftime('%H:%M:%S')
            
            # Encrypt sensitive log data
            encrypted_username = encrypt_data(username or "")
            encrypted_description = encrypt_data(description)
            encrypted_additional_info = encrypt_data(additional_info)
            
            query = """
            INSERT INTO logs (date, time, username, activity_description, additional_info, suspicious)
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            db.execute_non_query(query, (
                current_date, current_time, encrypted_username,
                encrypted_description, encrypted_additional_info, suspicious
            ))
            
        except Exception as e:
            # Log to console if database logging fails
            print(f"Logging error: {e}")
    
    @staticmethod
    def log_login_attempt(username: str, success: bool, additional_info: str = ""):
        """Log login attempts"""
        description = "Successful login" if success else "Failed login attempt"
        suspicious = not success
        LogService.log_activity(username, description, additional_info, suspicious)
    
    @staticmethod
    def log_user_creation(admin_username: str, new_username: str, role: str):
        """Log user creation"""
        description = f"New {role} user created"
        additional_info = f"Username: {new_username}"
        LogService.log_activity(admin_username, description, additional_info)
    
    @staticmethod
    def log_user_deletion(admin_username: str, deleted_username: str):
        """Log user deletion"""
        description = "User account deleted"
        additional_info = f"Deleted user: {deleted_username}"
        LogService.log_activity(admin_username, description, additional_info)
    
    @staticmethod
    def log_password_reset(admin_username: str, target_username: str):
        """Log password reset"""
        description = "Password reset performed"
        additional_info = f"Password reset for user: {target_username}"
        LogService.log_activity(admin_username, description, additional_info)
    
    @staticmethod
    def log_backup_restore(username: str, action: str, backup_name: str = ""):
        """Log backup and restore operations"""
        description = f"Backup {action}"
        additional_info = f"Backup file: {backup_name}" if backup_name else ""
        LogService.log_activity(username, description, additional_info)
    
    @staticmethod
    def log_data_operation(username: str, operation: str, table: str, record_id: str = ""):
        """Log CRUD operations on data"""
        description = f"{operation} operation on {table}"
        additional_info = f"Record ID: {record_id}" if record_id else ""
        LogService.log_activity(username, description, additional_info)
    
    @staticmethod
    def log_suspicious_activity(username: Optional[str], description: str, additional_info: str = ""):
        """Log suspicious activities"""
        LogService.log_activity(username, description, additional_info, suspicious=True)
    
    @staticmethod
    def get_logs_for_admin(admin_username: str) -> list:
        """Get all logs for admin viewing (decrypted)"""
        from security import decrypt_data
        
        query = "SELECT * FROM logs ORDER BY date DESC, time DESC"
        encrypted_logs = db.execute_query(query)
        
        decrypted_logs = []
        for log in encrypted_logs:
            try:
                decrypted_log = {
                    'id': log[0],
                    'date': log[1],
                    'time': log[2],
                    'username': decrypt_data(log[3]) if log[3] else "",
                    'description': decrypt_data(log[4]),
                    'additional_info': decrypt_data(log[5]) if log[5] else "",
                    'suspicious': bool(log[6])
                }
                decrypted_logs.append(decrypted_log)
            except Exception as e:
                # If decryption fails, log the error but continue
                print(f"Error decrypting log entry {log[0]}: {e}")
                continue
        
        # Log the admin viewing logs
        LogService.log_activity(admin_username, "Viewed system logs")
        
        return decrypted_logs
    
    @staticmethod
    def get_suspicious_logs_count() -> int:
        """Get count of unread suspicious activities"""
        query = "SELECT COUNT(*) FROM logs WHERE suspicious = 1"
        return db.execute_scalar(query) or 0
    
    @staticmethod
    def detect_multiple_failed_logins(username: str, time_window_minutes: int = 10) -> bool:
        """Detect multiple failed login attempts in time window"""
        from security import encrypt_data
        
        # Get current time and calculate time window
        current_time = datetime.now()
        window_start = current_time.replace(
            minute=max(0, current_time.minute - time_window_minutes)
        ).strftime('%H:%M:%S')
        current_time_str = current_time.strftime('%H:%M:%S')
        current_date = current_time.strftime('%Y-%m-%d')
        
        encrypted_username = encrypt_data(username)
        encrypted_description = encrypt_data("Failed login attempt")
        
        query = """
        SELECT COUNT(*) FROM logs 
        WHERE username = ? AND activity_description = ? 
        AND date = ? AND time BETWEEN ? AND ?
        """
        
        failed_count = db.execute_scalar(query, (
            encrypted_username, encrypted_description, 
            current_date, window_start, current_time_str
        )) or 0
        
        return failed_count >= 3  # Flag as suspicious after 3 failures