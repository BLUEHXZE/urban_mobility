import bcrypt
import os
from cryptography.fernet import Fernet
import hmac
import hashlib

# Secure key management
KEY_FILE = "data/encryption.key"

def _load_or_create_key():
    """Load existing key or create new one"""
    os.makedirs(os.path.dirname(KEY_FILE), exist_ok=True)
    
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        return key

SECRET_KEY = _load_or_create_key()
cipher = Fernet(SECRET_KEY)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def encrypt_data(plaintext: str) -> str:
    return cipher.encrypt(plaintext.encode()).decode()

def decrypt_data(ciphertext: str) -> str:
    return cipher.decrypt(ciphertext.encode()).decode()

def encrypt_username_deterministic(username: str) -> str:
    """Deterministically encrypt (hash) a username for storage and lookup."""
    # Use HMAC-SHA256 with the SECRET_KEY for deterministic, keyed pseudonymization
    return hmac.new(SECRET_KEY, username.lower().encode(), hashlib.sha256).hexdigest()
