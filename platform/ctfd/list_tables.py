import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'ctfd',
    'password': 'ctfd',
    'database': 'ctfd'
}

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()

print("All tables in ctfd database:")
for table in tables:
    print(f"  - {table[0]}")

cursor.close()
conn.close()