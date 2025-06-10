import mysql.connector
from config import DB_CONFIG  # Ensure DB_CONFIG contains correct credentials

try:
    db = mysql.connector.connect(**DB_CONFIG)
    print("Database connection successful!")
except mysql.connector.Error as e:
    print(f"Error connecting to the database: {e}")
cursor=db.cursor()