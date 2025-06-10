import mysql.connector

# Database configuration
config = {
    'user': 'AMANWEB',
    'password': '@M@N2007',
    'host': 'AMANWEB.mysql.pythonanywhere-services.com',
}

try:
    # Establish a connection to MySQL
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS AMAN27;")
    # Query to list all databases
    cursor.execute("SHOW DATABASES;")

    # Fetch and print all databases
    databases = cursor.fetchall()
    print("Databases in MySQL:")
    for db in databases:
        print(db[0])

except mysql.connector.Error as err:
    print(f"Error: {err}")