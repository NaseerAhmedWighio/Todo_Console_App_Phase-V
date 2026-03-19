"""
Migration: Add Search Indexes and Search Vector Column
Created: 2026-02-20
Description: Adds search_vector column and GIN indexes for full-text search
"""

from sqlalchemy import text


def upgrade():
    """Apply migration - add search vector and indexes"""

    from app.database.session import engine

    with engine.connect() as conn:
        # Add search_vector column if it doesn't exist
        add_column_sql = """
        ALTER TABLE todos 
        ADD COLUMN IF NOT EXISTS search_vector tsvector
        """
        conn.execute(text(add_column_sql))

        # Create function to update search vector
        create_function_sql = """
        CREATE OR REPLACE FUNCTION todos_search_vector_update() RETURNS trigger AS $$
        BEGIN
          NEW.search_vector :=
            setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
            setweight(to_tsvector('english', coalesce(NEW.description, '')), 'B') ||
            setweight(to_tsvector('english', coalesce(NEW.priority, '')), 'C');
          RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
        """
        conn.execute(text(create_function_sql))

        # Create trigger to auto-update search vector
        create_trigger_sql = """
        DROP TRIGGER IF EXISTS tsvectorupdate ON todos;
        CREATE TRIGGER tsvectorupdate
          BEFORE UPDATE OR INSERT ON todos
          FOR EACH ROW EXECUTE FUNCTION todos_search_vector_update();
        """
        conn.execute(text(create_trigger_sql))

        # Populate existing rows
        populate_sql = """
        UPDATE todos SET search_vector =
          setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
          setweight(to_tsvector('english', coalesce(description, '')), 'B') ||
          setweight(to_tsvector('english', coalesce(priority, '')), 'C')
        """
        conn.execute(text(populate_sql))

        # Create GIN index for full-text search
        create_gin_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_todos_search_vector 
        ON todos USING GIN (search_vector)
        """
        conn.execute(text(create_gin_index_sql))

        # Create index for priority filtering
        create_priority_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_todos_priority 
        ON todos (priority)
        """
        conn.execute(text(create_priority_index_sql))

        # Create index for due date filtering
        create_due_date_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_todos_due_date 
        ON todos (due_date)
        """
        conn.execute(text(create_due_date_index_sql))

        # Create composite index for user filtering with priority
        create_composite_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_todos_user_priority 
        ON todos (user_id, priority)
        """
        conn.execute(text(create_composite_index_sql))

        # Create composite index for user filtering with due date
        create_user_due_date_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_todos_user_due_date 
        ON todos (user_id, due_date)
        """
        conn.execute(text(create_user_due_date_index_sql))

        # Commit all changes
        conn.commit()

    print("✓ Created search_vector column, trigger, and GIN indexes")
    print("✓ Created indexes: idx_todos_search_vector, idx_todos_priority, idx_todos_due_date")


def downgrade():
    """Rollback migration - drop search vector and indexes"""
    from app.database.session import engine

    with engine.connect() as conn:
        # Drop indexes
        conn.execute(text("DROP INDEX IF EXISTS idx_todos_search_vector"))
        conn.execute(text("DROP INDEX IF EXISTS idx_todos_priority"))
        conn.execute(text("DROP INDEX IF EXISTS idx_todos_due_date"))
        conn.execute(text("DROP INDEX IF EXISTS idx_todos_user_priority"))
        conn.execute(text("DROP INDEX IF EXISTS idx_todos_user_due_date"))

        # Drop trigger
        conn.execute(text("DROP TRIGGER IF EXISTS tsvectorupdate ON todos"))

        # Drop function
        conn.execute(text("DROP FUNCTION IF EXISTS todos_search_vector_update()"))

        # Drop column
        conn.execute(text("ALTER TABLE todos DROP COLUMN IF EXISTS search_vector"))

        conn.commit()

    print("✓ Dropped search_vector column and indexes")


if __name__ == "__main__":
    upgrade()
