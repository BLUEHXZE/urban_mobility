from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from db.dbconn import db
from services.log_service import LogService
from utils.validators import InputValidator, ValidationError

@dataclass
class Scooter:
    id: int
    brand: str
    model: str
    serial_number: str
    top_speed: int
    battery_capacity: int
    soc: int
    soc_min: int
    soc_max: int
    latitude: float
    longitude: float
    out_of_service: bool
    mileage: int
    last_maintenance_date: str
    in_service_date: str

class ScooterModel:
    """Scooter model with role-based access control"""
    
    @staticmethod
    def create_scooter(admin_username: str, brand: str, model: str, serial_number: str,
                      top_speed: int, battery_capacity: int, soc: int, soc_min: int,
                      soc_max: int, latitude: float, longitude: float,
                      mileage: int = 0, last_maintenance_date: str = None) -> bool:
        """Create new scooter (Super Admin and System Admin only)"""
        try:
            # Validate inputs
            brand = InputValidator.validate_name(brand, "Brand")
            model = InputValidator.validate_name(model, "Model")
            serial_number = InputValidator.validate_serial_number(serial_number)
            
            top_speed = InputValidator.validate_integer(str(top_speed), 1, 100, "Top speed")
            battery_capacity = InputValidator.validate_integer(str(battery_capacity), 100, 10000, "Battery capacity")
            soc = InputValidator.validate_integer(str(soc), 0, 100, "State of Charge")
            soc_min = InputValidator.validate_integer(str(soc_min), 0, 100, "Minimum SoC")
            soc_max = InputValidator.validate_integer(str(soc_max), 0, 100, "Maximum SoC")
            mileage = InputValidator.validate_integer(str(mileage), 0, 999999, "Mileage")
            
            if soc_min >= soc_max:
                raise ValidationError("Minimum SoC must be less than Maximum SoC")
            
            if not (soc_min <= soc <= soc_max):
                raise ValidationError("Current SoC must be between minimum and maximum SoC")
            
            # Validate coordinates
            latitude, longitude = InputValidator.validate_coordinates(latitude, longitude)
            
            # Validate maintenance date if provided
            if last_maintenance_date:
                last_maintenance_date = InputValidator.validate_date(last_maintenance_date, "Last maintenance date")
            
            # Check for duplicate serial number
            existing_query = "SELECT COUNT(*) FROM scooters WHERE serial_number = ?"
            if db.execute_scalar(existing_query, (serial_number,)) > 0:
                raise ValidationError("Serial number already exists")
            
            in_service_date = datetime.now().strftime('%Y-%m-%d')
            
            query = """
            INSERT INTO scooters (brand, model, serial_number, top_speed, battery_capacity,
                                soc, soc_min, soc_max, latitude, longitude, out_of_service,
                                mileage, last_maintenance_date, in_service_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            db.execute_non_query(query, (
                brand, model, serial_number, top_speed, battery_capacity,
                soc, soc_min, soc_max, latitude, longitude, False,
                mileage, last_maintenance_date, in_service_date
            ))
            
            LogService.log_data_operation(admin_username, "CREATE", "scooters")
            return True
            
        except Exception as e:
            LogService.log_suspicious_activity(admin_username, f"Scooter creation failed: {str(e)}")
            raise e
    
    @staticmethod
    def get_all_scooters(username: str) -> List[Scooter]:
        """Get all scooters"""
        try:
            query = "SELECT * FROM scooters ORDER BY in_service_date DESC"
            results = db.execute_query(query)
            
            scooters = []
            for result in results:
                scooter = Scooter(
                    id=result[0],
                    brand=result[1],
                    model=result[2],
                    serial_number=result[3],
                    top_speed=result[4],
                    battery_capacity=result[5],
                    soc=result[6],
                    soc_min=result[7],
                    soc_max=result[8],
                    latitude=result[9],
                    longitude=result[10],
                    out_of_service=bool(result[11]),
                    mileage=result[12],
                    last_maintenance_date=result[13],
                    in_service_date=result[14]
                )
                scooters.append(scooter)
            
            LogService.log_activity(username, "Viewed scooters list")
            return scooters
            
        except Exception as e:
            LogService.log_suspicious_activity(username, f"Get scooters failed: {str(e)}")
            raise e
    
    @staticmethod
    def search_scooters(username: str, search_term: str) -> List[Scooter]:
        """Search scooters by partial match on brand, model, or serial number"""
        try:
            search_term = InputValidator.sanitize_input(search_term).lower()
            if len(search_term) < 2:
                raise ValidationError("Search term must be at least 2 characters")
            
            # Search in brand, model, serial_number, and ID
            query = """
            SELECT * FROM scooters 
            WHERE LOWER(brand) LIKE ? OR LOWER(model) LIKE ? OR LOWER(serial_number) LIKE ? OR CAST(id AS TEXT) LIKE ?
            ORDER BY in_service_date DESC
            """
            
            search_pattern = f"%{search_term}%"
            results = db.execute_query(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            
            scooters = []
            for result in results:
                scooter = Scooter(
                    id=result[0],
                    brand=result[1],
                    model=result[2],
                    serial_number=result[3],
                    top_speed=result[4],
                    battery_capacity=result[5],
                    soc=result[6],
                    soc_min=result[7],
                    soc_max=result[8],
                    latitude=result[9],
                    longitude=result[10],
                    out_of_service=bool(result[11]),
                    mileage=result[12],
                    last_maintenance_date=result[13],
                    in_service_date=result[14]
                )
                scooters.append(scooter)
            
            LogService.log_activity(username, f"Searched scooters: '{search_term}'")
            return scooters
            
        except Exception as e:
            LogService.log_suspicious_activity(username, f"Scooter search failed: {str(e)}")
            raise e
    
    @staticmethod
    def get_scooter_by_id(username: str, scooter_id: int) -> Optional[Scooter]:
        """Get specific scooter by ID"""
        try:
            query = "SELECT * FROM scooters WHERE id = ?"
            result = db.execute_query(query, (scooter_id,))
            
            if not result:
                return None
            
            result = result[0]
            scooter = Scooter(
                id=result[0],
                brand=result[1],
                model=result[2],
                serial_number=result[3],
                top_speed=result[4],
                battery_capacity=result[5],
                soc=result[6],
                soc_min=result[7],
                soc_max=result[8],
                latitude=result[9],
                longitude=result[10],
                out_of_service=bool(result[11]),
                mileage=result[12],
                last_maintenance_date=result[13],
                in_service_date=result[14]
            )
            
            LogService.log_activity(username, f"Viewed scooter details: ID {scooter_id}")
            return scooter
            
        except Exception as e:
            LogService.log_suspicious_activity(username, f"Get scooter failed: {str(e)}")
            raise e
    
    @staticmethod
    def update_scooter(username: str, user_role: str, scooter_id: int, **updates) -> bool:
        """Update scooter information with role-based restrictions"""
        try:
            # Get current scooter
            current = ScooterModel.get_scooter_by_id(username, scooter_id)
            if not current:
                raise ValidationError("Scooter not found")
            
            # Define what each role can update
            service_engineer_fields = {
                'soc', 'latitude', 'longitude', 'out_of_service', 'mileage', 'last_maintenance_date'
            }
            
            admin_fields = {
                'brand', 'model', 'serial_number', 'top_speed', 'battery_capacity',
                'soc', 'soc_min', 'soc_max', 'latitude', 'longitude', 'out_of_service',
                'mileage', 'last_maintenance_date'
            }
            
            # Check permissions
            allowed_fields = service_engineer_fields if user_role == 'service_engineer' else admin_fields
            
            for field in updates.keys():
                if field not in allowed_fields:
                    raise ValidationError(f"Role '{user_role}' cannot update field '{field}'")
            
            # Validate and prepare updates
            validated_updates = {}
            
            if 'brand' in updates:
                validated_updates['brand'] = InputValidator.validate_name(updates['brand'], "Brand")
            
            if 'model' in updates:
                validated_updates['model'] = InputValidator.validate_name(updates['model'], "Model")
            
            if 'serial_number' in updates:
                new_serial = InputValidator.validate_serial_number(updates['serial_number'])
                # Check for duplicates (excluding current record)
                duplicate_query = "SELECT COUNT(*) FROM scooters WHERE serial_number = ? AND id != ?"
                if db.execute_scalar(duplicate_query, (new_serial, scooter_id)) > 0:
                    raise ValidationError("Serial number already exists")
                validated_updates['serial_number'] = new_serial
            
            if 'top_speed' in updates:
                validated_updates['top_speed'] = InputValidator.validate_integer(
                    str(updates['top_speed']), 1, 100, "Top speed"
                )
            
            if 'battery_capacity' in updates:
                validated_updates['battery_capacity'] = InputValidator.validate_integer(
                    str(updates['battery_capacity']), 100, 10000, "Battery capacity"
                )
            
            if 'soc' in updates:
                validated_updates['soc'] = InputValidator.validate_integer(
                    str(updates['soc']), 0, 100, "State of Charge"
                )
            
            if 'soc_min' in updates:
                validated_updates['soc_min'] = InputValidator.validate_integer(
                    str(updates['soc_min']), 0, 100, "Minimum SoC"
                )
            
            if 'soc_max' in updates:
                validated_updates['soc_max'] = InputValidator.validate_integer(
                    str(updates['soc_max']), 0, 100, "Maximum SoC"
                )
            
            if 'latitude' in updates and 'longitude' in updates:
                lat, lon = InputValidator.validate_coordinates(
                    float(updates['latitude']), float(updates['longitude'])
                )
                validated_updates['latitude'] = lat
                validated_updates['longitude'] = lon
            elif 'latitude' in updates or 'longitude' in updates:
                raise ValidationError("Both latitude and longitude must be provided together")
            
            if 'out_of_service' in updates:
                validated_updates['out_of_service'] = bool(updates['out_of_service'])
            
            if 'mileage' in updates:
                validated_updates['mileage'] = InputValidator.validate_integer(
                    str(updates['mileage']), 0, 999999, "Mileage"
                )
            
            if 'last_maintenance_date' in updates:
                if updates['last_maintenance_date']:
                    validated_updates['last_maintenance_date'] = InputValidator.validate_date(
                        updates['last_maintenance_date'], "Last maintenance date"
                    )
                else:
                    validated_updates['last_maintenance_date'] = None
            
            # Validate SoC relationships
            final_soc_min = validated_updates.get('soc_min', current.soc_min)
            final_soc_max = validated_updates.get('soc_max', current.soc_max)
            final_soc = validated_updates.get('soc', current.soc)
            
            if final_soc_min >= final_soc_max:
                raise ValidationError("Minimum SoC must be less than Maximum SoC")
            
            if not (final_soc_min <= final_soc <= final_soc_max):
                raise ValidationError("Current SoC must be between minimum and maximum SoC")
            
            if not validated_updates:
                raise ValidationError("No valid updates provided")
            
            # Build update query
            set_clauses = []
            values = []
            for field, value in validated_updates.items():
                set_clauses.append(f"{field} = ?")
                values.append(value)
            
            values.append(scooter_id)
            query = f"UPDATE scooters SET {', '.join(set_clauses)} WHERE id = ?"
            
            rows_affected = db.execute_non_query(query, tuple(values))
            
            if rows_affected > 0:
                LogService.log_data_operation(username, "UPDATE", "scooters", str(scooter_id))
                return True
            
            return False
            
        except Exception as e:
            LogService.log_suspicious_activity(username, f"Scooter update failed: {str(e)}")
            raise e
    
    @staticmethod
    def delete_scooter(admin_username: str, scooter_id: int) -> bool:
        """Delete scooter (Super Admin and System Admin only)"""
        try:
            query = "DELETE FROM scooters WHERE id = ?"
            rows_affected = db.execute_non_query(query, (scooter_id,))
            
            if rows_affected > 0:
                LogService.log_data_operation(admin_username, "DELETE", "scooters", str(scooter_id))
                return True
            
            return False
            
        except Exception as e:
            LogService.log_suspicious_activity(admin_username, f"Scooter deletion failed: {str(e)}")
            raise e