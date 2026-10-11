#!/usr/bin/env python3
"""
Hint Score Adjuster Service
Monitors hint_deductions table and ensures negative awards are created
Runs as a background service in the CTFd container

Usage:
    python3 hint_score_adjuster.py &

Configuration:
    Set DB_HOST, DB_USER, DB_PASS, DB_NAME, POLL_INTERVAL in environment or below
"""

import os
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import time
import sys

# Database configuration
DB_HOST = os.getenv("DB_HOST", "db")
DB_USER = os.getenv("DB_USER", "ctfd")
DB_PASS = os.getenv("DB_PASS", "ctfd")
DB_NAME = os.getenv("DB_NAME", "ctfd")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))

DB_CONFIG = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASS,
    "database": DB_NAME,
    "auth_plugin": "mysql_native_password",
}

# Track which deductions we've already processed
processed_deductions = set()


def log_msg(msg):
    """Print timestamped log message"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def connect_db():
    """Create database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as err:
        log_msg(f"Database connection failed: {err}")
        return None


def get_unprocessed_deductions():
    """Get hint deductions that don't have corresponding awards yet"""
    try:
        conn = connect_db()
        if not conn:
            return []

        cursor = conn.cursor(dictionary=True)

        # Find deductions without matching awards
        cursor.execute("""
            SELECT
                hd.id,
                hd.user_id,
                hd.hint_id,
                hd.challenge_id,
                hd.cost,
                u.team_id,
                h.title as hint_title
            FROM hint_deductions hd
            JOIN users u ON hd.user_id = u.id
            LEFT JOIN hints h ON hd.hint_id = h.id
            LEFT JOIN awards a ON (
                a.team_id = u.team_id
                AND a.category = 'hints'
                AND a.value = -hd.cost
                AND a.created >= hd.created
            )
            WHERE a.id IS NULL
            AND hd.id NOT IN ({})
        """.format(",".join(map(str, processed_deductions)) if processed_deductions else "0"))

        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Error as err:
        log_msg(f"Error fetching deductions: {err}")
        return []


def create_award_for_deduction(deduction):
    """Create a negative award for a hint deduction"""
    try:
        conn = connect_db()
        if not conn:
            return False

        cursor = conn.cursor()

        user_id = deduction["user_id"]
        hint_id = deduction["hint_id"]
        team_id = deduction["team_id"]
        cost = deduction["cost"]
        hint_title = deduction["hint_title"] or "hint"

        # Insert award with negative value
        cursor.execute("""
            INSERT INTO awards
            (team_id, name, description, value, category, type, created)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (
            team_id,
            "Hint penalty",
            f"Penalty for viewing hint: {hint_title}",
            -cost,
            "hints",
            "standard"
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return True
    except Error as err:
        log_msg(f"Error creating award: {err}")
        return False


def process_deductions():
    """Main processing loop"""
    global processed_deductions

    while True:
        try:
            deductions = get_unprocessed_deductions()

            if deductions:
                for deduction in deductions:
                    if create_award_for_deduction(deduction):
                        processed_deductions.add(deduction["id"])
                        log_msg(
                            f"✓ Created award for User {deduction['user_id']} "
                            f"(Team {deduction['team_id']}): "
                            f"-{deduction['cost']} pts for hint #{deduction['hint_id']}"
                        )
                    else:
                        log_msg(
                            f"✗ Failed to create award for User {deduction['user_id']} "
                            f"hint #{deduction['hint_id']}"
                        )

            # Clean up very old processed entries (keep last 1000)
            if len(processed_deductions) > 5000:
                processed_deductions = set(list(processed_deductions)[-1000:])

            time.sleep(POLL_INTERVAL)

        except Exception as err:
            log_msg(f"Unexpected error: {err}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    log_msg("Starting Hint Score Adjuster Service")
    log_msg(f"Database: {DB_HOST}/{DB_NAME}, Poll interval: {POLL_INTERVAL}s")

    # Wait for DB to be ready
    max_retries = 30
    for attempt in range(max_retries):
        conn = connect_db()
        if conn:
            conn.close()
            log_msg("Database connected successfully")
            break
        if attempt == max_retries - 1:
            log_msg("Failed to connect to database after 30 attempts, exiting")
            sys.exit(1)
        time.sleep(1)

    try:
        process_deductions()
    except KeyboardInterrupt:
        log_msg("Shutting down...")
        sys.exit(0)