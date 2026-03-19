"""
Celery Application Configuration
Background task processing for reminders and recurring tasks
"""

import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "todo_app",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "backend.app.workers.reminder_worker",
        "backend.app.workers.recurring_worker",
        "backend.app.workers.event_worker",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Task execution settings
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=240,  # 4 minutes soft limit
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Rate limiting
    worker_prefetch_multiplier=1,
    # Scheduled tasks (Celery Beat)
    beat_schedule={
        # Process reminders every minute (FOR TESTING)
        "process-reminders-every-minute": {
            "task": "backend.app.workers.reminder_worker.process_due_reminders",
            "schedule": crontab(minute="*/1"),  # Every minute
        },
        # Generate recurring tasks every minute (FOR TESTING)
        # In production, change to: crontab(minute='0')  # Every hour
        "generate-recurring-tasks-every-minute": {
            "task": "backend.app.workers.recurring_worker.generate_recurring_instances",
            "schedule": crontab(minute="*/1"),  # Every minute for testing
        },
        # Cleanup old events daily
        "cleanup-old-events-daily": {
            "task": "backend.app.workers.event_worker.cleanup_old_events",
            "schedule": crontab(hour="3", minute="0"),  # Daily at 3 AM
        },
    },
)


# Auto-discover tasks in workers package
celery_app.autodiscover_tasks(["backend.app.workers"])


if __name__ == "__main__":
    # Test Celery configuration
    print(f"Celery broker: {CELERY_BROKER_URL}")
    print(f"Celery backend: {CELERY_RESULT_BACKEND}")
    print("Scheduled tasks:")
    for task_name, task_config in celery_app.conf.beat_schedule.items():
        print(f"  - {task_name}: {task_config['task']}")
