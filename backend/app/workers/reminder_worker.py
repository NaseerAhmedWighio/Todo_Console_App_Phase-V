"""
Task Reminder Worker
Sends email reminders for upcoming tasks based on configured reminder settings
"""

import logging
from datetime import datetime
from typing import List

from celery import shared_task
from sqlmodel import Session, select

from ..models.reminder import Reminder
from ..models.todo import Todo
from ..models.user import User
from ..services.email_service import email_service

logger = logging.getLogger(__name__)


class TaskReminderWorker:
    """Worker that sends task reminder emails based on configured reminders"""

    def __init__(self, session: Session):
        self.session = session

    def get_due_reminders(self) -> List[tuple[Reminder, Todo, User]]:
        """
        Get reminders that are due to be sent (scheduled_time <= now and status = pending)

        Returns:
            List of tuples containing (Reminder, Todo, User) pairs
        """
        now = datetime.utcnow()

        # Get all reminders that are:
        # - Pending (not yet sent)
        # - Scheduled time has arrived
        # - Task is not completed
        # - User email is verified
        statement = (
            select(Reminder, Todo, User)
            .join(Todo, Reminder.task_id == Todo.id)
            .join(User, Reminder.user_id == User.id)
            .where(Reminder.status == "pending")
            .where(Reminder.scheduled_time <= now)
            .where(Todo.is_completed == False)
            .where(User.is_email_verified == True)
        )

        results = self.session.exec(statement).all()
        return [(reminder, todo, user) for reminder, todo, user in results]

    def send_reminder(self, reminder: Reminder, todo: Todo, user: User) -> bool:
        """
        Send reminder email for a task

        Args:
            reminder: The reminder record
            todo: The todo item
            user: The user who owns the task

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Format due date
            due_date_str = todo.due_date.strftime("%B %d, %Y at %I:%M %p UTC") if todo.due_date else "No due date"

            # Send email
            email_sent = email_service.send_task_reminder_email(
                to_email=user.email,
                user_name=user.name or user.email.split("@")[0],
                task_title=todo.title,
                task_description=todo.description,
                due_date=due_date_str,
                priority=todo.priority or "medium",
            )

            if email_sent:
                logger.info(f"Sent reminder email for task {todo.id} to user {user.id}")

                # Update reminder record
                reminder.status = "sent"
                reminder.sent_at = datetime.utcnow()
                reminder.message = f"Reminder email sent for task: {todo.title}"
                self.session.add(reminder)
                self.session.commit()

            return email_sent

        except Exception as e:
            logger.error(f"Failed to send reminder for task {todo.id}: {str(e)}")
            reminder.status = "failed"
            reminder.error_message = str(e)
            self.session.add(reminder)
            self.session.commit()
            return False

    def send_all_reminders(self) -> dict:
        """
        Send reminders for all due reminders

        Returns:
            Dictionary with statistics about sent reminders
        """
        due_reminders = self.get_due_reminders()

        stats = {"total": len(due_reminders), "sent": 0, "failed": 0}

        for reminder, todo, user in due_reminders:
            # Send reminder
            if self.send_reminder(reminder, todo, user):
                stats["sent"] += 1
            else:
                stats["failed"] += 1

        logger.info(f"Reminder worker completed: {stats['sent']} sent, " f"{stats['failed']} failed")

        return stats


def run_reminder_worker():
    """
    Run the reminder worker
    This function can be called periodically (e.g., every minute) via cron or scheduler
    """
    from ..database.session import get_session

    session = next(get_session())
    try:
        worker = TaskReminderWorker(session)
        stats = worker.send_all_reminders()
        return stats
    finally:
        session.close()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_due_reminders(self):
    """
    Celery task to process and send due reminders
    Runs every minute via Celery Beat

    This only sends reminders for reminders that have been explicitly configured
    with a scheduled_time. It does NOT create automatic reminders for all tasks.

    Users must create a reminder via the API to receive notifications.
    """
    logger.info("Starting reminder processing...")

    try:
        from ..database.session import get_session

        session = next(get_session())
        try:
            worker = TaskReminderWorker(session)
            stats = worker.send_all_reminders()

            logger.info(f"Reminder processing completed: {stats}")
            return stats
        finally:
            session.close()

    except Exception as exc:
        logger.error(f"Reminder processing failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))
