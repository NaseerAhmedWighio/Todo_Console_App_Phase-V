"""
Verify the todos table schema
"""

from sqlmodel import Session, text

from app.database.session import engine


def check_schema():
    """Check the todos table schema"""

    with Session(engine) as session:
        result = session.exec(text("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'todos' 
            ORDER BY ordinal_position
        """))

        print("\n=== Todos Table Schema ===")
        for row in result:
            print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")

        # Also check recurring_tasks table exists
        try:
            result = session.exec(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'recurring_tasks'
            """))
            tables = list(result)
            if tables:
                print("\n=== recurring_tasks table exists ===")
            else:
                print("\n=== recurring_tasks table DOES NOT exist - creating it ===")
                # Create the table if it doesn't exist
                session.exec(text("""
                    CREATE TABLE IF NOT EXISTS recurring_tasks (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        title VARCHAR(255) NOT NULL,
                        description TEXT,
                        frequency VARCHAR(50) DEFAULT 'daily',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """))
                session.commit()
                print("Created recurring_tasks table")
        except Exception as e:
            print(f"Error checking recurring_tasks: {e}")


if __name__ == "__main__":
    check_schema()
