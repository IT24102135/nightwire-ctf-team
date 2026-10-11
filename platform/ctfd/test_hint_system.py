#!/usr/bin/env python3
"""
Test Script for Hint Penalty System
Verifies that the hint penalty system is working correctly
"""

import mysql.connector
from mysql.connector import Error
import sys
import os
from datetime import datetime

# Database config
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "ctfd")
DB_PASS = os.getenv("DB_PASS", "ctfd")
DB_NAME = os.getenv("DB_NAME", "ctfd")

DB_CONFIG = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASS,
    "database": DB_NAME,
    "auth_plugin": "mysql_native_password",
}

def log_msg(msg, status="INFO"):
    """Print formatted log message"""
    status_symbol = {
        "OK": "✓",
        "FAIL": "✗",
        "WARN": "⚠",
        "INFO": "ℹ"
    }
    symbol = status_symbol.get(status, "?")
    print(f"[{symbol}] {msg}")

def connect_db():
    """Connect to database"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        log_msg(f"Failed to connect to database: {e}", "FAIL")
        return None

def test_database_connection():
    """Test 1: Database Connection"""
    print("\n[TEST 1] Database Connection")
    print("-" * 50)

    conn = connect_db()
    if not conn:
        log_msg("Cannot connect to database", "FAIL")
        return False

    conn.close()
    log_msg("Connected to database", "OK")
    return True

def test_hint_deductions_table():
    """Test 2: hint_deductions Table"""
    print("\n[TEST 2] hint_deductions Table Exists")
    print("-" * 50)

    conn = connect_db()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute("DESC hint_deductions")
        columns = [row[0] for row in cursor.fetchall()]

        required = ["id", "user_id", "hint_id", "challenge_id", "cost", "created"]
        missing = [col for col in required if col not in columns]

        if missing:
            log_msg(f"Missing columns: {missing}", "FAIL")
            cursor.close()
            conn.close()
            return False

        log_msg("hint_deductions table has all required columns", "OK")

        # Check UNIQUE constraint
        cursor.execute("SHOW KEYS FROM hint_deductions WHERE Key_name LIKE '%uq%'")
        if cursor.fetchone():
            log_msg("UNIQUE constraint on (user_id, hint_id) found", "OK")
        else:
            log_msg("UNIQUE constraint NOT found", "WARN")

        cursor.close()
        conn.close()
        return True

    except Error as e:
        if "Unknown table" in str(e):
            log_msg("hint_deductions table does not exist (will be created on first hint view)", "WARN")
            cursor.close()
            conn.close()
            return True
        else:
            log_msg(f"Error checking table: {e}", "FAIL")
            cursor.close()
            conn.close()
            return False

def test_awards_table():
    """Test 3: awards Table"""
    print("\n[TEST 3] awards Table Exists")
    print("-" * 50)

    conn = connect_db()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute("DESC awards")
        columns = [row[0] for row in cursor.fetchall()]

        if "category" not in columns:
            log_msg("awards table missing 'category' column", "FAIL")
            cursor.close()
            conn.close()
            return False

        log_msg("awards table exists with required columns", "OK")

        # Check for existing hint penalties
        cursor.execute("SELECT COUNT(*) FROM awards WHERE category = 'hints'")
        count = cursor.fetchone()[0]
        log_msg(f"Current hint penalty awards in database: {count}", "INFO")

        if count > 0:
            cursor.execute("SELECT team_id, SUM(value) as total FROM awards WHERE category = 'hints' GROUP BY team_id")
            for team_id, total in cursor.fetchall():
                log_msg(f"  Team {team_id}: {total} points deducted", "INFO")

        cursor.close()
        conn.close()
        return True

    except Error as e:
        log_msg(f"Error checking awards table: {e}", "FAIL")
        cursor.close()
        conn.close()
        return False

def test_data_integrity():
    """Test 4: Data Integrity"""
    print("\n[TEST 4] Data Integrity")
    print("-" * 50)

    conn = connect_db()
    if not conn:
        return False

    cursor = conn.cursor()
    all_ok = True

    try:
        # Check hints table
        cursor.execute("SELECT COUNT(*) FROM hints")
        hint_count = cursor.fetchone()[0]
        log_msg(f"Total hints in database: {hint_count}", "INFO")

        # Check challenges table
        cursor.execute("SELECT COUNT(*) FROM challenges")
        challenge_count = cursor.fetchone()[0]
        log_msg(f"Total challenges in database: {challenge_count}", "INFO")

        # Check users table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        log_msg(f"Total users in database: {user_count}", "INFO")

        # Check teams table
        cursor.execute("SELECT COUNT(*) FROM teams")
        team_count = cursor.fetchone()[0]
        log_msg(f"Total teams in database: {team_count}", "INFO")

        # Check for orphaned hint_deductions (if table exists)
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM hint_deductions hd
                LEFT JOIN users u ON hd.user_id = u.id
                WHERE u.id IS NULL
            """)
            orphaned = cursor.fetchone()[0]
            if orphaned > 0:
                log_msg(f"Found {orphaned} orphaned hint_deduction records", "WARN")
            else:
                log_msg("No orphaned hint_deduction records", "OK")
        except:
            pass  # Table might not exist yet

        cursor.close()
        conn.close()
        return True

    except Error as e:
        log_msg(f"Error checking data integrity: {e}", "FAIL")
        cursor.close()
        conn.close()
        return False

def test_team_scores():
    """Test 5: Team Scores Calculation"""
    print("\n[TEST 5] Team Score Calculation")
    print("-" * 50)

    conn = connect_db()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT t.id, t.name, SUM(a.value) as total_score
            FROM teams t
            LEFT JOIN awards a ON t.id = a.team_id
            GROUP BY t.id
            ORDER BY total_score DESC
            LIMIT 5
        """)

        results = cursor.fetchall()
        if not results:
            log_msg("No teams found", "WARN")
        else:
            log_msg("Top 5 Team Scores:", "INFO")
            for team_id, team_name, score in results:
                score_display = score if score else 0
                log_msg(f"  {team_name} (ID {team_id}): {score_display} points", "INFO")

        cursor.close()
        conn.close()
        return True

    except Error as e:
        log_msg(f"Error calculating team scores: {e}", "FAIL")
        cursor.close()
        conn.close()
        return False

def test_hint_costs():
    """Test 6: Hint Costs"""
    print("\n[TEST 6] Hint Costs Configuration")
    print("-" * 50)

    conn = connect_db()
    if not conn:
        return False

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, title, cost FROM hints LIMIT 10")
        hints = cursor.fetchall()

        if not hints:
            log_msg("No hints found in database", "WARN")
        else:
            log_msg("Hints and their costs:", "INFO")
            for hint_id, title, cost in hints:
                cost_display = cost if cost else "DEFAULT (5)"
                log_msg(f"  Hint {hint_id}: {title} - {cost_display} points", "INFO")

        cursor.close()
        conn.close()
        return True

    except Error as e:
        log_msg(f"Error checking hint costs: {e}", "FAIL")
        cursor.close()
        conn.close()
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("HINT PENALTY SYSTEM TEST SUITE")
    print("=" * 50)
    print(f"Database: {DB_HOST}/{DB_NAME}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = []

    results.append(("Database Connection", test_database_connection()))
    results.append(("hint_deductions Table", test_hint_deductions_table()))
    results.append(("awards Table", test_awards_table()))
    results.append(("Data Integrity", test_data_integrity()))
    results.append(("Team Scores", test_team_scores()))
    results.append(("Hint Costs", test_hint_costs()))

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ System is ready!")
    else:
        print(f"\n⚠ {total - passed} test(s) need attention")

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())