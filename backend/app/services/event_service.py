"""
Event Service
High-level service for publishing domain events
"""

from ..events.publisher import get_event_publisher
from ..events.schemas import EventTypes, KafkaTopics
from typing import Dict, Any, Optional
import uuid
import logging

logger = logging.getLogger(__name__)


class EventService:
    """Service for publishing domain events to Kafka"""

    def __init__(self):
        self.publisher = get_event_publisher()

    async def publish_task_event(
        self,
        event_type: str,
        task_id: uuid.UUID,
        task_data: Dict[str, Any],
        user_id: uuid.UUID,
        changes: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Publish a task-related event

        Args:
            event_type: Type of task event (created, updated, completed, deleted)
            task_id: ID of the task
            task_data: Full task data
            user_id: ID of the user
            changes: For updates, the fields that changed

        Returns:
            True if published successfully
        """
        payload = {
            'task_id': str(task_id),
            'task_data': task_data,
        }

        if changes:
            payload['changes'] = changes

        return await self.publisher.publish(
            topic=KafkaTopics.TASKS_CREATED,  # Main topic for all task events
            event_type=event_type,
            payload=payload,
            user_id=str(user_id),
            aggregate_id=str(task_id)
        )

    async def publish_task_created(
        self,
        task_id: uuid.UUID,
        task_data: Dict[str, Any],
        user_id: uuid.UUID
    ) -> bool:
        """Publish task.created event"""
        return await self.publish_task_event(
            event_type=EventTypes.TASK_CREATED,
            task_id=task_id,
            task_data=task_data,
            user_id=user_id
        )

    async def publish_task_updated(
        self,
        task_id: uuid.UUID,
        task_data: Dict[str, Any],
        user_id: uuid.UUID,
        changes: Dict[str, Any]
    ) -> bool:
        """Publish task.updated event"""
        return await self.publish_task_event(
            event_type=EventTypes.TASK_UPDATED,
            task_id=task_id,
            task_data=task_data,
            user_id=user_id,
            changes=changes
        )

    async def publish_task_completed(
        self,
        task_id: uuid.UUID,
        task_data: Dict[str, Any],
        user_id: uuid.UUID
    ) -> bool:
        """Publish task.completed event"""
        return await self.publish_task_event(
            event_type=EventTypes.TASK_COMPLETED,
            task_id=task_id,
            task_data=task_data,
            user_id=user_id
        )

    async def publish_task_deleted(
        self,
        task_id: uuid.UUID,
        task_data: Dict[str, Any],
        user_id: uuid.UUID
    ) -> bool:
        """Publish task.deleted event"""
        return await self.publish_task_event(
            event_type=EventTypes.TASK_DELETED,
            task_id=task_id,
            task_data=task_data,
            user_id=user_id
        )

    async def publish_reminder_event(
        self,
        task_id: uuid.UUID,
        reminder_data: Dict[str, Any],
        user_id: uuid.UUID
    ) -> bool:
        """
        Publish a reminder-related event

        Args:
            task_id: ID of the task
            reminder_data: Reminder configuration
            user_id: ID of the user

        Returns:
            True if published successfully
        """
        payload = {
            'task_id': str(task_id),
            'reminder_data': reminder_data,
        }

        return await self.publisher.publish(
            topic=KafkaTopics.REMINDERS,
            event_type='reminder.created',
            payload=payload,
            user_id=str(user_id),
            aggregate_id=str(task_id)
        )

    async def publish_recurring_event(
        self,
        event_type: str,
        recurring_task_id: uuid.UUID,
        data: Dict[str, Any],
        user_id: uuid.UUID
    ) -> bool:
        """
        Publish a recurring task event

        Args:
            event_type: Type of recurring event
            recurring_task_id: ID of the recurring task
            data: Event data
            user_id: ID of the user

        Returns:
            True if published successfully
        """
        payload = {
            'recurring_task_id': str(recurring_task_id),
            'data': data,
        }

        return await self.publisher.publish(
            topic=KafkaTopics.RECURRING,
            event_type=event_type,
            payload=payload,
            user_id=str(user_id),
            aggregate_id=str(recurring_task_id)
        )

    async def publish_and_track(
        self,
        event_type: str,
        aggregate_id: uuid.UUID | str,
        aggregate_type: str,
        user_id: uuid.UUID | str,
        payload: Dict[str, Any],
        topic: str = KafkaTopics.ALL_EVENTS
    ) -> bool:
        """
        Publish an event with tracking information

        Args:
            event_type: Type of event
            aggregate_id: ID of the aggregate
            aggregate_type: Type of aggregate (Task, Reminder, etc.)
            user_id: ID of the user
            payload: Event payload
            topic: Kafka topic to publish to

        Returns:
            True if published successfully
        """
        return await self.publisher.publish(
            topic=topic,
            event_type=event_type,
            payload={
                'aggregate_type': aggregate_type,
                'aggregate_id': str(aggregate_id),
                **payload
            },
            user_id=str(user_id),
            aggregate_id=str(aggregate_id)
        )


# Global instance
_event_service: Optional[EventService] = None


def get_event_service() -> EventService:
    """Get or create the global event service instance"""
    global _event_service
    if _event_service is None:
        _event_service = EventService()
    return _event_service
