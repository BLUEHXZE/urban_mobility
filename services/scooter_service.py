from typing import List, Optional
from models.scooter_model import Scooter, ScooterModel
from models.user_model import User
from services.log_service import LogService
from utils.validators import ValidationError

class ScooterService:
    """Service for scooter operations with proper authorization"""
    
    @staticmethod
    def create_scooter_interactive(user: User) -> bool:
        """Interactive scooter creation"""
        if user.role not in ['super_admin', 'system_admin']:
            print("❌ Only Super Admin and System Admin can create scooters")
            return False
        
        try:
            print("\n--- Add New Scooter ---")
            
            brand = input("Brand: ").strip()
            model = input("Model: ").strip()
            serial_number = input("Serial Number (10-17 chars): ").strip()
            
            top_speed = input("Top Speed (km/h): ").strip()
            battery_capacity = input("Battery Capacity (Wh): ").strip()
            soc = input("Current State of Charge (%): ").strip()
            soc_min = input("Minimum SoC (%): ").strip()
            soc_max = input("Maximum SoC (%): ").strip()
            
            latitude = input("Latitude (5 decimal places): ").strip()
            longitude = input("Longitude (5 decimal places): ").strip()
            
            mileage = input("Current Mileage (km, default 0): ").strip() or "0"
            maintenance_date = input("Last Maintenance Date (YYYY-MM-DD, optional): ").strip()
            
            # Convert numeric inputs
            try:
                top_speed = int(top_speed)
                battery_capacity = int(battery_capacity)
                soc = int(soc)
                soc_min = int(soc_min)
                soc_max = int(soc_max)
                latitude = float(latitude)
                longitude = float(longitude)
                mileage = int(mileage)
            except ValueError:
                raise ValidationError("Invalid numeric input")
            
            maintenance_date = maintenance_date if maintenance_date else None
            
            if ScooterModel.create_scooter(
                user.username, brand, model, serial_number,
                top_speed, battery_capacity, soc, soc_min, soc_max,
                latitude, longitude, mileage, maintenance_date
            ):
                print("✅ Scooter created successfully!")
                return True
            else:
                print("❌ Failed to create scooter")
                return False
                
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return False
    
    @staticmethod
    def list_scooters(user: User) -> List[Scooter]:
        """List all scooters"""
        try:
            scooters = ScooterModel.get_all_scooters(user.username)
            
            if not scooters:
                print("No scooters found.")
                return []
            
            print(f"\n--- Scooters List ({len(scooters)} total) ---")
            print(f"{'ID':<5} {'Brand':<10} {'Model':<12} {'Serial':<15} {'SoC':<5} {'Status':<10} {'Mileage':<8}")
            print("-" * 75)
            
            for scooter in scooters:
                status = "Out of Service" if scooter.out_of_service else "In Service"
                print(f"{scooter.id:<5} {scooter.brand:<10} {scooter.model:<12} "
                      f"{scooter.serial_number:<15} {scooter.soc:<5}% {status:<10} {scooter.mileage:<8}km")
            
            return scooters
            
        except Exception as e:
            print(f"❌ Error listing scooters: {e}")
            return []
    
    @staticmethod
    def search_scooters(user: User) -> List[Scooter]:
        """Interactive scooter search"""
        try:
            search_term = input("\nEnter search term (brand, model, serial, or ID): ").strip()
            
            if not search_term:
                print("❌ Search term cannot be empty")
                return []
            
            scooters = ScooterModel.search_scooters(user.username, search_term)
            
            if not scooters:
                print("No scooters found matching the search term.")
                return []
            
            print(f"\n--- Search Results ({len(scooters)} found) ---")
            print(f"{'ID':<5} {'Brand':<10} {'Model':<12} {'Serial':<15} {'SoC':<5} {'Status':<10}")
            print("-" * 70)
            
            for scooter in scooters:
                status = "Out of Service" if scooter.out_of_service else "In Service"
                print(f"{scooter.id:<5} {scooter.brand:<10} {scooter.model:<12} "
                      f"{scooter.serial_number:<15} {scooter.soc:<5}% {status:<10}")
            
            return scooters
            
        except Exception as e:
            print(f"❌ Error searching scooters: {e}")
            return []
    
    @staticmethod
    def view_scooter_details(user: User, scooter_id: int = None) -> Optional[Scooter]:
        """View detailed scooter information"""
        try:
            if scooter_id is None:
                scooter_id_str = input("Enter Scooter ID: ").strip()
                try:
                    scooter_id = int(scooter_id_str)
                except ValueError:
                    print("❌ Invalid Scooter ID")
                    return None
            
            scooter = ScooterModel.get_scooter_by_id(user.username, scooter_id)
            
            if not scooter:
                print("❌ Scooter not found")
                return None
            
            print(f"\n--- Scooter Details (ID: {scooter.id}) ---")
            print(f"Brand: {scooter.brand}")
            print(f"Model: {scooter.model}")
            print(f"Serial Number: {scooter.serial_number}")
            print(f"Top Speed: {scooter.top_speed} km/h")
            print(f"Battery Capacity: {scooter.battery_capacity} Wh")
            print(f"State of Charge: {scooter.soc}% (Range: {scooter.soc_min}%-{scooter.soc_max}%)")
            print(f"Location: {scooter.latitude}, {scooter.longitude}")
            print(f"Status: {'Out of Service' if scooter.out_of_service else 'In Service'}")
            print(f"Mileage: {scooter.mileage} km")
            print(f"Last Maintenance: {scooter.last_maintenance_date or 'Never'}")
            print(f"In Service Since: {scooter.in_service_date}")
            
            return scooter
            
        except Exception as e:
            print(f"❌ Error viewing scooter: {e}")
            return None
    
    @staticmethod
    def update_scooter_interactive(user: User) -> bool:
        """Interactive scooter update"""
        try:
            scooter_id_str = input("Enter Scooter ID to update: ").strip()
            try:
                scooter_id = int(scooter_id_str)
            except ValueError:
                print("❌ Invalid Scooter ID")
                return False
            
            # Get current scooter
            scooter = ScooterModel.get_scooter_by_id(user.username, scooter_id)
            if not scooter:
                print("❌ Scooter not found")
                return False
            
            print(f"\n--- Update Scooter (ID: {scooter.id}) ---")
            print("Leave blank to keep current value")
            
            updates = {}
            
            # Show what fields the user can update
            if user.role in ['super_admin', 'system_admin']:
                print("(You can update all fields)")
                
                brand = input(f"Brand [{scooter.brand}]: ").strip()
                if brand: updates['brand'] = brand
                
                model = input(f"Model [{scooter.model}]: ").strip()
                if model: updates['model'] = model
                
                serial = input(f"Serial Number [{scooter.serial_number}]: ").strip()
                if serial: updates['serial_number'] = serial
                
                top_speed = input(f"Top Speed [{scooter.top_speed}]: ").strip()
                if top_speed: updates['top_speed'] = int(top_speed)
                
                battery_cap = input(f"Battery Capacity [{scooter.battery_capacity}]: ").strip()
                if battery_cap: updates['battery_capacity'] = int(battery_cap)
                
                soc_min = input(f"Min SoC [{scooter.soc_min}]: ").strip()
                if soc_min: updates['soc_min'] = int(soc_min)
                
                soc_max = input(f"Max SoC [{scooter.soc_max}]: ").strip()
                if soc_max: updates['soc_max'] = int(soc_max)
                
            else:
                print("(Service Engineers can only update: SoC, Location, Status, Mileage, Maintenance)")
            
            # Fields all roles can update (if authorized)
            soc = input(f"Current SoC [{scooter.soc}]: ").strip()
            if soc: updates['soc'] = int(soc)
            
            lat = input(f"Latitude [{scooter.latitude}]: ").strip()
            lon = input(f"Longitude [{scooter.longitude}]: ").strip()
            if lat and lon:
                updates['latitude'] = float(lat)
                updates['longitude'] = float(lon)
            elif lat or lon:
                print("❌ Both latitude and longitude must be provided together")
                return False
            
            status = input(f"Out of Service [{scooter.out_of_service}] (true/false): ").strip().lower()
            if status in ['true', 'false']:
                updates['out_of_service'] = status == 'true'
            
            mileage = input(f"Mileage [{scooter.mileage}]: ").strip()
            if mileage: updates['mileage'] = int(mileage)
            
            maintenance = input(f"Last Maintenance Date [{scooter.last_maintenance_date or 'None'}] (YYYY-MM-DD): ").strip()
            if maintenance: updates['last_maintenance_date'] = maintenance
            
            if not updates:
                print("No changes made.")
                return False
            
            if ScooterModel.update_scooter(user.username, user.role, scooter_id, **updates):
                print("✅ Scooter updated successfully!")
                return True
            else:
                print("❌ Failed to update scooter")
                return False
                
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
        except ValueError as e:
            print(f"❌ Invalid input format: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        return False
    
    @staticmethod
    def delete_scooter_interactive(user: User) -> bool:
        """Interactive scooter deletion"""
        if user.role not in ['super_admin', 'system_admin']:
            print("❌ Only Super Admin and System Admin can delete scooters")
            return False
        
        try:
            scooter_id_str = input("Enter Scooter ID to delete: ").strip()
            try:
                scooter_id = int(scooter_id_str)
            except ValueError:
                print("❌ Invalid Scooter ID")
                return False
            
            # Show scooter details first
            scooter = ScooterModel.get_scooter_by_id(user.username, scooter_id)
            if not scooter:
                print("❌ Scooter not found")
                return False
            
            print(f"\n--- Scooter to Delete ---")
            print(f"ID: {scooter.id}")
            print(f"Brand: {scooter.brand}")
            print(f"Model: {scooter.model}")
            print(f"Serial: {scooter.serial_number}")
            
            # Confirm deletion
            confirm = input("\nAre you sure you want to delete this scooter? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("Deletion cancelled.")
                return False
            
            if ScooterModel.delete_scooter(user.username, scooter_id):
                print("✅ Scooter deleted successfully!")
                return True
            else:
                print("❌ Failed to delete scooter")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False