from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from core.db.dbconn import db
from security import encrypt_data, decrypt_data
from core.services.log_service import LogService
from core.utils.validators import InputValidator, ValidationError

@dataclass
class Traveller:
    id: int
    first_name: str
    last_name: str
    birthday: str
    gender: str
    street_name: str
    house_number: str
    zip_code: str
    city: str
    email: str
    mobile_phone: str
    driving_license_number: str
    registration_date: str

class TravellerModel:
    """Traveller model with secure operations"""
    
    @staticmethod
    def create_traveller(admin_username: str, first_name: str, last_name: str, 
                        birthday: str, gender: str, street_name: str, house_number: str,
                        zip_code: str, city: str, email: str, mobile_phone: str,
                        driving_license_number: str) -> bool:
        """Create new traveller record"""
        try:
            # Validate all inputs
            first_name = InputValidator.validate_name(first_name, "First name")
            last_name = InputValidator.validate_name(last_name, "Last name")
            birthday = InputValidator.validate_date(birthday, "Birthday")
            
            if gender.lower() not in ['male', 'female']:
                raise ValidationError("Gender must be 'male' or 'female'")
            gender = gender.lower()
            
            street_name = InputValidator.validate_name(street_name, "Street name")
            house_number = InputValidator.sanitize_input(house_number)
            zip_code = InputValidator.validate_zip_code(zip_code)
            city = InputValidator.validate_city(city)
            email = InputValidator.validate_email(email)
            mobile_phone = InputValidator.validate_phone(mobile_phone)
            driving_license_number = InputValidator.validate_driving_license(driving_license_number)
            
            # Check for duplicate driving license
            encrypted_license = encrypt_data(driving_license_number)
            existing_query = "SELECT COUNT(*) FROM travellers WHERE driving_license_number = ?"
            if db.execute_scalar(existing_query, (encrypted_license,)) > 0:
                raise ValidationError("Driving license number already exists")
            
            # Encrypt sensitive data
            encrypted_first_name = encrypt_data(first_name)
            encrypted_last_name = encrypt_data(last_name)
            encrypted_street_name = encrypt_data(street_name)
            encrypted_house_number = encrypt_data(house_number)
            encrypted_email = encrypt_data(email)
            encrypted_phone = encrypt_data(mobile_phone)
            
            registration_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            query = """
            INSERT INTO travellers (first_name, last_name, birthday, gender, street_name, 
                                  house_number, zip_code, city, email, mobile_phone, 
                                  driving_license_number, registration_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            db.execute_non_query(query, (
                encrypted_first_name, encrypted_last_name, birthday, gender,
                encrypted_street_name, encrypted_house_number, zip_code, city,
                encrypted_email, encrypted_phone, encrypted_license, registration_date
            ))
            
            LogService.log_data_operation(admin_username, "CREATE", "travellers")
            return True
            
        except Exception as e:
            LogService.log_suspicious_activity(admin_username, f"Traveller creation failed: {str(e)}")
            raise e
    
    @staticmethod
    def get_all_travellers(admin_username: str) -> List[Traveller]:
        """Get all travellers with decrypted data"""
        try:
            query = "SELECT * FROM travellers ORDER BY registration_date DESC"
            results = db.execute_query(query)
            
            travellers = []
            for result in results:
                traveller = Traveller(
                    id=result[0],
                    first_name=decrypt_data(result[1]),
                    last_name=decrypt_data(result[2]),
                    birthday=result[3],
                    gender=result[4],
                    street_name=decrypt_data(result[5]),
                    house_number=decrypt_data(result[6]),
                    zip_code=result[7],
                    city=result[8],
                    email=decrypt_data(result[9]),
                    mobile_phone=decrypt_data(result[10]),
                    driving_license_number=decrypt_data(result[11]),
                    registration_date=result[12]
                )
                travellers.append(traveller)
            
            LogService.log_activity(admin_username, "Viewed travellers list")
            return travellers
            
        except Exception as e:
            LogService.log_suspicious_activity(admin_username, f"Get travellers failed: {str(e)}")
            raise e
    
    @staticmethod
    def search_travellers(admin_username: str, search_term: str) -> List[Traveller]:
        """Search travellers by partial match on name, email, phone, or license"""
        try:
            search_term = InputValidator.sanitize_input(search_term).lower()
            if len(search_term) < 2:
                raise ValidationError("Search term must be at least 2 characters")
            
            # Get all travellers and filter client-side due to encryption
            all_travellers = TravellerModel.get_all_travellers(admin_username)
            
            matching_travellers = []
            for traveller in all_travellers:
                # Search in decrypted fields
                searchable_fields = [
                    traveller.first_name.lower(),
                    traveller.last_name.lower(),
                    traveller.email.lower(),
                    traveller.mobile_phone.lower(),
                    traveller.driving_license_number.lower(),
                    str(traveller.id)
                ]
                
                if any(search_term in field for field in searchable_fields):
                    matching_travellers.append(traveller)
            
            LogService.log_activity(admin_username, f"Searched travellers: '{search_term}'")
            return matching_travellers
            
        except Exception as e:
            LogService.log_suspicious_activity(admin_username, f"Traveller search failed: {str(e)}")
            raise e
    
    @staticmethod
    def get_traveller_by_id(admin_username: str, traveller_id: int) -> Optional[Traveller]:
        """Get specific traveller by ID"""
        try:
            query = "SELECT * FROM travellers WHERE id = ?"
            result = db.execute_query(query, (traveller_id,))
            
            if not result:
                return None
            
            result = result[0]
            traveller = Traveller(
                id=result[0],
                first_name=decrypt_data(result[1]),
                last_name=decrypt_data(result[2]),
                birthday=result[3],
                gender=result[4],
                street_name=decrypt_data(result[5]),
                house_number=decrypt_data(result[6]),
                zip_code=result[7],
                city=result[8],
                email=decrypt_data(result[9]),
                mobile_phone=decrypt_data(result[10]),
                driving_license_number=decrypt_data(result[11]),
                registration_date=result[12]
            )
            
            LogService.log_activity(admin_username, f"Viewed traveller details: ID {traveller_id}")
            return traveller
            
        except Exception as e:
            LogService.log_suspicious_activity(admin_username, f"Get traveller failed: {str(e)}")
            raise e
    
    @staticmethod
    def update_traveller(admin_username: str, traveller_id: int, **updates) -> bool:
        """Update traveller information"""
        try:
            # Get current traveller
            current = TravellerModel.get_traveller_by_id(admin_username, traveller_id)
            if not current:
                raise ValidationError("Traveller not found")
            
            # Validate and encrypt updates
            encrypted_updates = {}
            
            if 'first_name' in updates:
                encrypted_updates['first_name'] = encrypt_data(
                    InputValidator.validate_name(updates['first_name'], "First name")
                )
            
            if 'last_name' in updates:
                encrypted_updates['last_name'] = encrypt_data(
                    InputValidator.validate_name(updates['last_name'], "Last name")
                )
            
            if 'birthday' in updates:
                encrypted_updates['birthday'] = InputValidator.validate_date(updates['birthday'], "Birthday")
            
            if 'gender' in updates:
                gender = updates['gender'].lower()
                if gender not in ['male', 'female']:
                    raise ValidationError("Gender must be 'male' or 'female'")
                encrypted_updates['gender'] = gender
            
            if 'street_name' in updates:
                encrypted_updates['street_name'] = encrypt_data(
                    InputValidator.validate_name(updates['street_name'], "Street name")
                )
            
            if 'house_number' in updates:
                encrypted_updates['house_number'] = encrypt_data(
                    InputValidator.sanitize_input(updates['house_number'])
                )
            
            if 'zip_code' in updates:
                encrypted_updates['zip_code'] = InputValidator.validate_zip_code(updates['zip_code'])
            
            if 'city' in updates:
                encrypted_updates['city'] = InputValidator.validate_city(updates['city'])
            
            if 'email' in updates:
                encrypted_updates['email'] = encrypt_data(
                    InputValidator.validate_email(updates['email'])
                )
            
            if 'mobile_phone' in updates:
                encrypted_updates['mobile_phone'] = encrypt_data(
                    InputValidator.validate_phone(updates['mobile_phone'])
                )
            
            if 'driving_license_number' in updates:
                new_license = InputValidator.validate_driving_license(updates['driving_license_number'])
                # Check for duplicates (excluding current record)
                encrypted_license = encrypt_data(new_license)
                duplicate_query = "SELECT COUNT(*) FROM travellers WHERE driving_license_number = ? AND id != ?"
                if db.execute_scalar(duplicate_query, (encrypted_license, traveller_id)) > 0:
                    raise ValidationError("Driving license number already exists")
                encrypted_updates['driving_license_number'] = encrypted_license
            
            if not encrypted_updates:
                raise ValidationError("No valid updates provided")
            
            # Build update query
            set_clauses = []
            values = []
            for field, value in encrypted_updates.items():
                set_clauses.append(f"{field} = ?")
                values.append(value)
            
            values.append(traveller_id)
            query = f"UPDATE travellers SET {', '.join(set_clauses)} WHERE id = ?"
            
            rows_affected = db.execute_non_query(query, tuple(values))
            
            if rows_affected > 0:
                LogService.log_data_operation(admin_username, "UPDATE", "travellers", str(traveller_id))
                return True
            
            return False
            
        except Exception as e:
            LogService.log_suspicious_activity(admin_username, f"Traveller update failed: {str(e)}")
            raise e
    
    @staticmethod
    def delete_traveller(admin_username: str, traveller_id: int) -> bool:
        """Delete traveller record"""
        try:
            query = "DELETE FROM travellers WHERE id = ?"
            rows_affected = db.execute_non_query(query, (traveller_id,))
            
            if rows_affected > 0:
                LogService.log_data_operation(admin_username, "DELETE", "travellers", str(traveller_id))
                return True
            
            return False
            
        except Exception as e:
            LogService.log_suspicious_activity(admin_username, f"Traveller deletion failed: {str(e)}")
            raise e