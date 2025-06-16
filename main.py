from init_db import initialize_database
from services.auth_service import login_user

if __name__ == "__main__":
    initialize_database()
    print("Welcome to Urban Mobility Admin System")
    login_user()
