from typing import List, Optional
from models.user_model import User, UserModel
from services.backup_service import BackupService
from services.log_service import LogService
from utils.validators import ValidationError
import getpass

class UserManagementService:
    """Service for user management operations"""
    
    @staticmethod
    def create_user_interactive(admin_user: User) -> bool:
        """Interactive user creation"""
        try:
            print("\n--- Create New User ---")
            
            # Show what roles can be created
            if admin_user.role == 'super_admin':
                print("Available roles: system_admin, service_engineer")
                available_roles = ['system_admin', 'service_engineer']
            elif admin_user.role == 'system_admin':
                print("Available roles: service_engineer")
                available_roles = ['service_engineer']
            else:
                print("❌ Insufficient permissions to create users")
                return False
            
            role = input("Role: ").strip().lower()
            if role not in available_roles:
                print(f"❌ Invalid role. Available: {', '.join(available_roles)}")
                return False
            
            username = input("Username (8-10 chars): ").strip()
            password = getpass.getpass("Password (12-30 chars): ")
            confirm_password = getpass.getpass("Confirm password: ")
            
            if password != confirm_password:
                print("❌ Passwords do not match")
                return False
            
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()
            
            if UserModel.create_user(admin_user, username, password, role, first_name, last_name):
                print("✅ User created successfully!")
                return True
            else:
                print("❌ Failed to create user")
                return False
                
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return False
    
    @staticmethod
    def list_users(admin_user: User) -> List[User]:
        """List all users"""
        if admin_user.role not in ['super_admin', 'system_admin']:
            print("❌ Only Super Admin and System Admin can list users")
            return []
        
        try:
            users = UserModel.get_all_users(admin_user)
            
            if not users:
                print("No users found.")
                return []
            
            print(f"\n--- Users List ({len(users)} total) ---")
            print(f"{'ID':<5} {'Username':<12} {'Role':<15} {'Name':<25} {'Registration':<20}")
            print("-" * 80)
            
            for user in users:
                name = f"{user.first_name} {user.last_name}"
                role_display = user.role.replace('_', ' ').title()
                print(f"{user.id:<5} {user.username:<12} {role_display:<15} "
                      f"{name:<25} {user.registration_date:<20}")
            
            return users
            
        except Exception as e:
            print(f"❌ Error listing users: {e}")
            return []
    
    @staticmethod
    def update_user_profile_interactive(admin_user: User) -> bool:
        """Interactive user profile update"""
        try:
            print("\n--- Update User Profile ---")
            
            if admin_user.role == 'super_admin':
                target_username = input("Username to update (or 'self' for your profile): ").strip()
                if target_username.lower() == 'self':
                    target_username = admin_user.username
            else:
                target_username = admin_user.username
                print(f"Updating your profile: {target_username}")
            
            first_name = input("New First Name: ").strip()
            last_name = input("New Last Name: ").strip()
            
            if UserModel.update_user_profile(admin_user, target_username, first_name, last_name):
                print("✅ Profile updated successfully!")
                return True
            else:
                print("❌ Failed to update profile")
                return False
                
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return False
    
    @staticmethod
    def reset_user_password_interactive(admin_user: User) -> bool:
        """Interactive password reset"""
        if admin_user.role not in ['super_admin', 'system_admin']:
            print("❌ Only Super Admin and System Admin can reset passwords")
            return False
        
        try:
            print("\n--- Reset User Password ---")
            
            target_username = input("Username to reset password: ").strip()
            new_password = getpass.getpass("New password: ")
            confirm_password = getpass.getpass("Confirm password: ")
            
            if new_password != confirm_password:
                print("❌ Passwords do not match")
                return False
            
            if UserModel.reset_user_password(admin_user, target_username, new_password):
                print("✅ Password reset successfully!")
                return True
            else:
                print("❌ Failed to reset password")
                return False
                
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return False
    
    @staticmethod
    def delete_user_interactive(admin_user: User) -> bool:
        """Interactive user deletion"""
        if admin_user.role not in ['super_admin', 'system_admin']:
            print("❌ Only Super Admin and System Admin can delete users")
            return False
        
        try:
            print("\n--- Delete User ---")
            
            target_username = input("Username to delete: ").strip()
            
            if target_username == admin_user.username:
                print("❌ Cannot delete your own account using this method")
                return False
            
            if target_username == 'super_admin':
                print("❌ Cannot delete super admin account")
                return False
            
            # Confirm deletion
            confirm = input(f"Are you sure you want to delete user '{target_username}'? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("Deletion cancelled.")
                return False
            
            if UserModel.delete_user(admin_user, target_username):
                print("✅ User deleted successfully!")
                return True
            else:
                print("❌ Failed to delete user")
                return False
                
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return False
    
    @staticmethod
    def manage_backup_restore_codes(admin_user: User):
        """Manage backup and restore codes (Super Admin only)"""
        if admin_user.role != 'super_admin':
            print("❌ Only Super Admin can manage restore codes")
            return
        
        while True:
            print("\n--- Backup & Restore Code Management ---")
            print("1. List all restore codes")
            print("2. Generate restore code")
            print("3. Revoke restore code")
            print("4. Back to main menu")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                UserManagementService._list_restore_codes(admin_user)
            elif choice == '2':
                UserManagementService._generate_restore_code(admin_user)
            elif choice == '3':
                UserManagementService._revoke_restore_code(admin_user)
            elif choice == '4':
                break
            else:
                print("❌ Invalid choice")
    
    @staticmethod
    def _list_restore_codes(admin_user: User):
        """List all restore codes"""
        try:
            codes = BackupService.list_restore_codes(admin_user)
            
            if not codes:
                print("No restore codes found.")
                return
            
            print(f"\n--- Restore Codes ({len(codes)} total) ---")
            print(f"{'ID':<5} {'Code':<15} {'Admin':<15} {'Backup':<25} {'Used':<6} {'Created':<20}")
            print("-" * 90)
            
            for code in codes:
                used_status = "Yes" if code['used'] else "No"
                print(f"{code['id']:<5} {code['code']:<15} {code['system_admin_username']:<15} "
                      f"{code['backup_filename']:<25} {used_status:<6} {code['created_at']:<20}")
                
        except Exception as e:
            print(f"❌ Error listing restore codes: {e}")
    
    @staticmethod
    def _generate_restore_code(admin_user: User):
        """Generate restore code"""
        try:
            # List available backups
            backups = BackupService.list_backups(admin_user)
            if not backups:
                print("No backups available.")
                return
            
            print("\nAvailable backups:")
            for i, backup in enumerate(backups, 1):
                size_str = BackupService.format_file_size(backup['size'])
                print(f"{i}. {backup['filename']} ({size_str}) - {backup['modified']}")
            
            backup_choice = input(f"\nSelect backup (1-{len(backups)}): ").strip()
            try:
                backup_index = int(backup_choice) - 1
                if not 0 <= backup_index < len(backups):
                    raise ValueError()
                selected_backup = backups[backup_index]['filename']
            except ValueError:
                print("❌ Invalid backup selection")
                return
            
            admin_username = input("System Admin username to authorize: ").strip()
            
            restore_code = BackupService.generate_restore_code(admin_user, selected_backup, admin_username)
            
            print(f"✅ Restore code generated: {restore_code}")
            print(f"   Backup: {selected_backup}")
            print(f"   Authorized for: {admin_username}")
            print("   This code can only be used once!")
            
        except Exception as e:
            print(f"❌ Error generating restore code: {e}")
    
    @staticmethod
    def _revoke_restore_code(admin_user: User):
        """Revoke restore code"""
        try:
            restore_code = input("Enter restore code to revoke: ").strip()
            
            if BackupService.revoke_restore_code(admin_user, restore_code):
                print("✅ Restore code revoked successfully!")
            else:
                print("❌ Failed to revoke restore code (may not exist or already used)")
                
        except Exception as e:
            print(f"❌ Error revoking restore code: {e}")
