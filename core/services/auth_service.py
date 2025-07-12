import getpass
import os
from typing import Optional
from core.models.user_model import User, UserModel
from core.services.log_service import LogService
from core.utils.validators import ValidationError

class AuthService:
    """Authentication and session management service"""
    
    current_user: Optional[User] = None
    
    @staticmethod
    def login_user() -> Optional[User]:
        """Handle user login process"""
        max_attempts = 3
        attempts = 0
        
        while attempts < max_attempts:
            try:
                print("\n" + "="*50)
                print("   URBAN MOBILITY BACKEND SYSTEM")
                print("="*50)
                print("\nLogin Required")
                
                username = input("Username: ").strip()
                try:
                    password = getpass.getpass("Password: ")
                except (EOFError, KeyboardInterrupt):
                    print("\nPassword input cancelled.")
                    return None
                except Exception:
                    # Fallback to regular input if getpass fails
                    print("Note: Password will be visible")
                    password = input("Password: ").strip()
                
                if not username:
                    print("❌ Username is required")
                    attempts += 1
                    continue
                
                if not password:
                    print("❌ Password is required")
                    attempts += 1
                    continue
                
                user = UserModel.authenticate_user(username, password)
                
                if user:
                    AuthService.current_user = user
                    print(f"✅ Welcome, {user.first_name} {user.last_name}!")
                    print(f"Role: {user.role.replace('_', ' ').title()}")
                    
                    # Check for suspicious activities
                    suspicious_count = LogService.get_suspicious_logs_count()
                    if suspicious_count > 0 and user.role in ['super_admin', 'system_admin']:
                        print(f"⚠️  Warning: {suspicious_count} suspicious activities detected!")
                    
                    return user
                else:
                    attempts += 1
                    remaining = max_attempts - attempts
                    if remaining > 0:
                        print(f"❌ Invalid credentials. {remaining} attempts remaining.")
                    else:
                        print("❌ Maximum login attempts exceeded.")
                
            except KeyboardInterrupt:
                print("\n\nLogin cancelled.")
                return None
            except Exception as e:
                print(f"❌ Login error: {e}")
                attempts += 1
        
        # Log suspicious activity after max attempts
        try:
            LogService.log_suspicious_activity(
                username if 'username' in locals() else None,
                "Maximum login attempts exceeded",
                "Possible brute force attack"
            )
        except:
            pass  # Don't fail if logging fails
        
        return None
    
    @staticmethod
    def logout_user():
        """Handle user logout"""
        if AuthService.current_user:
            LogService.log_activity(AuthService.current_user.username, "Logged out")
            AuthService.current_user = None
        print("👋 Goodbye!")
    
    @staticmethod
    def require_auth(required_roles: list = None) -> bool:
        """Check if user is authenticated and has required role"""
        if not AuthService.current_user:
            print("❌ Authentication required")
            return False
        
        if required_roles and AuthService.current_user.role not in required_roles:
            print("❌ Insufficient permissions")
            LogService.log_suspicious_activity(
                AuthService.current_user.username,
                "Unauthorized access attempt",
                f"Required roles: {required_roles}, User role: {AuthService.current_user.role}"
            )
            return False
        
        return True
    
    @staticmethod
    def get_current_user() -> Optional[User]:
        """Get current authenticated user"""
        return AuthService.current_user
    
    @staticmethod
    def change_password():
        """Change current user's password"""
        if not AuthService.require_auth():
            return
        
        if AuthService.current_user.username == 'super_admin':
            print("❌ Super admin password cannot be changed")
            return
        
        try:
            print("\n--- Change Password ---")
            new_password = getpass.getpass("New password: ")
            confirm_password = getpass.getpass("Confirm password: ")
            
            if new_password != confirm_password:
                print("❌ Passwords do not match")
                return
            
            if UserModel.update_user_password(AuthService.current_user, new_password):
                print("✅ Password updated successfully")
            else:
                print("❌ Failed to update password")
                
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    @staticmethod
    def clear_screen():
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def pause():
        """Pause for user input"""
        input("\nPress Enter to continue...")
    
    @staticmethod
    def confirm_action(message: str) -> bool:
        """Get user confirmation for potentially dangerous actions"""
        while True:
            response = input(f"{message} (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no")

# Global authentication instance
auth = AuthService()
