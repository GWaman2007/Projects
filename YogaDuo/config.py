import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
SESSION_TYPE = os.getenv('SESSION_TYPE')
