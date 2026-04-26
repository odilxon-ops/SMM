import sqlite3

import runtime_bootstrap
from config import DB_NAME


def migrate():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        if "id" in columns:
            print("ID column already exists.")
            return

        cursor.execute("ALTER TABLE users RENAME TO users_old")
        cursor.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT,
                full_name TEXT,
                balance INTEGER DEFAULT 0,
                total_spent INTEGER DEFAULT 0,
                referrer_id INTEGER DEFAULT 0,
                phone_number TEXT DEFAULT 'No',
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_blocked INTEGER DEFAULT 0
            )
            """
        )
        cursor.execute(
            """
            INSERT INTO users (
                user_id, username, full_name, balance, total_spent, referrer_id, phone_number, registered_at, is_blocked
            )
            SELECT
                user_id,
                username,
                full_name,
                CAST(ROUND(balance) AS INTEGER),
                CAST(ROUND(total_spent) AS INTEGER),
                referrer_id,
                phone_number,
                registered_at,
                is_blocked
            FROM users_old
            """
        )
        cursor.execute('DELETE FROM sqlite_sequence WHERE name="users"')
        cursor.execute('INSERT INTO sqlite_sequence (name, seq) VALUES ("users", 1999)')
        cursor.execute("DROP TABLE users_old")

        conn.commit()
        print("Database migrated successfully! IDs start from 2000.")
    except Exception as exc:
        print(f"Error during migration: {exc}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
