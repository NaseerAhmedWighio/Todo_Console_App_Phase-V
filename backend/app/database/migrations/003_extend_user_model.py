"""
Migration: Extend User Model with Preferences
Created: 2026-02-19
Description: Adds timezone, notification_preferences, default_task_priority columns
"""

from sqlalchemy import text


def upgrade():
    """Apply migration - extend users table"""

    from app.database.session import engine
    with engine.connect() as conn:
        # Add timezone column
        conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) NOT NULL DEFAULT 'UTC'
        """))
        
        # Add notification_preferences column (JSON)
        conn.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS notification_preferences JSON
        """))
        
        # Add default_task_priority column
        conn.execute(text("""
            ALTER TABLE users
            ADD COLUMN IF NOT EXISTS default_task_priority VARCHAR(20) DEFAULT 'medium'
        """))

        # Add constraint separately (drop first if exists to allow re-runs)
        conn.execute(text("""
            ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_default_priority
        """))
        conn.execute(text("""
            ALTER TABLE users
            ADD CONSTRAINT chk_default_priority CHECK (
                default_task_priority IN ('low', 'medium', 'high', 'urgent')
            )
        """))
        
        # Set default notification preferences for existing users
        conn.execute(text("""
            UPDATE users
            SET notification_preferences = '{"in_app": true, "email": false, "web_push": false, "sms": false}'::json
            WHERE notification_preferences IS NULL
        """))

        conn.commit()

    print("Extended users table with: timezone, notification_preferences, default_task_priority")


def downgrade():
    """Rollback migration - remove new columns"""
    from app.database.session import engine
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS default_task_priority"))
        conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS notification_preferences"))
        conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS timezone"))
        conn.execute(text("ALTER TABLE users DROP CONSTRAINT IF EXISTS chk_default_priority"))
        conn.commit()
    
    print("✓ Removed preference columns from users table")


if __name__ == "__main__":
    upgrade()
