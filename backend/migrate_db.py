"""
Database Migration Script
Adds email verification columns to existing users table
Run this to update your database schema
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./todo_app.db"

print(f"Using database: {DATABASE_URL}")

# Create engine
engine = create_engine(DATABASE_URL)

def column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def table_exists(table_name):
    """Check if a table exists"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def migrate_database():
    """Add email verification columns to users table"""
    
    print("Starting database migration...")
    print("=" * 50)
    
    with engine.begin() as conn:
        # Check if is_email_verified column exists
        if column_exists('users', 'is_email_verified'):
            print("[OK] Column 'is_email_verified' already exists")
        else:
            print("Adding 'is_email_verified' column...")
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN is_email_verified BOOLEAN DEFAULT FALSE"
            ))
            print("[OK] Column 'is_email_verified' added successfully")
        
        # Check if email_verified_at column exists
        if column_exists('users', 'email_verified_at'):
            print("[OK] Column 'email_verified_at' already exists")
        else:
            print("Adding 'email_verified_at' column...")
            conn.execute(text(
                "ALTER TABLE users ADD COLUMN email_verified_at TIMESTAMP"
            ))
            print("[OK] Column 'email_verified_at' added successfully")
        
        # Check if email_verifications table exists
        if table_exists('email_verifications'):
            print("[OK] Table 'email_verifications' already exists")
        else:
            print("Creating 'email_verifications' table...")
            conn.execute(text("""
                CREATE TABLE email_verifications (
                    id UUID PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    is_verified BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    verified_at TIMESTAMP
                )
            """))
            print("[OK] Table 'email_verifications' created successfully")
        
        # Check if reminders table has user_id column
        if table_exists('reminders') and column_exists('reminders', 'user_id'):
            print("[OK] Column 'user_id' already exists in reminders table")
        elif table_exists('reminders'):
            print("Adding 'user_id' column to reminders table...")
            conn.execute(text(
                "ALTER TABLE reminders ADD COLUMN user_id UUID REFERENCES users(id)"
            ))
            print("[OK] Column 'user_id' added to reminders table")
        
        # Check if reminders table has reminder_type column
        if table_exists('reminders') and column_exists('reminders', 'reminder_type'):
            print("[OK] Column 'reminder_type' already exists in reminders table")
        elif table_exists('reminders'):
            print("Adding 'reminder_type' column to reminders table...")
            conn.execute(text(
                "ALTER TABLE reminders ADD COLUMN reminder_type VARCHAR(20) DEFAULT 'scheduled'"
            ))
            print("[OK] Column 'reminder_type' added to reminders table")
        
        # Check if reminders table has message column
        if table_exists('reminders') and column_exists('reminders', 'message'):
            print("[OK] Column 'message' already exists in reminders table")
        elif table_exists('reminders'):
            print("Adding 'message' column to reminders table...")
            conn.execute(text(
                "ALTER TABLE reminders ADD COLUMN message TEXT"
            ))
            print("[OK] Column 'message' added to reminders table")
    
    print("=" * 50)
    print("Database migration completed successfully!")
    print("\nAll email verification features are now available.")


if __name__ == "__main__":
    try:
        migrate_database()
    except Exception as e:
        print(f"Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
