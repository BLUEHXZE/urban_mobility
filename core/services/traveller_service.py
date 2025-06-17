from typing import List, Optional
from core.models.traveller_model import Traveller, TravellerModel
from core.models.user_model import User
from core.services.log_service import LogService
from core.utils.validators import ValidationError, InputValidator

class TravellerService:
    """Service for traveller operations with proper authorization"""
    
    @staticmethod
    def create_traveller_interactive(user: User) -> bool:
        """Interactive traveller creation"""
        if user.role not in ['super_admin', 'system_admin']:
            print("❌ Only Super Admin and System Admin can create travellers")
            return False
        
        try:
            print("\n--- Add New Traveller ---")
            
            first_name = input("First Name: ").strip()
            last_name = input("Last Name: ").strip()
            birthday = input("Birthday (YYYY-MM-DD): ").strip()
            
            print("Gender options: male, female")
            gender = input("Gender: ").strip().lower()
            
            street_name = input("Street Name: ").strip()
            house_number = input("House Number: ").strip()
            zip_code = input("Zip Code (DDDDXX format): ").strip()
            
            print("Available cities:")
            cities = ["Rotterdam", "Amsterdam", "The Hague", "Utrecht", "Eindhoven",
                     "Groningen", "Tilburg", "Almere", "Breda", "Nijmegen"]
            for i, city in enumerate(cities, 1):
                print(f"  {i}. {city}")
            
            city_choice = input("Select city (1-10) or enter name: ").strip()
            if city_choice.isdigit() and 1 <= int(city_choice) <= 10:
                city = cities[int(city_choice) - 1]
            else:
                city = city_choice
            
            email = input("Email Address: ").strip()
            mobile_phone = input("Mobile Phone (8 digits only): ").strip()
            driving_license = input("Driving License Number: ").strip()
            
            if TravellerModel.create_traveller(
                user.username, first_name, last_name, birthday, gender,
                street_name, house_number, zip_code, city, email,
                mobile_phone, driving_license
            ):
                print("✅ Traveller created successfully!")
                return True
            else:
                print("❌ Failed to create traveller")
                return False
                
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return False
    
    @staticmethod
    def list_travellers(user: User) -> List[Traveller]:
        """List all travellers"""
        if user.role not in ['super_admin', 'system_admin']:
            print("❌ Only Super Admin and System Admin can view travellers")
            return []
        
        try:
            travellers = TravellerModel.get_all_travellers(user.username)
            
            if not travellers:
                print("No travellers found.")
                return []
            
            print(f"\n--- Travellers List ({len(travellers)} total) ---")
            print(f"{'ID':<5} {'Name':<25} {'Email':<25} {'City':<15} {'License':<12}")
            print("-" * 85)
            
            for traveller in travellers:
                name = f"{traveller.first_name} {traveller.last_name}"
                print(f"{traveller.id:<5} {name:<25} {traveller.email:<25} "
                      f"{traveller.city:<15} {traveller.driving_license_number:<12}")
            
            return travellers
            
        except Exception as e:
            print(f"❌ Error listing travellers: {e}")
            return []
    
    @staticmethod
    def search_travellers(user: User) -> List[Traveller]:
        """Interactive traveller search"""
        if user.role not in ['super_admin', 'system_admin']:
            print("❌ Only Super Admin and System Admin can search travellers")
            return []
        
        try:
            search_term = input("\nEnter search term (name, email, phone, license, or ID): ").strip()
            
            if not search_term:
                print("❌ Search term cannot be empty")
                return []
            
            travellers = TravellerModel.search_travellers(user.username, search_term)
            
            if not travellers:
                print("No travellers found matching the search term.")
                return []
            
            print(f"\n--- Search Results ({len(travellers)} found) ---")
            print(f"{'ID':<5} {'Name':<25} {'Email':<25} {'Phone':<15}")
            print("-" * 75)
            
            for traveller in travellers:
                name = f"{traveller.first_name} {traveller.last_name}"
                print(f"{traveller.id:<5} {name:<25} {traveller.email:<25} {traveller.mobile_phone:<15}")
            
            return travellers
            
        except Exception as e:
            print(f"❌ Error searching travellers: {e}")
            return []
    
    @staticmethod
    def view_traveller_details(user: User, traveller_id: int = None) -> Optional[Traveller]:
        """View detailed traveller information"""
        if user.role not in ['super_admin', 'system_admin']:
            print("❌ Only Super Admin and System Admin can view traveller details")
            return None
        
        try:
            if traveller_id is None:
                traveller_id_str = input("Enter Traveller ID: ").strip()
                try:
                    traveller_id = int(traveller_id_str)
                except ValueError:
                    print("❌ Invalid Traveller ID")
                    return None
            
            traveller = TravellerModel.get_traveller_by_id(user.username, traveller_id)
            
            if not traveller:
                print("❌ Traveller not found")
                return None
            
            print(f"\n--- Traveller Details (ID: {traveller.id}) ---")
            print(f"Name: {traveller.first_name} {traveller.last_name}")
            print(f"Birthday: {traveller.birthday}")
            print(f"Gender: {traveller.gender.title()}")
            print(f"Address: {traveller.street_name} {traveller.house_number}")
            print(f"         {traveller.zip_code} {traveller.city}")
            print(f"Email: {traveller.email}")
            print(f"Phone: {traveller.mobile_phone}")
            print(f"Driving License: {traveller.driving_license_number}")
            print(f"Registration Date: {traveller.registration_date}")
            
            return traveller
            
        except Exception as e:
            print(f"❌ Error viewing traveller: {e}")
            return None
    
    @staticmethod
    def update_traveller_interactive(user: User) -> bool:
        """Interactive traveller update"""
        if user.role not in ['super_admin', 'system_admin']:
            print("❌ Only Super Admin and System Admin can update travellers")
            return False
        
        try:
            traveller_id_str = input("Enter Traveller ID to update: ").strip()
            try:
                traveller_id = int(traveller_id_str)
            except ValueError:
                print("❌ Invalid Traveller ID")
                return False
            
            # Get current traveller
            traveller = TravellerModel.get_traveller_by_id(user.username, traveller_id)
            if not traveller:
                print("❌ Traveller not found")
                return False
            
            print(f"\n--- Update Traveller (ID: {traveller.id}) ---")
            print("Leave blank to keep current value")
            
            updates = {}
            
            first_name = input(f"First Name [{traveller.first_name}]: ").strip()
            if first_name: updates['first_name'] = first_name
            
            last_name = input(f"Last Name [{traveller.last_name}]: ").strip()
            if last_name: updates['last_name'] = last_name
            
            birthday = input(f"Birthday [{traveller.birthday}]: ").strip()
            if birthday: updates['birthday'] = birthday
            
            gender = input(f"Gender [{traveller.gender}] (male/female): ").strip()
            if gender: updates['gender'] = gender
            
            street_name = input(f"Street Name [{traveller.street_name}]: ").strip()
            if street_name: updates['street_name'] = street_name
            
            house_number = input(f"House Number [{traveller.house_number}]: ").strip()
            if house_number: updates['house_number'] = house_number
            
            zip_code = input(f"Zip Code [{traveller.zip_code}]: ").strip()
            if zip_code: updates['zip_code'] = zip_code
            
            city = input(f"City [{traveller.city}]: ").strip()
            if city: updates['city'] = city
            
            email = input(f"Email [{traveller.email}]: ").strip()
            if email: updates['email'] = email
            
            mobile_phone = input(f"Mobile Phone [{traveller.mobile_phone}] (8 digits): ").strip()
            if mobile_phone: updates['mobile_phone'] = mobile_phone
            
            driving_license = input(f"Driving License [{traveller.driving_license_number}]: ").strip()
            if driving_license: updates['driving_license_number'] = driving_license
            
            if not updates:
                print("No changes made.")
                return False
            
            if TravellerModel.update_traveller(user.username, traveller_id, **updates):
                print("✅ Traveller updated successfully!")
                return True
            else:
                print("❌ Failed to update traveller")
                return False
                
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return False
    
    @staticmethod
    def delete_traveller_interactive(user: User) -> bool:
        """Interactive traveller deletion"""
        if user.role not in ['super_admin', 'system_admin']:
            print("❌ Only Super Admin and System Admin can delete travellers")
            return False
        
        try:
            traveller_id_str = input("Enter Traveller ID to delete: ").strip()
            try:
                traveller_id = int(traveller_id_str)
            except ValueError:
                print("❌ Invalid Traveller ID")
                return False
            
            # Show traveller details first
            traveller = TravellerModel.get_traveller_by_id(user.username, traveller_id)
            if not traveller:
                print("❌ Traveller not found")
                return False
            
            print(f"\n--- Traveller to Delete ---")
            print(f"ID: {traveller.id}")
            print(f"Name: {traveller.first_name} {traveller.last_name}")
            print(f"Email: {traveller.email}")
            print(f"License: {traveller.driving_license_number}")
            
            # Confirm deletion
            confirm = input("\nAre you sure you want to delete this traveller? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("Deletion cancelled.")
                return False
            
            if TravellerModel.delete_traveller(user.username, traveller_id):
                print("✅ Traveller deleted successfully!")
                return True
            else:
                print("❌ Failed to delete traveller")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
