"""
Event Worker
Celery tasks for event processing and cleanup
"""

from celery import shared_task
from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select
import logging

from ..database.session import engine
from ..models.event import DomainEvent

logger = logging.getLogger(__name__)


@shared_task
def cleanup_old_events(days_to_keep: int = 30):
    """
    Celery task to clean up old processed events
    Runs daily at 3 AM via Celery Beat

    Args:
        days_to_keep: Number of days to keep events (default: 30)
    """
    logger.info(f"Starting cleanup of events older than {days_to_keep} days...")

    try:
        with Session(engine) as session:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_to_keep)

            # Delete old processed events
            statement = (
                select(DomainEvent)
                .where(DomainEvent.processed == True)
                .where(DomainEvent.created_at < cutoff_date)
            )
            old_events = session.exec(statement).all()

            deleted_count = 0
            for event in old_events:
                session.delete(event)
                deleted_count += 1

            session.commit()

        logger.info(f"Deleted {deleted_count} old events")
        return {"deleted": deleted_count}

    except Exception as e:
        logger.error(f"Event cleanup failed: {e}")
        raise


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def retry_failed_events(self):
    """
    Retry publishing failed events
    Runs every 5 minutes
    """
    logger.info("Starting retry of failed events...")

    try:
        with Session(engine) as session:
            # Get events that failed to publish
            statement = (
                select(DomainEvent)
                .where(DomainEvent.published == False)
                .where(DomainEvent.error_message != None)  # noqa: E711
                .order_by(DomainEvent.created_at)
                .limit(50)
            )
            failed_events = session.exec(statement).all()

            retried_count = 0
            for event in failed_events:
                try:
                    # Clear error message and mark for retry
                    event.error_message = None
                    session.add(event)
                    retried_count += 1
                except Exception as e:
                    logger.error(f"Error preparing event {event.id} for retry: {e}")

            session.commit()

        logger.info(f"Prepared {retried_count} events for retry")
        return {"retried": retried_count}

    except Exception as exc:
        logger.error(f"Event retry failed: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@shared_task
def publish_pending_events():
    """
    Publish any events that were created but not published
    Runs every minute as a backup to real-time publishing
    """
    from ..services.event_service import get_event_service
    from ..events.schemas import KafkaTopics

    logger.info("Starting publication of pending events...")

    try:
        event_service = get_event_service()

        # Get unpublished events
        unpublished = event_service.get_unpublished_events(limit=100)

        published_count = 0
        for event in unpublished:
            try:
                import asyncio
                asyncio.run(event_service.publish_event(event))
                published_count += 1
            except Exception as e:
                logger.error(f"Failed to publish event {event.id}: {e}")

        logger.info(f"Published {published_count} pending events")
        return {"published": published_count}

    except Exception as e:
        logger.error(f"Pending event publication failed: {e}")


if __name__ == '__main__':
    # Test the tasks
    print("Testing event worker...")

    print("\nTesting cleanup_old_events...")
    result = cleanup_old_events.delay(days_to_keep=7)
    print(f"Cleanup Task ID: {result.id}")
    print(f"Cleanup Result: {result.get(timeout=30)}")

    print("\nTesting retry_failed_events...")
    result = retry_failed_events.delay()
    print(f"Retry Task ID: {result.id}")
    print(f"Retry Result: {result.get(timeout=30)}")
