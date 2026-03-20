"""
Dapr Notification Event Handler
Handles scheduled notification events from Dapr Cron binding
Sends email notifications to users for tasks at their scheduled time
Supports recurring patterns: daily, weekly, monthly, yearly, custom (e.g., pay bills)
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from sqlmodel import Session, select

from ..database.session import get_session
from ..models.recurring_task import RecurringTask
from ..models.todo import Todo
from ..models.user import User
from ..services.email_service import email_service

logger = logging.getLogger(__name__)


class ScheduledNotificationHandler:
    """Handler for scheduled notification events from Dapr"""

    def __init__(self, session: Session):
        self.session = session

    def get_due_notifications(self) -> List[Dict[str, Any]]:
        """
        Get all notifications that are due to be sent

        Returns:
            List of dictionaries containing notification data
        """
        now = datetime.now(timezone.utc)

        # Get all tasks that:
        # - Have a scheduled_time (reminder_time) <= now
        # - Are not completed
        # - User email is verified
        # - Haven't been notified yet for this occurrence
        statement = (
            select(Todo, User)
            .join(User, Todo.user_id == User.id)
            .where(Todo.scheduled_time <= now)
            .where(Todo.is_completed == False)
            .where(User.is_email_verified == True)
            .where(Todo.notification_sent == False)
        )

        results = self.session.exec(statement).all()
        notifications = []

        for todo, user in results:
            notifications.append(
                {
                    "todo": todo,
                    "user": user,
                    "scheduled_time": todo.scheduled_time,
                }
            )

        return notifications

    def send_notification(
        self, todo: Todo, user: User, scheduled_time: datetime
    ) -> bool:
        """
        Send notification email for a task

        Args:
            todo: The todo item
            user: The user who owns the task
            scheduled_time: When the notification was scheduled

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Format due date
            due_date_str = (
                todo.due_date.strftime("%B %d, %Y at %I:%M %p %Z")
                if todo.due_date
                else "No due date"
            )

            # Get recurrence pattern info if applicable
            recurrence_info = ""
            pattern_name = None
            if todo.is_recurring and todo.recurring_task_id:
                recurring_task = self.session.get(RecurringTask, todo.recurring_task_id)
                if recurring_task:
                    pattern_map = {
                        "daily": "Daily",
                        "weekly": "Weekly",
                        "monthly": "Monthly",
                        "yearly": "Yearly",
                        "pay_bills": "Pay Bills (Monthly)",
                        "biweekly": "Bi-Weekly",
                        "quarterly": "Quarterly",
                    }
                    pattern = pattern_map.get(
                        recurring_task.recurrence_pattern,
                        recurring_task.recurrence_pattern.title(),
                    )
                    pattern_name = recurring_task.recurrence_pattern
                    recurrence_info = f" ({pattern})"

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
                logger.info(
                    f"Sent scheduled notification for task {todo.id} to user {user.id}{recurrence_info}"
                )

                # Mark notification as sent
                todo.notification_sent = True
                todo.notified_at = datetime.now(timezone.utc)
                self.session.add(todo)
                self.session.commit()

                # For recurring tasks, prepare next occurrence
                if todo.is_recurring and todo.recurring_task_id:
                    self._schedule_next_recurring_occurrence(
                        todo, user, pattern_name
                    )

            return email_sent

        except Exception as e:
            logger.error(
                f"Failed to send scheduled notification for task {todo.id}: {str(e)}"
            )
            return False

    def _schedule_next_recurring_occurrence(
        self, todo: Todo, user: User, pattern_name: Optional[str]
    ) -> None:
        """
        Schedule the next occurrence of a recurring task

        Args:
            todo: Current todo instance
            user: User who owns the task
            pattern_name: Recurrence pattern name
        """
        try:
            if not todo.recurring_task_id:
                return

            recurring_task = self.session.get(RecurringTask, todo.recurring_task_id)
            if not recurring_task or not recurring_task.is_active:
                return

            # Check end conditions
            now = datetime.now(timezone.utc)
            if recurring_task.end_condition == "on_date" and recurring_task.end_date:
                if now > recurring_task.end_date.replace(tzinfo=timezone.utc):
                    return

            # Calculate next occurrence
            current_due = todo.due_date or now
            next_due = self._calculate_next_occurrence(
                pattern_name or "monthly",
                recurring_task.interval,
                current_due,
                recurring_task.by_weekday,
                recurring_task.by_monthday,
                recurring_task.by_month,
            )

            # Update recurring task's next due date
            recurring_task.next_due_date = next_due
            recurring_task.last_generated_date = now
            self.session.add(recurring_task)

            # Create next todo instance
            base_task = self.session.get(Todo, recurring_task.task_id)
            if base_task:
                next_todo = Todo(
                    user_id=user.id,
                    title=base_task.title.replace(" (Recurring)", ""),
                    description=base_task.description,
                    due_date=next_due,
                    scheduled_time=next_due - timedelta(hours=1),  # Notify 1 hour before
                    priority=base_task.priority,
                    is_recurring=True,
                    recurring_task_id=recurring_task.id,
                    series_id=recurring_task.series_id or recurring_task.id,
                    notification_sent=False,
                    timezone=user.timezone,
                )
                self.session.add(next_todo)
                self.session.commit()
                logger.info(
                    f"Scheduled next recurring occurrence for task {todo.id} at {next_due}"
                )

        except Exception as e:
            logger.error(f"Failed to schedule next recurring occurrence: {str(e)}")
            self.session.rollback()

    def _calculate_next_occurrence(
        self,
        pattern: str,
        interval: int,
        base_date: datetime,
        by_weekday: Optional[str] = None,
        by_monthday: Optional[int] = None,
        by_month: Optional[str] = None,
    ) -> datetime:
        """
        Calculate next occurrence based on pattern

        Supported patterns:
        - daily: Every day
        - weekly: Every week
        - monthly: Every month (e.g., pay bills on 1st)
        - yearly: Every year
        - biweekly: Every 2 weeks
        - quarterly: Every 3 months
        - pay_bills: Alias for monthly on specific day
        - custom: Custom interval in days

        Args:
            pattern: Recurrence pattern
            interval: Interval multiplier
            base_date: Base date for calculation
            by_weekday: Comma-separated weekdays (0-6, 0=Monday)
            by_monthday: Day of month (1-31)
            by_month: Comma-separated months (1-12)

        Returns:
            Next occurrence datetime
        """
        if base_date.tzinfo is None:
            base_date = base_date.replace(tzinfo=timezone.utc)

        if pattern == "daily":
            return base_date + timedelta(days=interval)

        elif pattern == "weekly":
            if by_weekday:
                weekdays = [int(d.strip()) for d in by_weekday.split(",")]
                current_weekday = base_date.weekday()
                days_ahead = min(
                    (d - current_weekday) % 7 for d in weekdays
                ) or 7
                return base_date + timedelta(days=days_ahead)
            return base_date + timedelta(weeks=interval)

        elif pattern == "biweekly":
            return base_date + timedelta(weeks=2 * interval)

        elif pattern == "monthly" or pattern == "pay_bills":
            if by_monthday:
                next_date = base_date + relativedelta(months=interval)
                try:
                    return next_date.replace(day=by_monthday)
                except ValueError:
                    # Handle months with fewer days
                    return next_date.replace(day=1)
            return base_date + relativedelta(months=interval)

        elif pattern == "quarterly":
            if by_monthday:
                next_date = base_date + relativedelta(months=3 * interval)
                try:
                    return next_date.replace(day=by_monthday)
                except ValueError:
                    return next_date.replace(day=1)
            return base_date + relativedelta(months=3 * interval)

        elif pattern == "yearly":
            if by_month:
                months = [int(m.strip()) for m in by_month.split(",")]
                current_month = base_date.month
                months_ahead = min(
                    (m - current_month) % 12 for m in months
                ) or 12
                next_date = base_date + relativedelta(months=months_ahead)
                if by_monthday:
                    try:
                        return next_date.replace(day=by_monthday)
                    except ValueError:
                        return next_date.replace(day=1)
            return base_date + relativedelta(years=interval)

        else:  # custom pattern (interval in days)
            return base_date + timedelta(days=interval)

    def process_all_notifications(self) -> Dict[str, int]:
        """
        Process and send all due notifications

        Returns:
            Dictionary with statistics about sent notifications
        """
        due_notifications = self.get_due_notifications()

        stats = {"total": len(due_notifications), "sent": 0, "failed": 0}

        for notification in due_notifications:
            if self.send_notification(
                notification["todo"], notification["user"], notification["scheduled_time"]
            ):
                stats["sent"] += 1
            else:
                stats["failed"] += 1

        logger.info(
            f"Scheduled notification processing completed: {stats['sent']} sent, "
            f"{stats['failed']} failed"
        )

        return stats


def handle_scheduled_notification_event(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle incoming scheduled notification event from Dapr

    Args:
        event_data: Event data from Dapr binding

    Returns:
        Response dictionary with processing results
    """
    logger.info(f"Received scheduled notification event: {event_data}")

    try:
        session = next(get_session())
        try:
            handler = ScheduledNotificationHandler(session)
            stats = handler.process_all_notifications()
            return {"success": True, "stats": stats}
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to process scheduled notifications: {str(e)}")
        return {"success": False, "error": str(e)}


def handle_recurring_notification_event(
    event_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Handle recurring task notification event from Dapr

    Args:
        event_data: Event data containing recurring task information

    Returns:
        Response dictionary with processing results
    """
    logger.info(f"Received recurring notification event: {event_data}")

    try:
        session = next(get_session())
        try:
            from ..services.recurring_notification_service import (
                RecurringNotificationService,
            )

            service = RecurringNotificationService(session)
            stats = service.process_recurring_notifications()
            return {"success": True, "stats": stats}
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to process recurring notifications: {str(e)}")
        return {"success": False, "error": str(e)}
