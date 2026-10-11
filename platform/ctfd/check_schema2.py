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

print("Solves table columns:")
print("=" * 50)
cursor.execute("DESCRIBE solves;")
for row in cursor.fetchall():
    print(row)

print("\n\nChallenges table columns:")
print("=" * 50)
cursor.execute("DESCRIBE challenges;")
for row in cursor.fetchall():
    print(row)

cursor.close()
conn.close()