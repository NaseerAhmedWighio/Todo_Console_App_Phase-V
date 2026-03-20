"""
Recurring Notification Service
Handles recurring task notifications with pattern support
(daily, weekly, monthly, yearly, pay bills, custom intervals)
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta
from sqlmodel import Session, select

from ..models.recurring_task import RecurringTask
from ..models.todo import Todo
from ..models.user import User
from ..services.email_service import email_service

logger = logging.getLogger(__name__)


class RecurringNotificationService:
    """Service for handling recurring task notifications"""

    def __init__(self, session: Session):
        self.session = session

    def get_active_recurring_tasks(self) -> List[RecurringTask]:
        """
        Get all active recurring tasks

        Returns:
            List of active recurring task configurations
        """
        statement = select(RecurringTask).where(RecurringTask.is_active == True)
        return list(self.session.exec(statement).all())

    def calculate_next_occurrence(
        self,
        recurrence_pattern: str,
        interval: int,
        last_occurrence: Optional[datetime],
        by_weekday: Optional[str] = None,
        by_monthday: Optional[int] = None,
        by_month: Optional[str] = None,
    ) -> datetime:
        """
        Calculate the next occurrence date based on recurrence pattern

        Supported patterns:
        - daily: Every day at the same time
        - weekly: Every week on the same day
        - monthly: Every month (e.g., pay bills on 1st)
        - yearly: Every year
        - biweekly: Every 2 weeks
        - quarterly: Every 3 months
        - pay_bills: Monthly bill payment pattern
        - custom: Custom interval

        Args:
            recurrence_pattern: Pattern type
            interval: Interval between occurrences
            last_occurrence: Last occurrence date
            by_weekday: Comma-separated weekdays (0-6, 0=Monday)
            by_monthday: Day of month (1-31)
            by_month: Comma-separated months (1-12)

        Returns:
            Next occurrence datetime
        """
        now = datetime.now(timezone.utc)

        # Use last_occurrence or now as base
        base_date = last_occurrence if last_occurrence else now
        if base_date.tzinfo is None:
            base_date = base_date.replace(tzinfo=timezone.utc)

        if recurrence_pattern == "daily":
            next_date = base_date + timedelta(days=interval)

        elif recurrence_pattern == "biweekly":
            next_date = base_date + timedelta(weeks=2 * interval)

        elif recurrence_pattern == "weekly":
            if by_weekday:
                # Parse weekdays (0=Monday, 6=Sunday)
                weekdays = [int(d.strip()) for d in by_weekday.split(",")]
                current_weekday = base_date.weekday()
                days_ahead = min(
                    (d - current_weekday) % 7 for d in weekdays
                ) or 7
                next_date = base_date + timedelta(days=days_ahead)
            else:
                next_date = base_date + timedelta(weeks=interval)

        elif recurrence_pattern == "monthly" or recurrence_pattern == "pay_bills":
            if by_monthday:
                # Set to specific day of month
                next_date = base_date + relativedelta(months=interval)
                try:
                    next_date = next_date.replace(day=by_monthday)
                except ValueError:
                    # Handle months with fewer days (e.g., 31st in February)
                    next_date = next_date.replace(day=1)
            else:
                next_date = base_date + relativedelta(months=interval)

        elif recurrence_pattern == "quarterly":
            if by_monthday:
                next_date = base_date + relativedelta(months=3 * interval)
                try:
                    next_date = next_date.replace(day=by_monthday)
                except ValueError:
                    next_date = next_date.replace(day=1)
            else:
                next_date = base_date + relativedelta(months=3 * interval)

        elif recurrence_pattern == "yearly":
            if by_month:
                months = [int(m.strip()) for m in by_month.split(",")]
                current_month = base_date.month
                # Find next month in the list
                months_ahead = min(
                    (m - current_month) % 12 for m in months
                ) or 12
                next_date = base_date + relativedelta(months=months_ahead)
                if by_monthday:
                    try:
                        next_date = next_date.replace(day=by_monthday)
                    except ValueError:
                        next_date = next_date.replace(day=1)
            else:
                next_date = base_date + relativedelta(years=interval)

        else:  # custom pattern
            next_date = base_date + timedelta(days=interval)

        return next_date

    def should_send_notification(
        self, recurring_task: RecurringTask, now: datetime
    ) -> bool:
        """
        Check if a notification should be sent for this recurring task

        Args:
            recurring_task: Recurring task configuration
            now: Current datetime

        Returns:
            True if notification should be sent
        """
        # Check if end condition is met
        if recurring_task.end_condition == "on_date" and recurring_task.end_date:
            if now > recurring_task.end_date.replace(tzinfo=timezone.utc):
                return False

        if recurring_task.end_condition == "after_occurrences":
            # Count occurrences since creation
            if recurring_task.created_at and recurring_task.end_occurrences:
                total_days = (now - recurring_task.created_at.replace(tzinfo=timezone.utc)).days
                interval_days = recurring_task.interval
                if recurring_task.recurrence_pattern == "weekly":
                    interval_days *= 7
                elif recurring_task.recurrence_pattern == "monthly" or recurring_task.recurrence_pattern == "pay_bills":
                    interval_days *= 30
                elif recurring_task.recurrence_pattern == "yearly":
                    interval_days *= 365
                elif recurring_task.recurrence_pattern == "quarterly":
                    interval_days *= 90
                elif recurring_task.recurrence_pattern == "biweekly":
                    interval_days *= 14

                occurrences = total_days // max(interval_days, 1)
                if occurrences >= recurring_task.end_occurrences:
                    return False

        # Check if it's time for next occurrence
        next_due = recurring_task.next_due_date
        if not next_due:
            return True

        if next_due.tzinfo is None:
            next_due = next_due.replace(tzinfo=timezone.utc)

        return now >= next_due

    def create_recurring_todo_instance(
        self,
        recurring_task: RecurringTask,
        user: User,
        occurrence_date: datetime,
    ) -> Optional[Todo]:
        """
        Create a new todo instance for a recurring task

        Args:
            recurring_task: Recurring task configuration
            user: User who owns the task
            occurrence_date: Date for this occurrence

        Returns:
            Created Todo instance or None
        """
        try:
            # Get the base task
            base_task = self.session.get(Todo, recurring_task.task_id)
            if not base_task:
                logger.error(f"Base task not found: {recurring_task.task_id}")
                return None

            # Remove "(Recurring)" suffix if it exists to avoid duplication
            title = base_task.title.replace(" (Recurring)", "")

            # Create new instance
            new_todo = Todo(
                user_id=user.id,
                title=f"{title} (Recurring)",
                description=base_task.description,
                due_date=occurrence_date,
                scheduled_time=occurrence_date - timedelta(hours=1),  # Notify 1 hour before
                priority=base_task.priority,
                is_recurring=True,
                recurring_task_id=recurring_task.id,
                series_id=recurring_task.series_id or recurring_task.id,
                notification_sent=False,
                timezone=user.timezone or "UTC",
            )

            self.session.add(new_todo)
            self.session.commit()
            self.session.refresh(new_todo)

            logger.info(
                f"Created recurring todo instance {new_todo.id} for {occurrence_date}"
            )

            return new_todo

        except Exception as e:
            logger.error(f"Failed to create recurring todo instance: {str(e)}")
            self.session.rollback()
            return None

    def update_recurring_task_next_due(
        self, recurring_task: RecurringTask, next_date: datetime
    ) -> None:
        """
        Update the next due date for a recurring task

        Args:
            recurring_task: Recurring task configuration
            next_date: Next occurrence date
        """
        recurring_task.next_due_date = next_date
        recurring_task.last_generated_date = datetime.now(timezone.utc)
        self.session.add(recurring_task)
        self.session.commit()

    def send_recurring_notification(
        self, todo: Todo, user: User, pattern: str
    ) -> bool:
        """
        Send notification for a recurring task instance

        Args:
            todo: Todo instance
            user: User who owns the task
            pattern: Recurrence pattern name

        Returns:
            True if email sent successfully
        """
        try:
            due_date_str = (
                todo.due_date.strftime("%B %d, %Y at %I:%M %p %Z")
                if todo.due_date
                else "No due date"
            )

            # Get recurrence pattern display name
            pattern_map = {
                "daily": "Daily",
                "weekly": "Weekly",
                "monthly": "Monthly",
                "yearly": "Yearly",
                "biweekly": "Bi-Weekly",
                "quarterly": "Quarterly",
                "pay_bills": "Pay Bills (Monthly)",
            }
            pattern_text = pattern_map.get(pattern, pattern.title())

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
                    f"Sent recurring notification for task {todo.id} to user {user.id} ({pattern_text})"
                )
                todo.notification_sent = True
                todo.notified_at = datetime.now(timezone.utc)
                self.session.add(todo)
                self.session.commit()

            return email_sent

        except Exception as e:
            logger.error(f"Failed to send recurring notification: {str(e)}")
            return False

    def process_recurring_notifications(self) -> Dict[str, int]:
        """
        Process all recurring tasks and send notifications for due occurrences

        Returns:
            Dictionary with processing statistics
        """
        now = datetime.now(timezone.utc)
        recurring_tasks = self.get_active_recurring_tasks()

        stats = {
            "total_recurring": len(recurring_tasks),
            "processed": 0,
            "notifications_sent": 0,
            "instances_created": 0,
            "failed": 0,
        }

        for recurring_task in recurring_tasks:
            try:
                # Get user who owns the task
                base_task = self.session.get(Todo, recurring_task.task_id)
                if not base_task:
                    continue

                user = self.session.get(User, base_task.user_id)
                if not user or not user.is_email_verified:
                    continue

                # Check if this recurring task is due
                if self.should_send_notification(recurring_task, now):
                    # Calculate next occurrence
                    next_occurrence = self.calculate_next_occurrence(
                        recurrence_pattern=recurring_task.recurrence_pattern,
                        interval=recurring_task.interval,
                        last_occurrence=recurring_task.last_generated_date,
                        by_weekday=recurring_task.by_weekday,
                        by_monthday=recurring_task.by_monthday,
                        by_month=recurring_task.by_month,
                    )

                    # Create new todo instance for this occurrence
                    new_todo = self.create_recurring_todo_instance(
                        recurring_task=recurring_task,
                        user=user,
                        occurrence_date=next_occurrence,
                    )

                    if new_todo:
                        stats["instances_created"] += 1

                        # Send notification if scheduled time has arrived
                        if new_todo.scheduled_time and new_todo.scheduled_time <= now:
                            if self.send_recurring_notification(
                                new_todo, user, recurring_task.recurrence_pattern
                            ):
                                stats["notifications_sent"] += 1
                            else:
                                stats["failed"] += 1

                    # Update next due date
                    self.update_recurring_task_next_due(
                        recurring_task, next_occurrence
                    )
                    stats["processed"] += 1

            except Exception as e:
                logger.error(
                    f"Failed to process recurring task {recurring_task.id}: {str(e)}"
                )
                stats["failed"] += 1

        logger.info(f"Recurring notification processing completed: {stats}")
        return stats
