"""
Migration: Extend Task Model with Advanced Features
Created: 2026-02-19
Description: Adds priority, due_date, timezone, is_recurring, recurring_task_id columns and search vector
"""

from sqlalchemy import text


def upgrade():
    """Apply migration - extend todos table"""
    
    from backend.app.database.session import engine
    with engine.connect() as conn:
        # Add priority column
        conn.execute(text("""
            ALTER TABLE todos 
            ADD COLUMN IF NOT EXISTS priority VARCHAR(20) NOT NULL DEFAULT 'medium',
            ADD CONSTRAINT chk_priority CHECK (priority IN ('low', 'medium', 'high', 'urgent'))
        """))
        
        # Add due_date column
        conn.execute(text("""
            ALTER TABLE todos 
            ADD COLUMN IF NOT EXISTS due_date TIMESTAMP
        """))
        
        # Add timezone column
        conn.execute(text("""
            ALTER TABLE todos 
            ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC'
        """))
        
        # Add is_recurring column
        conn.execute(text("""
            ALTER TABLE todos 
            ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN NOT NULL DEFAULT FALSE
        """))
        
        # Add recurring_task_id foreign key
        conn.execute(text("""
            ALTER TABLE todos 
            ADD COLUMN IF NOT EXISTS recurring_task_id UUID REFERENCES recurring_tasks(id)
        """))
        
        # Add search_vector column for full-text search
        conn.execute(text("""
            ALTER TABLE todos 
            ADD COLUMN IF NOT EXISTS search_vector tsvector
            GENERATED ALWAYS AS (
                to_tsvector('english',
                    coalesce(title, '') || ' ' ||
                    coalesce(description, '') || ' ' ||
                    coalesce(priority, '')
                )
            ) STORED
        """))
        
        # Create indexes for performance
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_priority ON todos(priority)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON todos(due_date)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_is_recurring ON todos(is_recurring)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_recurring_id ON todos(recurring_task_id)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_user_priority ON todos(user_id, priority)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_user_due_date ON todos(user_id, due_date)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_user_status_priority ON todos(user_id, is_completed, priority)"))
        
        # Create GIN index for full-text search
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_tasks_search_vector ON todos USING GIN (search_vector)"))
        
        conn.commit()
    
    print("✓ Extended todos table with: priority, due_date, timezone, is_recurring, recurring_task_id, search_vector")
    print("✓ Created indexes: idx_tasks_priority, idx_tasks_due_date, idx_tasks_is_recurring, idx_tasks_recurring_id, idx_tasks_search_vector")


def downgrade():
    """Rollback migration - remove new columns"""
    from backend.app.database.session import engine
    with engine.connect() as conn:
        # Drop indexes
        conn.execute(text("DROP INDEX IF EXISTS idx_tasks_search_vector"))
        conn.execute(text("DROP INDEX IF EXISTS idx_tasks_user_status_priority"))
        conn.execute(text("DROP INDEX IF EXISTS idx_tasks_user_due_date"))
        conn.execute(text("DROP INDEX IF EXISTS idx_tasks_user_priority"))
        conn.execute(text("DROP INDEX IF EXISTS idx_tasks_recurring_id"))
        conn.execute(text("DROP INDEX IF EXISTS idx_tasks_is_recurring"))
        conn.execute(text("DROP INDEX IF EXISTS idx_tasks_due_date"))
        conn.execute(text("DROP INDEX IF EXISTS idx_tasks_priority"))
        
        # Drop columns
        conn.execute(text("ALTER TABLE todos DROP COLUMN IF EXISTS search_vector"))
        conn.execute(text("ALTER TABLE todos DROP COLUMN IF EXISTS recurring_task_id"))
        conn.execute(text("ALTER TABLE todos DROP COLUMN IF EXISTS is_recurring"))
        conn.execute(text("ALTER TABLE todos DROP COLUMN IF EXISTS timezone"))
        conn.execute(text("ALTER TABLE todos DROP COLUMN IF EXISTS due_date"))
        conn.execute(text("ALTER TABLE todos DROP COLUMN IF EXISTS priority"))
        
        # Drop constraint
        conn.execute(text("ALTER TABLE todos DROP CONSTRAINT IF EXISTS chk_priority"))
        
        conn.commit()
    
    print("✓ Removed advanced feature columns from todos table")


if __name__ == "__main__":
    upgrade()
