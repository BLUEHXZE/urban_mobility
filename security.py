import bcrypt
from cryptography.fernet import Fernet

# You should store this key securely! Save it to a file if needed.
SECRET_KEY = Fernet.generate_key()
cipher = Fernet(SECRET_KEY)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def encrypt_data(plaintext: str) -> str:
    return cipher.encrypt(plaintext.encode()).decode()

def decrypt_data(ciphertext: str) -> str:
    return cipher.decrypt(ciphertext.encode()).decode()
