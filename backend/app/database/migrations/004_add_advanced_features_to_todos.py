"""
Migration 004: Add advanced features columns to todos table

This migration adds the following columns to the todos table:
- timezone: VARCHAR(50) DEFAULT 'UTC'
- is_recurring: BOOLEAN DEFAULT FALSE
- recurring_task_id: UUID (nullable, foreign key to recurring_tasks)

Run this migration to update existing todos table schema.
"""

from sqlmodel import Session, text

from app.database.session import engine


def run_migration():
    """Run the migration to add advanced features columns to todos table"""

    with Session(engine) as session:
        # Check if columns already exist before adding them
        # We'll use raw SQL to add the columns if they don't exist

        # Add timezone column
        try:
            session.exec(text("""
                ALTER TABLE todos 
                ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'UTC'
            """))
            print("Added 'timezone' column to todos table")
        except Exception as e:
            print(f"Note: {e}")

        # Add is_recurring column
        try:
            session.exec(text("""
                ALTER TABLE todos 
                ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT FALSE
            """))
            print("Added 'is_recurring' column to todos table")
        except Exception as e:
            print(f"Note: {e}")

        # Add recurring_task_id column
        try:
            session.exec(text("""
                ALTER TABLE todos 
                ADD COLUMN IF NOT EXISTS recurring_task_id UUID
            """))
            print("Added 'recurring_task_id' column to todos table")
        except Exception as e:
            print(f"Note: {e}")

        # Add foreign key constraint for recurring_task_id
        try:
            session.exec(text("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.table_constraints 
                        WHERE constraint_name = 'todos_recurring_task_id_fkey'
                    ) THEN
                        ALTER TABLE todos 
                        ADD CONSTRAINT todos_recurring_task_id_fkey 
                        FOREIGN KEY (recurring_task_id) 
                        REFERENCES recurring_tasks(id);
                    END IF;
                END $$;
            """))
            print("Added foreign key constraint for 'recurring_task_id'")
        except Exception as e:
            print(f"Note: {e}")

        session.commit()
        print("Migration 004 completed successfully!")


if __name__ == "__main__":
    run_migration()
