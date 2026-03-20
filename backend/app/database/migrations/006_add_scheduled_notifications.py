"""
Migration 006: Add scheduled notification fields to todos
Adds support for time-based email notifications
"""

import sqlalchemy as sa
from sqlmodel import SQLModel


def upgrade():
    """Add scheduled notification fields to todos table"""
    from app.database.session import engine

    # Add scheduled_time column
    with engine.connect() as conn:
        # Check if column already exists
        inspector = sa.inspect(engine)
        columns = [col["name"] for col in inspector.get_columns("todos")]

        if "scheduled_time" not in columns:
            conn.execute(
                sa.text(
                    "ALTER TABLE todos ADD COLUMN scheduled_time TIMESTAMP WITH TIME ZONE"
                )
            )
            conn.commit()
            print("Added scheduled_time column to todos")

        if "notification_sent" not in columns:
            conn.execute(
                sa.text("ALTER TABLE todos ADD COLUMN notification_sent BOOLEAN DEFAULT FALSE")
            )
            conn.commit()
            print("Added notification_sent column to todos")

        if "notified_at" not in columns:
            conn.execute(
                sa.text("ALTER TABLE todos ADD COLUMN notified_at TIMESTAMP WITH TIME ZONE")
            )
            conn.commit()
            print("Added notified_at column to todos")

        # Create index on scheduled_time for efficient querying
        indexes = [idx["name"] for idx in inspector.get_indexes("todos")]
        if "ix_todos_scheduled_time" not in indexes:
            conn.execute(
                sa.text("CREATE INDEX ix_todos_scheduled_time ON todos (scheduled_time)")
            )
            conn.commit()
            print("Created index on scheduled_time")

        if "ix_todos_notification_sent" not in indexes:
            conn.execute(
                sa.text("CREATE INDEX ix_todos_notification_sent ON todos (notification_sent)")
            )
            conn.commit()
            print("Created index on notification_sent")


def downgrade():
    """Remove scheduled notification fields from todos table"""
    from app.database.session import engine

    with engine.connect() as conn:
        inspector = sa.inspect(engine)
        columns = [col["name"] for col in inspector.get_columns("todos")]

        if "notified_at" in columns:
            conn.execute(sa.text("ALTER TABLE todos DROP COLUMN notified_at"))
            conn.commit()
            print("Removed notified_at column from todos")

        if "notification_sent" in columns:
            conn.execute(sa.text("ALTER TABLE todos DROP COLUMN notification_sent"))
            conn.commit()
            print("Removed notification_sent column from todos")

        if "scheduled_time" in columns:
            conn.execute(sa.text("ALTER TABLE todos DROP COLUMN scheduled_time"))
            conn.commit()
            print("Removed scheduled_time column from todos")


if __name__ == "__main__":
    print("Running migration 006: Add scheduled notification fields")
    upgrade()
    print("Migration 006 completed successfully")
