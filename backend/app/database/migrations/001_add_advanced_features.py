"""
Migration: Add Advanced Todo Features Tables
Created: 2026-02-19
Description: Creates tables for tags, task_tags, reminders, recurring_tasks, and domain_events
"""

from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, ForeignKey
from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import text


def upgrade():
    """Apply migration - create new tables"""
    
    # Tags table
    create_tags_sql = """
    CREATE TABLE IF NOT EXISTS tags (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name VARCHAR(50) NOT NULL,
        color VARCHAR(7) DEFAULT '#6B7280',
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        CONSTRAINT unique_user_tag_name UNIQUE (user_id, name)
    );
    """
    
    # Task-Tag join table (many-to-many)
    create_task_tags_sql = """
    CREATE TABLE IF NOT EXISTS task_tags (
        task_id UUID NOT NULL REFERENCES todos(id) ON DELETE CASCADE,
        tag_id UUID NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        PRIMARY KEY (task_id, tag_id)
    );
    """
    
    # Reminders table
    create_reminders_sql = """
    CREATE TABLE IF NOT EXISTS reminders (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        task_id UUID NOT NULL REFERENCES todos(id) ON DELETE CASCADE,
        timing_minutes INTEGER DEFAULT 0,
        timing_days INTEGER,
        delivery_channel VARCHAR(20) NOT NULL DEFAULT 'in_app',
        scheduled_time TIMESTAMP NOT NULL,
        sent_at TIMESTAMP,
        status VARCHAR(20) NOT NULL DEFAULT 'pending',
        error_message TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        CONSTRAINT chk_reminder_timing CHECK (
            timing_minutes >= 0 OR timing_days IS NULL OR timing_days >= 0
        ),
        CONSTRAINT chk_delivery_channel CHECK (
            delivery_channel IN ('in_app', 'email', 'web_push', 'sms')
        ),
        CONSTRAINT chk_reminder_status CHECK (
            status IN ('pending', 'sent', 'failed', 'cancelled')
        )
    );
    """
    
    # Recurring tasks table
    create_recurring_tasks_sql = """
    CREATE TABLE IF NOT EXISTS recurring_tasks (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        series_id UUID,
        task_id UUID NOT NULL REFERENCES todos(id) ON DELETE CASCADE,
        recurrence_pattern VARCHAR(50) NOT NULL,
        interval INTEGER NOT NULL DEFAULT 1,
        by_weekday VARCHAR(50),
        by_monthday INTEGER,
        by_month VARCHAR(50),
        end_condition VARCHAR(20) NOT NULL DEFAULT 'never',
        end_occurrences INTEGER,
        end_date TIMESTAMP,
        last_generated_date TIMESTAMP,
        next_due_date TIMESTAMP,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        CONSTRAINT chk_recurrence_pattern CHECK (
            recurrence_pattern IN ('daily', 'weekly', 'monthly', 'yearly', 'custom')
        ),
        CONSTRAINT chk_interval CHECK (interval >= 1),
        CONSTRAINT chk_end_condition CHECK (
            end_condition IN ('never', 'after_occurrences', 'on_date')
        ),
        CONSTRAINT chk_by_monthday CHECK (
            by_monthday IS NULL OR (by_monthday >= 1 AND by_monthday <= 31)
        )
    );
    """
    
    # Domain events table
    create_domain_events_sql = """
    CREATE TABLE IF NOT EXISTS domain_events (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        event_type VARCHAR(50) NOT NULL,
        aggregate_id UUID NOT NULL,
        aggregate_type VARCHAR(50) NOT NULL,
        user_id UUID NOT NULL REFERENCES users(id),
        payload JSON NOT NULL,
        metadata JSON,
        published BOOLEAN NOT NULL DEFAULT FALSE,
        published_at TIMESTAMP,
        processed BOOLEAN NOT NULL DEFAULT FALSE,
        processed_at TIMESTAMP,
        error_message TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        CONSTRAINT chk_event_type CHECK (
            event_type IN (
                'task.created', 'task.updated', 'task.completed', 'task.deleted',
                'task.reminder_sent', 'recurring.instance_generated'
            )
        )
    );
    """
    
    # Dapr state table
    create_dapr_state_sql = """
    CREATE TABLE IF NOT EXISTS dapr_state (
        key TEXT NOT NULL,
        value JSONB NOT NULL,
        version BIGINT,
        is_deleted BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        PRIMARY KEY (key)
    );
    """
    
    # Execute all table creation statements
    from backend.app.database.session import engine
    with engine.connect() as conn:
        conn.execute(text(create_tags_sql))
        conn.execute(text(create_task_tags_sql))
        conn.execute(text(create_reminders_sql))
        conn.execute(text(create_recurring_tasks_sql))
        conn.execute(text(create_domain_events_sql))
        conn.execute(text(create_dapr_state_sql))
        conn.commit()
    
    print("✓ Created tables: tags, task_tags, reminders, recurring_tasks, domain_events, dapr_state")


def downgrade():
    """Rollback migration - drop new tables"""
    from backend.app.database.session import engine
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS dapr_state CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS domain_events CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS recurring_tasks CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS reminders CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS task_tags CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS tags CASCADE"))
        conn.commit()
    
    print("✓ Dropped tables: tags, task_tags, reminders, recurring_tasks, domain_events, dapr_state")


if __name__ == "__main__":
    upgrade()
