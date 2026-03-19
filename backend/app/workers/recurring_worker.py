"""
Recurring Task Worker
Celery tasks for generating recurring task instances
"""

import logging
from datetime import datetime, timedelta, timezone

import pytz
from celery import shared_task
from dateutil.rrule import DAILY, MINUTELY, MONTHLY, WEEKLY, YEARLY, rrule
from sqlmodel import Session, select

from ..database.session import engine
from ..events.schemas import EventTypes, KafkaTopics
from ..models.recurring_task import RecurringTask
from ..models.todo import Todo
from ..services.event_service import get_event_service

logger = logging.getLogger(__name__)

# Map pattern strings to dateutil constants
PATTERN_MAP = {
    "minutely": MINUTELY,
    "daily": DAILY,
    "weekly": WEEKLY,
    "monthly": MONTHLY,
    "yearly": YEARLY,
}


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def generate_recurring_instances(self):
    """
    Celery task to generate recurring task instances
    Runs every hour via Celery Beat
    """
    logger.info("Starting recurring task generation...")

    try:
        with Session(engine) as session:
            # Get all active recurring tasks that are due
            now = datetime.now(timezone.utc)
            statement = (
                select(RecurringTask)
                .where(RecurringTask.is_active == True)
                .where((RecurringTask.next_due_date <= now) | (RecurringTask.next_due_date == None))  # noqa: E711
                .limit(100)  # Process in batches
            )
            recurring_tasks = session.exec(statement).all()

            logger.info(f"Found {len(recurring_tasks)} recurring tasks to process")

            for recurring_task in recurring_tasks:
                try:
                    # Generate new instance
                    _generate_instance(recurring_task, session)
                except Exception as e:
                    logger.error(f"Error processing recurring task {recurring_task.id}: {e}")
                    # Mark as inactive on repeated failures
                    if self.request.retries >= self.max_retries:
                        recurring_task.is_active = False
                        session.add(recurring_task)

            session.commit()

        logger.info(f"Processed {len(recurring_tasks)} recurring tasks")
        return {"processed": len(recurring_tasks)}

    except Exception as exc:
        logger.error(f"Recurring task generation failed: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=300 * (2**self.request.retries))


def _generate_instance(recurring_task: RecurringTask, session: Session):
    """
    Generate a new task instance from a recurring task

    Args:
        recurring_task: RecurringTask to process
        session: Database session
    """
    # Get the base task
    base_task = session.get(Todo, recurring_task.task_id)
    if not base_task:
        logger.warning(f"Base task {recurring_task.task_id} not found for recurring task {recurring_task.id}")
        recurring_task.is_active = False
        session.add(recurring_task)
        return

    # Check end conditions
    if recurring_task.end_condition == "after_occurrences":
        # Count existing instances
        count_statement = select(Todo).where(Todo.recurring_task_id == recurring_task.id)
        existing_instances = session.exec(count_statement).all()
        if len(existing_instances) >= recurring_task.end_occurrences:
            logger.info(f"Recurring task {recurring_task.id} reached end occurrences")
            recurring_task.is_active = False
            session.add(recurring_task)
            return

    elif recurring_task.end_condition == "on_date":
        if recurring_task.end_date and datetime.now(timezone.utc) > recurring_task.end_date:
            logger.info(f"Recurring task {recurring_task.id} reached end date")
            recurring_task.is_active = False
            session.add(recurring_task)
            return

    # Create new task instance
    timezone_str = base_task.timezone or "UTC"
    tz = pytz.timezone(timezone_str)

    # Calculate new due date based on pattern
    new_due_date = _calculate_next_due_date(recurring_task, tz)

    # Clone the base task
    new_task = Todo(
        user_id=base_task.user_id,
        title=base_task.title,
        description=base_task.description,
        priority=base_task.priority,
        due_date=new_due_date,
        timezone=timezone_str,
        is_completed=False,
        is_recurring=False,  # Instance is not recurring, only the series is
        recurring_task_id=recurring_task.id,
    )

    session.add(new_task)
    session.flush()  # Get the new task ID

    # Calculate the NEXT occurrence after the one we just created
    next_due_date = _calculate_next_due_date(recurring_task, tz, new_due_date)

    # Update recurring task with next due date
    recurring_task.next_due_date = next_due_date
    recurring_task.last_generated_date = datetime.now(timezone.utc)

    session.add(recurring_task)
    session.commit()

    logger.info(f"Generated instance {new_task.id} for recurring task {recurring_task.id} (next due: {next_due_date})")

    # Publish event
    import asyncio

    event_service = get_event_service()
    asyncio.run(
        event_service.publish_and_track(
            event_type=EventTypes.RECURRING_INSTANCE_GENERATED,
            aggregate_id=new_task.id,
            aggregate_type="Task",
            user_id=base_task.user_id,
            payload={
                "recurring_task_id": str(recurring_task.id),
                "new_task_id": str(new_task.id),
                "due_date": new_due_date.isoformat() if new_due_date else None,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            topic=KafkaTopics.RECURRING,
        )
    )


def _calculate_next_due_date(
    recurring_task: RecurringTask, tz: pytz.BaseTzInfo, last_due_date: datetime = None
) -> datetime:
    """
    Calculate the next due date based on recurrence pattern

    Args:
        recurring_task: RecurringTask configuration
        tz: Timezone for calculation
        last_due_date: Last due date (or None for first calculation)

    Returns:
        Next due date in UTC
    """
    # Start from last due date or use next_due_date from recurring task
    if last_due_date:
        start_date = last_due_date
    elif recurring_task.next_due_date:
        start_date = recurring_task.next_due_date
    else:
        start_date = datetime.now(timezone.utc)

    # Ensure start_date is timezone-aware
    if start_date.tzinfo is None:
        start_date = tz.localize(start_date)

    pattern = PATTERN_MAP.get(recurring_task.recurrence_pattern, DAILY)
    interval = recurring_task.interval or 1

    # Build rrule parameters
    rrule_kwargs = {
        "freq": pattern,
        "interval": interval,
        "dtstart": start_date,
        "count": 2,  # Get next occurrence after start_date
    }

    # Add pattern-specific parameters
    if recurring_task.recurrence_pattern == "weekly" and recurring_task.by_weekday:
        # Parse weekday string (e.g., "MO,WE,FR")
        weekday_map = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
        weekdays = [weekday_map.get(d.strip().upper()) for d in recurring_task.by_weekday.split(",")]
        weekdays = [w for w in weekdays if w is not None]
        if weekdays:
            rrule_kwargs["byweekday"] = weekdays

    elif recurring_task.recurrence_pattern == "monthly" and recurring_task.by_monthday:
        rrule_kwargs["bymonthday"] = recurring_task.by_monthday

    elif recurring_task.recurrence_pattern == "yearly" and recurring_task.by_month:
        # Parse month string (e.g., "1,6,12")
        months = [int(m.strip()) for m in recurring_task.by_month.split(",")]
        rrule_kwargs["bymonth"] = months

    # Generate occurrences
    rule = rrule(**rrule_kwargs)
    occurrences = list(rule)

    # Return the second occurrence (first is the start_date)
    if len(occurrences) > 1:
        next_date = occurrences[1]
        # Convert to UTC
        if hasattr(next_date, "astimezone"):
            return next_date.astimezone(pytz.UTC)
        return tz.localize(next_date).astimezone(pytz.UTC)
    else:
        # Fallback: add interval based on pattern
        if pattern == MINUTELY:
            return start_date + timedelta(minutes=interval)
        elif pattern == DAILY:
            return start_date + timedelta(days=interval)
        elif pattern == WEEKLY:
            return start_date + timedelta(weeks=interval)
        elif pattern == MONTHLY:
            # Handle month overflow
            month = start_date.month + interval
            year = start_date.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            return start_date.replace(year=year, month=month)
        elif pattern == YEARLY:
            return start_date.replace(year=start_date.year + interval)
        return start_date


if __name__ == "__main__":
    # Test the task
    print("Testing recurring task worker...")
    result = generate_recurring_instances.delay()
    print(f"Task ID: {result.id}")
    print(f"Result: {result.get(timeout=30)}")
