import re
from typing import Union, List

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class InputValidator:
    """Secure input validation using whitelisting approach"""
    
    @staticmethod
    def validate_username(username: str) -> str:
        """Validate username according to requirements"""
        if not username:
            raise ValidationError("Username cannot be empty")
        
        # Remove any potential null bytes
        username = username.replace('\x00', '')
        
        # Length check
        if len(username) < 8 or len(username) > 10:
            raise ValidationError("Username must be between 8-10 characters")
        
        # Pattern check: must start with letter or underscore, contain only allowed chars
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_.\']$'
        if not re.match(pattern, username):
            raise ValidationError("Username must start with letter/underscore and contain only letters, numbers, _, ', .")
        
        return username.lower()  # Case insensitive
    
    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password according to requirements"""
        if not password:
            raise ValidationError("Password cannot be empty")
        
        # Remove any potential null bytes
        password = password.replace('\x00', '')
        
        # Length check
        if len(password) < 12 or len(password) > 30:
            raise ValidationError("Password must be between 12-30 characters")
        
        # Check for required character types
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "~!@#$%&_-+=`|\\(){}[]:;'<>,.?/" for c in password)
        
        if not all([has_lower, has_upper, has_digit, has_special]):
            raise ValidationError("Password must contain at least one lowercase, uppercase, digit, and special character")
        
        return password
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email address"""
        if not email:
            raise ValidationError("Email cannot be empty")
        
        email = email.replace('\x00', '').strip()
        
        # Basic email pattern validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format")
        
        return email
    
    @staticmethod
    def validate_phone(phone: str) -> str:
        """Validate Dutch mobile phone number"""
        if not phone:
            raise ValidationError("Phone cannot be empty")
        
        phone = phone.replace('\x00', '').strip()
        
        # Check for exactly 8 digits
        if not re.match(r'^\d{8}$', phone):
            raise ValidationError("Phone must be exactly 8 digits")
        
        return f"+31-6-{phone}"
    
    @staticmethod
    def validate_zip_code(zip_code: str) -> str:
        """Validate Dutch postal code format DDDDXX"""
        if not zip_code:
            raise ValidationError("Zip code cannot be empty")
        
        zip_code = zip_code.replace('\x00', '').strip().upper()
        
        # Check format: 4 digits + 2 uppercase letters
        if not re.match(r'^\d{4}[A-Z]{2}$', zip_code):
            raise ValidationError("Zip code must be in format DDDDXX (4 digits + 2 letters)")
        
        return zip_code
    
    @staticmethod
    def validate_driving_license(license_num: str) -> str:
        """Validate driving license number format"""
        if not license_num:
            raise ValidationError("Driving license number cannot be empty")
        
        license_num = license_num.replace('\x00', '').strip().upper()
        
        # Check format: XXDDDDDDD or XDDDDDDDD
        if not re.match(r'^[A-Z]{1,2}\d{7,8}$', license_num):
            raise ValidationError("Driving license must be in format XXDDDDDDD or XDDDDDDDD")
        
        return license_num
    
    @staticmethod
    def validate_serial_number(serial: str) -> str:
        """Validate scooter serial number"""
        if not serial:
            raise ValidationError("Serial number cannot be empty")
        
        serial = serial.replace('\x00', '').strip()
        
        # 10-17 alphanumeric characters
        if len(serial) < 10 or len(serial) > 17:
            raise ValidationError("Serial number must be between 10-17 characters")
        
        if not re.match(r'^[a-zA-Z0-9]+$', serial):
            raise ValidationError("Serial number must contain only alphanumeric characters")
        
        return serial.upper()
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> tuple:
        """Validate GPS coordinates for Rotterdam region"""
        # Rotterdam region bounds (approximate)
        if not (51.8 <= lat <= 52.0 and 4.3 <= lon <= 4.6):
            raise ValidationError("Coordinates must be within Rotterdam region")
        
        # Round to 5 decimal places for 2-meter accuracy
        return round(lat, 5), round(lon, 5)
    
    @staticmethod
    def validate_name(name: str, field_name: str = "Name") -> str:
        """Validate person names"""
        if not name:
            raise ValidationError(f"{field_name} cannot be empty")
        
        name = name.replace('\x00', '').strip()
        
        # Allow letters, spaces, hyphens, apostrophes
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            raise ValidationError(f"{field_name} must contain only letters, spaces, hyphens, and apostrophes")
        
        if len(name) > 50:
            raise ValidationError(f"{field_name} must be less than 50 characters")
        
        return name.title()
    
    @staticmethod
    def validate_city(city: str) -> str:
        """Validate city selection from predefined list"""
        predefined_cities = [
            "Rotterdam", "Amsterdam", "The Hague", "Utrecht", "Eindhoven",
            "Groningen", "Tilburg", "Almere", "Breda", "Nijmegen"
        ]
        
        if not city:
            raise ValidationError("City cannot be empty")
        
        city = city.replace('\x00', '').strip().title()
        
        if city not in predefined_cities:
            raise ValidationError(f"City must be one of: {', '.join(predefined_cities)}")
        
        return city
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """General input sanitization"""
        if not isinstance(input_str, str):
            return str(input_str)
        
        # Remove null bytes and control characters
        sanitized = input_str.replace('\x00', '')
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\r\t')
        
        return sanitized.strip()
    
    @staticmethod
    def validate_integer(value: str, min_val: int = None, max_val: int = None, field_name: str = "Value") -> int:
        """Validate integer input with optional range"""
        if not value:
            raise ValidationError(f"{field_name} cannot be empty")
        
        value = value.replace('\x00', '').strip()
        
        try:
            int_val = int(value)
        except ValueError:
            raise ValidationError(f"{field_name} must be a valid integer")
        
        if min_val is not None and int_val < min_val:
            raise ValidationError(f"{field_name} must be at least {min_val}")
        
        if max_val is not None and int_val > max_val:
            raise ValidationError(f"{field_name} must be at most {max_val}")
        
        return int_val
    
    @staticmethod
    def validate_date(date_str: str, field_name: str = "Date") -> str:
        """Validate date in ISO format YYYY-MM-DD"""
        if not date_str:
            raise ValidationError(f"{field_name} cannot be empty")
        
        date_str = date_str.replace('\x00', '').strip()
        
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            raise ValidationError(f"{field_name} must be in format YYYY-MM-DD")
        
        # Additional date validation could be added here
        return date_str