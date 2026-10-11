#!/usr/bin/env python3
"""
NIGHTWIRE CTFd Hint Score Adjustment Service
Monitors hint views and automatically deducts points from player scores.
Writes deductions to the hint_deductions table for CTFd to read.
"""

import mysql.connector
import time
import sys
from datetime import datetime
from mysql.connector import Error as MySQLError

# Configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'ctfd',
    'password': 'ctfd',
    'database': 'ctfd'
}

HINT_COST = 5  # Points deducted per hint

# Track processed unlocks to avoid double-deducting
processed_unlocks = set()

def log(message):
    """Log with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print(f"[{timestamp}] {message}")
    sys.stdout.flush()

def get_db_connection():
    """Create database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except MySQLError as e:
        log(f"Database connection error: {e}")
        return None

def ensure_deductions_table(cursor):
    """Ensure hint_deductions table exists"""
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS hint_deductions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            challenge_id INT,
            hint_id INT,
            cost INT DEFAULT 5,
            created DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE KEY unique_hint_unlock (user_id, hint_id)
        )
        """)
        log("✓ hint_deductions table ready")
    except MySQLError as e:
        log(f"Error creating deductions table: {e}")

def process_hint_views():
    """Check for new hint views and record deductions"""
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Ensure table exists
        ensure_deductions_table(cursor)
        
        # Query all hint unlocks
        query = """
        SELECT u.id, u.user_id, h.id as hint_id, h.challenge_id, COALESCE(h.cost, %s) as cost
        FROM unlocks u
        JOIN hints h ON u.target = h.id
        WHERE u.type = 'hints'
        ORDER BY u.id
        """
        
        cursor.execute(query, (HINT_COST,))
        results = cursor.fetchall()
        
        new_unlocks = []
        for row in results:
            unlock_id = row['id']
            if unlock_id not in processed_unlocks:
                new_unlocks.append(row)
                processed_unlocks.add(unlock_id)
        
        if new_unlocks:
            log(f"Found {len(new_unlocks)} new hint view(s)")
            for row in new_unlocks:
                user_id = row['user_id']
                challenge_id = row['challenge_id']
                hint_id = row['hint_id']
                cost = row['cost']
                
                # Record the deduction in the database
                try:
                    insert_query = """
                    INSERT INTO hint_deductions (user_id, challenge_id, hint_id, cost)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE created=CURRENT_TIMESTAMP
                    """
                    cursor.execute(insert_query, (user_id, challenge_id, hint_id, cost))
                    conn.commit()
                    log(f"✓ User {user_id} - Hint {hint_id}: -{cost} points deducted")
                except MySQLError as e:
                    log(f"✗ Error recording deduction for user {user_id}: {e}")
                    conn.rollback()
        
        cursor.close()
        
    except MySQLError as e:
        log(f"Database query error: {e}")
    finally:
        conn.close()

def main():
    """Main service loop"""
    log("=" * 60)
    log("NIGHTWIRE Hint Score Adjustment Service started")
    log("Monitoring for hint views... (checking every 5 seconds)")
    log("Press Ctrl+C to stop")
    log("=" * 60)
    
    try:
        while True:
            process_hint_views()
            time.sleep(5)
    except KeyboardInterrupt:
        log("\nService stopped by user")
        sys.exit(0)
    except Exception as e:
        log(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
