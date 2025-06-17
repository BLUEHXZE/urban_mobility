import os
import shutil
import zipfile
from datetime import datetime
from typing import Optional, List
import secrets
from core.db.dbconn import db
from core.services.log_service import LogService
from core.models.user_model import User
from core.utils.validators import ValidationError

class BackupService:
    """Backup and restore service for the system"""
    
    BACKUP_DIR = "backups"
    
    @staticmethod
    def create_backup(user: User, backup_name: str = None) -> str:
        """Create a backup of the system"""
        try:
            if user.role not in ['super_admin', 'system_admin']:
                raise ValidationError("Insufficient permissions to create backup")
            
            # Ensure backup directory exists
            os.makedirs(BackupService.BACKUP_DIR, exist_ok=True)
            
            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if not backup_name:
                backup_name = f"backup_{timestamp}"
            
            backup_filename = f"{backup_name}.zip"
            backup_path = os.path.join(BackupService.BACKUP_DIR, backup_filename)
            
            # Create zip file with database
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add database file
                db_path = "data/urban_mobility.db"
                if os.path.exists(db_path):
                    zipf.write(db_path, "urban_mobility.db")
                
                # Add backup metadata
                metadata = f"""Backup created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Created by: {user.username}
Role: {user.role}
"""
                zipf.writestr("backup_info.txt", metadata)
            
            LogService.log_backup_restore(user.username, "created", backup_filename)
            return backup_filename
            
        except Exception as e:
            LogService.log_suspicious_activity(user.username, f"Backup creation failed: {str(e)}")
            raise e
    
    @staticmethod
    def list_backups(user: User) -> List[str]:
        """List all available backups"""
        try:
            if user.role not in ['super_admin', 'system_admin']:
                raise ValidationError("Insufficient permissions to list backups")
            
            if not os.path.exists(BackupService.BACKUP_DIR):
                return []
            
            backups = []
            for filename in os.listdir(BackupService.BACKUP_DIR):
                if filename.endswith('.zip'):
                    backup_path = os.path.join(BackupService.BACKUP_DIR, filename)
                    stat = os.stat(backup_path)
                    size = stat.st_size
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    backups.append({
                        'filename': filename,
                        'size': size,
                        'modified': modified,
                        'path': backup_path
                    })
            
            # Sort by modification time (newest first)
            backups.sort(key=lambda x: x['modified'], reverse=True)
            
            LogService.log_activity(user.username, "Listed backups")
            return backups
            
        except Exception as e:
            LogService.log_suspicious_activity(user.username, f"List backups failed: {str(e)}")
            raise e
    
    @staticmethod
    def restore_backup_super_admin(user: User, backup_filename: str) -> bool:
        """Restore backup (Super Admin only)"""
        try:
            if user.role != 'super_admin':
                raise ValidationError("Only Super Admin can restore backups directly")
            
            backup_path = os.path.join(BackupService.BACKUP_DIR, backup_filename)
            
            if not os.path.exists(backup_path):
                raise ValidationError("Backup file not found")
            
            # Create backup of current database
            current_backup = BackupService.create_backup(user, f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Extract backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Extract database
                zipf.extract("urban_mobility.db", "data/")
            
            LogService.log_backup_restore(user.username, "restored", backup_filename)
            return True
            
        except Exception as e:
            LogService.log_suspicious_activity(user.username, f"Backup restore failed: {str(e)}")
            raise e
    
    @staticmethod
    def generate_restore_code(user: User, backup_filename: str, system_admin_username: str) -> str:
        """Generate one-time restore code for System Admin"""
        try:
            if user.role != 'super_admin':
                raise ValidationError("Only Super Admin can generate restore codes")
            
            # Validate backup exists
            backup_path = os.path.join(BackupService.BACKUP_DIR, backup_filename)
            if not os.path.exists(backup_path):
                raise ValidationError("Backup file not found")
            
            # Generate secure random code
            restore_code = secrets.token_urlsafe(16)
            created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Store in database
            query = """
            INSERT INTO restore_codes (code, system_admin_username, backup_filename, used, created_at)
            VALUES (?, ?, ?, ?, ?)
            """
            
            db.execute_non_query(query, (restore_code, system_admin_username, backup_filename, False, created_at))
            
            LogService.log_activity(
                user.username, 
                "Generated restore code",
                f"For admin: {system_admin_username}, Backup: {backup_filename}"
            )
            
            return restore_code
            
        except Exception as e:
            LogService.log_suspicious_activity(user.username, f"Generate restore code failed: {str(e)}")
            raise e
    
    @staticmethod
    def restore_with_code(user: User, restore_code: str) -> bool:
        """Restore backup using one-time code (System Admin only)"""
        try:
            if user.role != 'system_admin':
                raise ValidationError("Only System Admin can use restore codes")
            
            # Find valid restore code
            query = """
            SELECT backup_filename, system_admin_username, used 
            FROM restore_codes 
            WHERE code = ?
            """
            
            result = db.execute_query(query, (restore_code,))
            
            if not result:
                raise ValidationError("Invalid restore code")
            
            backup_filename, authorized_admin, used = result[0]
            
            if used:
                LogService.log_suspicious_activity(
                    user.username,
                    "Attempted to use already used restore code",
                    f"Code: {restore_code[:8]}..."
                )
                raise ValidationError("Restore code already used")
            
            if authorized_admin != user.username:
                LogService.log_suspicious_activity(
                    user.username,
                    "Attempted to use restore code for different admin",
                    f"Code authorized for: {authorized_admin}"
                )
                raise ValidationError("Restore code not authorized for this admin")
            
            # Mark code as used
            update_query = "UPDATE restore_codes SET used = ? WHERE code = ?"
            db.execute_non_query(update_query, (True, restore_code))
            
            # Restore backup
            backup_path = os.path.join(BackupService.BACKUP_DIR, backup_filename)
            
            if not os.path.exists(backup_path):
                raise ValidationError("Backup file not found")
            
            # Create backup of current database
            current_backup = BackupService.create_backup(user, f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            # Extract backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Extract database
                zipf.extract("urban_mobility.db", "data/")
            
            LogService.log_backup_restore(user.username, "restored with code", backup_filename)
            return True
            
        except Exception as e:
            LogService.log_suspicious_activity(user.username, f"Restore with code failed: {str(e)}")
            raise e
    
    @staticmethod
    def revoke_restore_code(user: User, restore_code: str) -> bool:
        """Revoke a restore code (Super Admin only)"""
        try:
            if user.role != 'super_admin':
                raise ValidationError("Only Super Admin can revoke restore codes")
            
            query = "UPDATE restore_codes SET used = ? WHERE code = ? AND used = ?"
            rows_affected = db.execute_non_query(query, (True, restore_code, False))
            
            if rows_affected > 0:
                LogService.log_activity(user.username, "Revoked restore code", f"Code: {restore_code[:8]}...")
                return True
            
            return False
            
        except Exception as e:
            LogService.log_suspicious_activity(user.username, f"Revoke restore code failed: {str(e)}")
            raise e
    
    @staticmethod
    def list_restore_codes(user: User) -> List[dict]:
        """List all restore codes (Super Admin only)"""
        try:
            if user.role != 'super_admin':
                raise ValidationError("Only Super Admin can list restore codes")
            
            query = "SELECT * FROM restore_codes ORDER BY created_at DESC"
            results = db.execute_query(query)
            
            codes = []
            for result in results:
                codes.append({
                    'id': result[0],
                    'code': result[1][:8] + "...",  # Partial code for security
                    'system_admin_username': result[2],
                    'backup_filename': result[3],
                    'used': bool(result[4]),
                    'created_at': result[5]
                })
            
            LogService.log_activity(user.username, "Listed restore codes")
            return codes
            
        except Exception as e:
            LogService.log_suspicious_activity(user.username, f"List restore codes failed: {str(e)}")
            raise e
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
