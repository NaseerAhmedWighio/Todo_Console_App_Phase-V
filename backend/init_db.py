"""
Initialize Database - Force create all tables
"""
import sys
sys.path.insert(0, '.')

from app.database.session import engine, create_db_and_tables
from sqlalchemy import text

# Drop all tables using raw SQL to avoid circular dependency issues
print("Dropping existing tables...")
try:
    with engine.connect() as conn:
        # Drop tables in reverse order of dependencies
        tables_to_drop = [
            'messages',
            'conversations',
            'task_tags',
            'tags',
            'reminders',
            'recurring_tasks',
            'todos',
            'users',
            'domain_events',
        ]
        for table_name in tables_to_drop:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
                print(f"  Dropped table: {table_name}")
            except Exception as e:
                print(f"  Error dropping {table_name}: {e}")
        conn.commit()
    print("All tables dropped successfully")
except Exception as e:
    print(f"Error dropping tables: {e}")

# Create all tables
print("\nCreating database tables...")
create_db_and_tables()

print("[OK] Database initialized successfully!")

# Verify tables
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"Tables created: {tables}")
