import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'ctfd',
    'password': 'ctfd',
    'database': 'ctfd'
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Get users table structure
    cursor.execute("DESCRIBE users;")
    results = cursor.fetchall()
    
    print("Users table columns:")
    print("=" * 50)
    for row in results:
        print(row)
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")