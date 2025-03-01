import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from loguru import logger

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

def get_admin_user_id():
    """Get the admin user ID from the database."""
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query to get admin user ID
        query = """
        SELECT user_id 
        FROM users 
        WHERE username = %s
        LIMIT 1
        """
        cur.execute(query, (AUTH_CREDENTIALS["username"].replace("-","_"),))
        result = cur.fetchone()
        
        if result:
            return result['user_id']
        logger.error("Admin user not found in database")
        return None
        
    except Exception as e:
        logger.error(f"Error fetching admin user ID: {e}")
        return None
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

# Get USER_ID from database
USER_ID = get_admin_user_id()