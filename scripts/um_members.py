#!/usr/bin/env python3
"""
Urban Mobility Backend System
Main application entry point with secure console interface
"""

import os
import sys
from datetime import datetime
from typing import Optional
import traceback

# ✅ Ensure project root is added to module path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.init_db import initialize_database
from core.services.auth_service import AuthService
from core.services.log_service import LogService
from core.services.scooter_service import ScooterService
from core.services.backup_service import BackupService

from core.models.user_model import User, UserModel
from core.models.traveller_model import TravellerModel

from core.utils.validators import ValidationError, InputValidator

# Include the rest of the original code below this (assumed already working)
class UrbanMobilityApp:
    """Main application class"""
    
    def __init__(self):
        self.running = True
        self.auth = AuthService()
    
    def run(self):
        """Main application loop"""
        try:
            # Initialize database
            print("Initializing database...")
            initialize_database()
            
            # Clear screen and show welcome
            self.auth.clear_screen()
            self.show_welcome()
            
            # Login loop
            user = self.auth.login_user()
            if not user:
                print("Exiting...")
                return
            
            # Main application loop
            while self.running:
                try:
                    self.show_main_menu(user)
                    choice = input("\nSelect option: ").strip()
                    
                    if not self.handle_main_menu_choice(user, choice):
                        break
                        
                except KeyboardInterrupt:
                    print("\n\nOperation cancelled.")
                    if self.confirm_exit():
                        break
                except Exception as e:
                    print(f"\n❌ Unexpected error: {e}")
                    LogService.log_suspicious_activity(user.username, f"Unexpected error: {str(e)}")
                    self.auth.pause()
            
        except Exception as e:
            print(f"Critical error: {e}")
            LogService.log_suspicious_activity(None, f"Critical application error: {str(e)}")
        
        finally:
            self.cleanup()
    
    def show_welcome(self):
        """Show welcome screen"""
        print("="*60)
        print("   🛴 URBAN MOBILITY BACKEND SYSTEM 🛴")
        print("="*60)
        print("   Secure Admin Interface v1.0")
        print("   Final Assignment - Software Quality")
        print("="*60)
    
    def show_main_menu(self, user: User):
        """Show role-based main menu"""
        self.auth.clear_screen()
        print(f"🏠 Main Menu - Welcome {user.first_name} {user.last_name}")
        print(f"Role: {user.role.replace('_', ' ').title()}")
        print("="*50)
        print("Enter the number of the option you want to select and press Enter.")

        menu_options = []
        # Common options for all roles
        if user.username != 'super_admin':
            menu_options.append(("🔐 Change Password", self.auth.change_password))
        # Scooter management (all roles)
        menu_options.append(("🛴 View Scooters", lambda: ScooterService.list_scooters(user)))
        menu_options.append(("🔍 Search Scooters", lambda: ScooterService.search_scooters(user)))
        menu_options.append(("📝 Update Scooter", lambda: ScooterService.update_scooter_interactive(user)))
        if user.role in ['super_admin', 'system_admin']:
            menu_options.append(("➕ Add New Scooter", lambda: ScooterService.create_scooter_interactive(user)))
            menu_options.append(("❌ Delete Scooter", lambda: ScooterService.delete_scooter_interactive(user)))
            menu_options.append(("👥 User Management", lambda: self.user_management_menu(user)))
            menu_options.append(("🚶 Traveller Management", lambda: self.traveller_management_menu(user)))
            menu_options.append(("📊 View System Logs", lambda: self.show_system_logs(user)))
            menu_options.append(("💾 Backup & Restore", lambda: self.backup_restore_menu(user)))
        for idx, (label, _) in enumerate(menu_options, 1):
            print(f"{idx}. {label}")
        print("0. 🚪 Logout")

        # Store for use in handle_main_menu_choice
        self._menu_options = menu_options

    def handle_main_menu_choice(self, user: User, choice: str) -> bool:
        """Handle main menu selection"""
        try:
            if choice == '0':
                if self.confirm_exit():
                    return False
                return True
            try:
                idx = int(choice)
            except ValueError:
                print("❌ Invalid option or insufficient permissions")
                self.auth.pause()
                return True
            if 1 <= idx <= len(self._menu_options):
                action = self._menu_options[idx-1][1]
                action()
                self.auth.pause()
            else:
                print("❌ Invalid option or insufficient permissions")
                self.auth.pause()
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
            return True
    
    def user_management_menu(self, user: User):
        """User management submenu"""
        while True:
            self.auth.clear_screen()
            print("👥 User Management")
            print("="*30)
            print("1. 📋 List All Users")
            print("2. ➕ Add New User")
            print("3. 📝 Update User Profile")
            print("4. 🔄 Reset User Password")
            print("5. ❌ Delete User")
            print("0. 🔙 Back to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.list_users(user)
            elif choice == '2':
                self.add_user(user)
            elif choice == '3':
                self.update_user_profile(user)
            elif choice == '4':
                self.reset_user_password(user)
            elif choice == '5':
                self.delete_user(user)
            elif choice == '0':
                break
            else:
                print("❌ Invalid option")
                self.auth.pause()
    
    def traveller_management_menu(self, user: User):
        """Traveller management submenu"""
        while True:
            self.auth.clear_screen()
            print("🚶 Traveller Management")
            print("="*30)
            print("1. 📋 List All Travellers")
            print("2. 🔍 Search Travellers")
            print("3. ➕ Add New Traveller")
            print("4. 📝 Update Traveller")
            print("5. 👁️ View Traveller Details")
            print("6. ❌ Delete Traveller")
            print("0. 🔙 Back to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.list_travellers(user)
            elif choice == '2':
                self.search_travellers(user)
            elif choice == '3':
                self.add_traveller(user)
            elif choice == '4':
                self.update_traveller(user)
            elif choice == '5':
                self.view_traveller_details(user)
            elif choice == '6':
                self.delete_traveller(user)
            elif choice == '0':
                break
            else:
                print("❌ Invalid option")
                self.auth.pause()
    
    def backup_restore_menu(self, user: User):
        """Backup and restore submenu"""
        while True:
            self.auth.clear_screen()
            print("💾 Backup & Restore")
            print("="*30)
            print("1. 📋 List Backups")
            print("2. ➕ Create Backup")
            
            if user.role == 'super_admin':
                print("3. 🔄 Restore Backup (Super Admin)")
                print("4. 🔑 Generate Restore Code")
                print("5. 📋 List Restore Codes")
                print("6. ❌ Revoke Restore Code")
            else:
                print("3. 🔄 Restore with Code")
            
            print("0. 🔙 Back to Main Menu")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.list_backups(user)
            elif choice == '2':
                self.create_backup(user)
            elif choice == '3':
                if user.role == 'super_admin':
                    self.restore_backup_super_admin(user)
                else:
                    self.restore_with_code(user)
            elif choice == '4' and user.role == 'super_admin':
                self.generate_restore_code(user)
            elif choice == '5' and user.role == 'super_admin':
                self.list_restore_codes(user)
            elif choice == '6' and user.role == 'super_admin':
                self.revoke_restore_code(user)
            elif choice == '0':
                break
            else:
                print("❌ Invalid option")
                self.auth.pause()
    
    # User Management Methods
    def list_users(self, user: User):
        """List all users"""
        try:
            users = UserModel.get_all_users(user)
            
            if not users:
                print("No users found.")
                self.auth.pause()
                return
            
            print(f"\n--- Users List ({len(users)} total) ---")
            print(f"{'ID':<5} {'Username':<12} {'Role':<15} {'Name':<25} {'Registered':<12}")
            print("-" * 75)
            
            for u in users:
                role_display = u.role.replace('_', ' ').title()
                name = f"{u.first_name} {u.last_name}"
                reg_date = u.registration_date[:10] if u.registration_date else "N/A"
                print(f"{u.id:<5} {u.username:<12} {role_display:<15} {name:<25} {reg_date:<12}")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            traceback.print_exc()
            self.auth.pause()
    
    def add_user(self, user: User):
        """Add new user"""
        try:
            print("\n--- Add New User ---")
            print("\nUsername requirements:")
            print("- Must be unique and have a length of at least 8 characters")
            print("- Must be no longer than 10 characters")
            print("- Must be started with a letter or underscore (_)")
            print("- Can contain letters (a-z), numbers (0-9), underscores (_), apostrophes ('), and periods (.)")
            print("- No distinction between lowercase and uppercase letters (case-insensitive)")
            print("")
            print("Password requirements:")
            print("- Must have a length of at least 12 characters")
            print("- Must be no longer than 30 characters")
            print("- Can contain letters (a-z), (A-Z), numbers (0-9), Special characters such as ~!@#$%&_-+=`|\\(){}[]:;'\"<>,.?/")
            print("- Must have a combination of at least one lowercase letter, one uppercase letter, one digit, and one special character")
            print("")
            # Username input and validation
            while True:
                username = input("Username (8-10 chars): ").strip()
                try:
                    InputValidator.validate_username(username)
                    # Check uniqueness
                    if UserModel.username_exists(username):
                        print("❌ Username already exists. Please choose another.")
                        continue
                    break
                except ValidationError as e:
                    print(f"❌ {e}")
            # Password input and validation
            while True:
                password = input("Password (12-30 chars): ").strip()
                try:
                    InputValidator.validate_password(password)
                    break
                except ValidationError as e:
                    print(f"❌ {e}")
            print("Available roles:")
            if user.role == 'super_admin':
                print("1. System Administrator")
                print("2. Service Engineer")
                role_choice = input("Select role (1-2): ").strip()
                role = 'system_admin' if role_choice == '1' else 'service_engineer'
            else:
                print("1. Service Engineer")
                role_choice = input("Select role (1): ").strip()
                role = 'service_engineer'
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()
            if UserModel.create_user(user, username, password, role, first_name, last_name):
                print("✅ User created successfully!")
            else:
                print("❌ Failed to create user")
            self.auth.pause()
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
            self.auth.pause()
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def update_user_profile(self, user: User):
        """Update user profile by selecting from a list of users (by ID, no username prompt)"""
        try:
            users = UserModel.get_all_users(user)
            if not users:
                print("No users found.")
                self.auth.pause()
                return
            print(f"\n--- Users List ({len(users)} total) ---")
            print(f"{'ID':<5} {'Username':<12} {'Role':<15} {'Name':<25} {'Registered':<12}")
            print("-" * 75)
            for u in users:
                role_display = u.role.replace('_', ' ').title()
                name = f"{u.first_name} {u.last_name}"
                reg_date = u.registration_date[:10] if u.registration_date else "N/A"
                print(f"{u.id:<5} {u.username:<12} {role_display:<15} {name:<25} {reg_date:<12}")
            user_id_input = input("\nEnter the ID of the user to update: ").strip()
            try:
                user_id = int(user_id_input)
            except ValueError:
                print("❌ Invalid user ID.")
                self.auth.pause()
                return
            target_user = next((u for u in users if u.id == user_id), None)
            if not target_user:
                print(f"❌ No user found with ID {user_id}.")
                self.auth.pause()
                return
            print(f"Updating user: {target_user.username} ({target_user.first_name} {target_user.last_name})")
            first_name = input(f"New First Name [{target_user.first_name}]: ").strip() or target_user.first_name
            last_name = input(f"New Last Name [{target_user.last_name}]: ").strip() or target_user.last_name
            if first_name == target_user.first_name and last_name == target_user.last_name:
                print("No changes detected. Profile not updated.")
            else:
                try:
                    result = UserModel.update_user_profile_by_id(user, user_id, first_name, last_name)
                    if result:
                        print("✅ Profile updated successfully!")
                    else:
                        print("❌ Update failed (database error or insufficient permissions)")
                except Exception as update_exc:
                    print(f"❌ Update failed with error: {update_exc}")
                    traceback.print_exc()
            self.auth.pause()
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def reset_user_password(self, user: User):
        """Reset user password by selecting from a list of users (by ID)"""
        try:
            users = UserModel.get_all_users(user)
            if not users:
                print("No users found.")
                self.auth.pause()
                return
            print(f"\n--- Users List ({len(users)} total) ---")
            print(f"{'ID':<5} {'Username':<12} {'Role':<15} {'Name':<25} {'Registered':<12}")
            print("-" * 75)
            for u in users:
                role_display = u.role.replace('_', ' ').title()
                name = f"{u.first_name} {u.last_name}"
                reg_date = u.registration_date[:10] if u.registration_date else "N/A"
                print(f"{u.id:<5} {u.username:<12} {role_display:<15} {name:<25} {reg_date:<12}")
            user_id_input = input("\nEnter the ID of the user to reset password: ").strip()
            try:
                user_id = int(user_id_input)
            except ValueError:
                print("❌ Invalid user ID.")
                self.auth.pause()
                return
            target_user = next((u for u in users if u.id == user_id), None)
            if not target_user:
                print(f"❌ No user found with ID {user_id}.")
                self.auth.pause()
                return
            print(f"Resetting password for user: {target_user.username} ({target_user.first_name} {target_user.last_name})")
            new_password = input("New password: ").strip()
            try:
                result = UserModel.reset_user_password_by_id(user, user_id, new_password)
                if result:
                    print("✅ Password reset successfully!")
                else:
                    print("❌ Failed to reset password (database error or insufficient permissions)")
            except Exception as reset_exc:
                print(f"❌ Password reset failed with error: {reset_exc}")
                traceback.print_exc()
            self.auth.pause()
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def delete_user(self, user: User):
        """Delete user by selecting from a list of users"""
        try:
            users = UserModel.get_all_users(user)
            if not users:
                print("No users found.")
                self.auth.pause()
                return
            print(f"\n--- Users List ({len(users)} total) ---")
            print(f"{'ID':<5} {'Username':<12} {'Role':<15} {'Name':<25} {'Registered':<12}")
            print("-" * 75)
            for u in users:
                role_display = u.role.replace('_', ' ').title()
                name = f"{u.first_name} {u.last_name}"
                reg_date = u.registration_date[:10] if u.registration_date else "N/A"
                print(f"{u.id:<5} {u.username:<12} {role_display:<15} {name:<25} {reg_date:<12}")
            user_id_input = input("\nEnter the ID of the user to delete: ").strip()
            try:
                user_id = int(user_id_input)
            except ValueError:
                print("❌ Invalid user ID.")
                self.auth.pause()
                return
            target_user = next((u for u in users if u.id == user_id), None)
            if not target_user:
                print(f"❌ No user found with ID {user_id}.")
                self.auth.pause()
                return
            if target_user.username == 'super_admin':
                print("❌ Cannot delete super admin.")
                self.auth.pause()
                return
            if not self.auth.confirm_action(f"Delete user '{target_user.username}' ({target_user.first_name} {target_user.last_name})?"):
                print("Cancelled.")
                self.auth.pause()
                return
            try:
                result = UserModel.delete_user_by_id(user, user_id)
                if result:
                    print("✅ User deleted successfully!")
                else:
                    print("❌ Failed to delete user (database error or insufficient permissions)")
            except Exception as delete_exc:
                print(f"❌ Delete failed with error: {delete_exc}")
                traceback.print_exc()
            self.auth.pause()
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    # Traveller Management Methods
    def list_travellers(self, user: User):
        """List all travellers"""
        try:
            travellers = TravellerModel.get_all_travellers(user.username)
            
            if not travellers:
                print("No travellers found.")
                self.auth.pause()
                return
            
            print(f"\n--- Travellers List ({len(travellers)} total) ---")
            print(f"{'ID':<5} {'Name':<25} {'Email':<25} {'Phone':<15} {'City':<12}")
            print("-" * 85)
            
            for t in travellers:
                name = f"{t.first_name} {t.last_name}"
                print(f"{t.id:<5} {name:<25} {t.email:<25} {t.mobile_phone:<15} {t.city:<12}")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def search_travellers(self, user: User):
        """Search travellers"""
        try:
            search_term = input("Enter search term: ").strip()
            travellers = TravellerModel.search_travellers(user.username, search_term)
            
            if not travellers:
                print("No travellers found.")
                self.auth.pause()
                return
            
            print(f"\n--- Search Results ({len(travellers)} found) ---")
            print(f"{'ID':<5} {'Name':<25} {'Email':<25} {'Phone':<15}")
            print("-" * 75)
            
            for t in travellers:
                name = f"{t.first_name} {t.last_name}"
                print(f"{t.id:<5} {name:<25} {t.email:<25} {t.mobile_phone:<15}")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def add_traveller(self, user: User):
        """Add new traveller"""
        try:
            print("\n--- Add New Traveller ---")
            print("Predefined cities: Rotterdam, Amsterdam, The Hague, Utrecht, Eindhoven, Groningen, Tilburg, Almere, Breda, Nijmegen")
            
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()
            birthday = input("Birthday (YYYY-MM-DD): ").strip()
            gender = input("Gender (male/female): ").strip()
            street_name = input("Street Name: ").strip()
            house_number = input("House Number: ").strip()
            zip_code = input("Zip Code (DDDDXX): ").strip()
            city = input("City: ").strip()
            email = input("Email: ").strip()
            mobile_phone = input("Mobile Phone (8 digits): ").strip()
            driving_license = input("Driving License (XXDDDDDDD): ").strip()
            
            if TravellerModel.create_traveller(
                user.username, first_name, last_name, birthday, gender,
                street_name, house_number, zip_code, city, email,
                mobile_phone, driving_license
            ):
                print("✅ Traveller created successfully!")
            else:
                print("❌ Failed to create traveller")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def update_traveller(self, user: User):
        """Update traveller"""
        try:
            traveller_id = input("Traveller ID to update: ").strip()
            
            try:
                traveller_id = int(traveller_id)
            except ValueError:
                print("❌ Invalid Traveller ID")
                self.auth.pause()
                return
            
            # Get current traveller
            traveller = TravellerModel.get_traveller_by_id(user.username, traveller_id)
            if not traveller:
                print("❌ Traveller not found")
                self.auth.pause()
                return
            
            print(f"\n--- Update Traveller (ID: {traveller.id}) ---")
            print("Leave blank to keep current value")
            
            updates = {}
            
            first_name = input(f"First Name [{traveller.first_name}]: ").strip()
            if first_name: updates['first_name'] = first_name
            
            last_name = input(f"Last Name [{traveller.last_name}]: ").strip()
            if last_name: updates['last_name'] = last_name
            
            email = input(f"Email [{traveller.email}]: ").strip()
            if email: updates['email'] = email
            
            mobile_phone = input(f"Mobile Phone [{traveller.mobile_phone}]: ").strip()
            if mobile_phone: updates['mobile_phone'] = mobile_phone
            
            city = input(f"City [{traveller.city}]: ").strip()
            if city: updates['city'] = city
            
            if updates and TravellerModel.update_traveller(user.username, traveller_id, **updates):
                print("✅ Traveller updated successfully!")
            else:
                print("❌ No updates made or update failed")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def view_traveller_details(self, user: User):
        """View traveller details"""
        try:
            traveller_id = input("Traveller ID: ").strip()
            
            try:
                traveller_id = int(traveller_id)
            except ValueError:
                print("❌ Invalid Traveller ID")
                self.auth.pause()
                return
            
            traveller = TravellerModel.get_traveller_by_id(user.username, traveller_id)
            if not traveller:
                print("❌ Traveller not found")
                self.auth.pause()
                return
            
            print(f"\n--- Traveller Details (ID: {traveller.id}) ---")
            print(f"Name: {traveller.first_name} {traveller.last_name}")
            print(f"Birthday: {traveller.birthday}")
            print(f"Gender: {traveller.gender}")
            print(f"Address: {traveller.house_number} {traveller.street_name}, {traveller.zip_code} {traveller.city}")
            print(f"Email: {traveller.email}")
            print(f"Phone: {traveller.mobile_phone}")
            print(f"Driving License: {traveller.driving_license_number}")
            print(f"Registered: {traveller.registration_date}")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def delete_traveller(self, user: User):
        """Delete traveller"""
        try:
            traveller_id = input("Traveller ID to delete: ").strip()
            
            try:
                traveller_id = int(traveller_id)
            except ValueError:
                print("❌ Invalid Traveller ID")
                self.auth.pause()
                return
            
            if self.auth.confirm_action(f"Delete traveller ID {traveller_id}?"):
                if TravellerModel.delete_traveller(user.username, traveller_id):
                    print("✅ Traveller deleted successfully!")
                else:
                    print("❌ Failed to delete traveller")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    # System Management Methods
    def show_system_logs(self, user: User):
        """Show system logs"""
        try:
            logs = LogService.get_logs_for_admin(user.username)
            
            if not logs:
                print("No logs found.")
                return
            
            print(f"\n--- System Logs ({len(logs)} entries) ---")
            print("Recent entries first:")
            print("-" * 100)
            
            for i, log in enumerate(logs[:20]):  # Show first 20 entries
                status = "🚨 SUSPICIOUS" if log['suspicious'] else "✅ Normal"
                print(f"{log['date']} {log['time']} | {log['username']:<12} | {status}")
                print(f"    {log['description']}")
                if log['additional_info']:
                    print(f"    Additional: {log['additional_info']}")
                print("-" * 100)
            
            if len(logs) > 20:
                print(f"... and {len(logs) - 20} more entries")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Backup Methods
    def list_backups(self, user: User):
        """List all backups"""
        try:
            backups = BackupService.list_backups(user)
            
            if not backups:
                print("No backups found.")
                self.auth.pause()
                return
            
            print(f"\n--- Backups List ({len(backups)} total) ---")
            print(f"{'Filename':<30} {'Size':<10} {'Modified':<20}")
            print("-" * 65)
            
            for backup in backups:
                size = BackupService.format_file_size(backup['size'])
                print(f"{backup['filename']:<30} {size:<10} {backup['modified']:<20}")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def create_backup(self, user: User):
        """Create new backup"""
        try:
            backup_name = input("Backup name (optional): ").strip()
            backup_name = backup_name if backup_name else None
            
            print("Creating backup...")
            filename = BackupService.create_backup(user, backup_name)
            print(f"✅ Backup created: {filename}")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def restore_backup_super_admin(self, user: User):
        """Restore backup (Super Admin)"""
        try:
            backups = BackupService.list_backups(user)
            if not backups:
                print("No backups available.")
                self.auth.pause()
                return
            
            print("\nAvailable backups:")
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup['filename']} ({backup['modified']})")
            
            choice = input("\nSelect backup number: ").strip()
            try:
                choice_idx = int(choice) - 1
                selected_backup = backups[choice_idx]['filename']
            except (ValueError, IndexError):
                print("❌ Invalid selection")
                self.auth.pause()
                return
            
            if self.auth.confirm_action(f"Restore backup '{selected_backup}'? This will overwrite current data"):
                if BackupService.restore_backup_super_admin(user, selected_backup):
                    print("✅ Backup restored successfully!")
                    print("⚠️  Please restart the application to use restored data.")
                else:
                    print("❌ Failed to restore backup")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def generate_restore_code(self, user: User):
        """Generate restore code"""
        try:
            # List backups
            backups = BackupService.list_backups(user)
            if not backups:
                print("No backups available.")
                self.auth.pause()
                return
            
            print("\nAvailable backups:")
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup['filename']}")
            
            backup_choice = input("\nSelect backup number: ").strip()
            try:
                backup_idx = int(backup_choice) - 1
                selected_backup = backups[backup_idx]['filename']
            except (ValueError, IndexError):
                print("❌ Invalid backup selection")
                self.auth.pause()
                return
            
            system_admin = input("System Admin username: ").strip()
            
            restore_code = BackupService.generate_restore_code(user, selected_backup, system_admin)
            
            print(f"\n✅ Restore code generated successfully!")
            print(f"Code: {restore_code}")
            print(f"For: {system_admin}")
            print(f"Backup: {selected_backup}")
            print("\n⚠️  This code is one-time use only. Share it securely.")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def restore_with_code(self, user: User):
        """Restore with code (System Admin)"""
        try:
            restore_code = input("Enter restore code: ").strip()
            
            if self.auth.confirm_action("Restore backup with this code? This will overwrite current data"):
                if BackupService.restore_with_code(user, restore_code):
                    print("✅ Backup restored successfully!")
                    print("⚠️  Please restart the application to use restored data.")
                else:
                    print("❌ Failed to restore backup")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def list_restore_codes(self, user: User):
        """List restore codes"""
        try:
            codes = BackupService.list_restore_codes(user)
            
            if not codes:
                print("No restore codes found.")
                self.auth.pause()
                return
            
            print(f"\n--- Restore Codes ({len(codes)} total) ---")
            print(f"{'Code':<12} {'Admin':<15} {'Backup':<25} {'Used':<6} {'Created':<12}")
            print("-" * 75)
            
            for code in codes:
                used_status = "Yes" if code['used'] else "No"
                created_date = code['created_at'][:10]
                print(f"{code['code']:<12} {code['system_admin_username']:<15} "
                      f"{code['backup_filename']:<25} {used_status:<6} {created_date:<12}")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def revoke_restore_code(self, user: User):
        """Revoke restore code"""
        try:
            restore_code = input("Enter restore code to revoke: ").strip()
            
            if self.auth.confirm_action("Revoke this restore code?"):
                if BackupService.revoke_restore_code(user, restore_code):
                    print("✅ Restore code revoked successfully!")
                else:
                    print("❌ Failed to revoke code (may not exist or already used)")
            
            self.auth.pause()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.auth.pause()
    
    def confirm_exit(self) -> bool:
        """Confirm application exit"""
        return self.auth.confirm_action("Are you sure you want to exit?")
    
    def cleanup(self):
        """Cleanup on exit"""
        if hasattr(self.auth, 'current_user') and self.auth.current_user:
            self.auth.logout_user()
        print("System shutdown complete.")

def main():
    """Main entry point"""
    app = UrbanMobilityApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
    except Exception as e:
        print(f"Critical error: {e}")
        LogService.log_suspicious_activity(None, f"Critical main error: {str(e)}")
    finally:
        print("Goodbye!")

if __name__ == "__main__":
    main()
