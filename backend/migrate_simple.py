"""
Simple Database Migration Script - Direct SQL
"""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env file")
    exit(1)

print("Connecting to database...")

# Parse connection URL
# Format: postgresql://user:password@host/dbname?sslmode=require
try:
    # Remove postgresql:// prefix
    conn_str = DATABASE_URL.replace("postgresql://", "")

    # Split by @ to get user:pass and host/db
    parts = conn_str.split("@")
    user_pass = parts[0]
    host_db_params = parts[1]

    # Split user:pass
    user, password = user_pass.split(":", 1)

    # Split host/db?params
    host_db = host_db_params.split("?")[0]
    host, db = host_db.split("/", 1)

    print(f"Connecting to: {host}/{db}")

    # Connect
    conn = psycopg2.connect(host=host, database=db, user=user, password=password, sslmode="require")

    conn.autocommit = True
    cur = conn.cursor()

    print("Connected successfully!")
    print("=" * 50)

    # Add is_email_verified column
    try:
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_email_verified BOOLEAN DEFAULT FALSE")
        print("[OK] Column 'is_email_verified' ready")
    except Exception as e:
        print(f"[SKIP] is_email_verified: {e}")

    # Add email_verified_at column
    try:
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified_at TIMESTAMP")
        print("[OK] Column 'email_verified_at' ready")
    except Exception as e:
        print(f"[SKIP] email_verified_at: {e}")

    # Create email_verifications table
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS email_verifications (
                id UUID PRIMARY KEY,
                email VARCHAR(255) NOT NULL,
                token VARCHAR(255) UNIQUE NOT NULL,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                verified_at TIMESTAMP
            )
        """)
        print("[OK] Table 'email_verifications' ready")
    except Exception as e:
        print(f"[SKIP] email_verifications table: {e}")

    # Add user_id to reminders
    try:
        cur.execute("ALTER TABLE reminders ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id)")
        print("[OK] Column 'reminders.user_id' ready")
    except Exception as e:
        print(f"[SKIP] reminders.user_id: {e}")

    # Add reminder_type to reminders
    try:
        cur.execute("ALTER TABLE reminders ADD COLUMN IF NOT EXISTS reminder_type VARCHAR(20) DEFAULT 'scheduled'")
        print("[OK] Column 'reminders.reminder_type' ready")
    except Exception as e:
        print(f"[SKIP] reminders.reminder_type: {e}")

    # Add message to reminders
    try:
        cur.execute("ALTER TABLE reminders ADD COLUMN IF NOT EXISTS message TEXT")
        print("[OK] Column 'reminders.message' ready")
    except Exception as e:
        print(f"[SKIP] reminders.message: {e}")

    cur.close()
    conn.close()

    print("=" * 50)
    print("Database migration completed successfully!")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback

    traceback.print_exc()
    exit(1)
