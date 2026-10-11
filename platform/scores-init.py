from sqlalchemy import func, select
from CTFd.models import db, Users, Solves, Awards

def get_standings(count=None, admin=False):
    try:
        query = db.session.execute(
            db.text("SELECT 1 FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'ctfd' AND TABLE_NAME = 'hint_deductions'")
        )
        table_exists = query.fetchone() is not None
    except:
        table_exists = False

    if table_exists:
        standings = db.session.execute(
            db.text("""
                SELECT 
                    u.id as account_id,
                    u.name,
                    (
                        SELECT COALESCE(SUM(
                            CASE 
                                WHEN EXISTS(SELECT 1 FROM hint_deductions hd WHERE hd.user_id = u.id AND hd.challenge_id = s.challenge_id)
                                THEN s.value - 5
                                ELSE s.value
                            END
                        ), 0)
                        FROM solves s
                        WHERE s.user_id = u.id
                    ) + COALESCE((SELECT SUM(a.value) FROM awards a WHERE a.user_id = u.id), 0) as score,
                    MAX(s.date) as last_solve
                FROM users u
                LEFT JOIN solves s ON u.id = s.user_id
                WHERE u.banned = FALSE AND u.type = 'user'
                GROUP BY u.id, u.name
                ORDER BY score DESC, last_solve ASC
            """)
        ).fetchall()
    else:
        standings = db.session.execute(
            db.text("""
                SELECT 
                    u.id as account_id,
                    u.name,
                    COALESCE(SUM(s.value), 0) + COALESCE(SUM(a.value), 0) as score,
                    MAX(s.date) as last_solve
                FROM users u
                LEFT JOIN solves s ON u.id = s.user_id
                LEFT JOIN awards a ON u.id = a.user_id
                WHERE u.banned = FALSE
                GROUP BY u.id, u.name
                ORDER BY score DESC, last_solve ASC
            """)
        ).fetchall()

    return standings

def get_user_standings(user_id, count=None):
    try:
        query = db.session.execute(
            db.text("SELECT 1 FROM information_schema.TABLES WHERE TABLE_SCHEMA = 'ctfd' AND TABLE_NAME = 'hint_deductions'")
        )
        table_exists = query.fetchone() is not None
    except:
        table_exists = False

    if table_exists:
        standings = db.session.execute(
            db.text("""
                SELECT 
                    u.id as account_id,
                    u.name,
                    (
                        SELECT COALESCE(SUM(
                            CASE 
                                WHEN EXISTS(SELECT 1 FROM hint_deductions hd WHERE hd.user_id = u.id AND hd.challenge_id = s.challenge_id)
                                THEN s.value - 5
                                ELSE s.value
                            END
                        ), 0)
                        FROM solves s
                        WHERE s.user_id = u.id
                    ) + COALESCE((SELECT SUM(a.value) FROM awards a WHERE a.user_id = u.id), 0) as score,
                    MAX(s.date) as last_solve
                FROM users u
                LEFT JOIN solves s ON u.id = s.user_id
                WHERE u.id = :user_id AND u.banned = FALSE AND u.type = 'user'
                GROUP BY u.id, u.name
            """, {"user_id": user_id})
        ).fetchall()
    else:
        standings = db.session.execute(
            db.text("""
                SELECT 
                    u.id as account_id,
                    u.name,
                    COALESCE(SUM(s.value), 0) + COALESCE(SUM(a.value), 0) as score,
                    MAX(s.date) as last_solve
                FROM users u
                LEFT JOIN solves s ON u.id = s.user_id
                LEFT JOIN awards a ON u.id = a.user_id
                WHERE u.id = :user_id AND u.banned = FALSE
                GROUP BY u.id, u.name
            """, {"user_id": user_id})
        ).fetchall()

    return standings

def get_team_standings(count=None, admin=False):
    standings = db.session.execute(
        db.text("""
            SELECT 
                t.id as account_id,
                t.name,
                COALESCE(SUM(s.value), 0) + COALESCE(SUM(a.value), 0) as score,
                MAX(s.date) as last_solve
            FROM teams t
            LEFT JOIN solves s ON t.id = s.team_id
            LEFT JOIN awards a ON t.id = a.team_id
            WHERE t.banned = FALSE
            GROUP BY t.id, t.name
            ORDER BY score DESC, last_solve ASC
        """)
    ).fetchall()

    return standings