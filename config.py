import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin123user")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "skin_disease_detection")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Authentication settings
AUTH_CREDENTIALS = {
    "username": "admin-user",
    "password": "admin123user"
}

# Session configuration
SESSION_EXPIRE_DAYS = 30

# User ID for now
USER_ID = os.getenv("USER_ID")