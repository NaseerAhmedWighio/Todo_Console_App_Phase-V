"""
Kafka Event Consumer
Consumes and processes events from Kafka topics
"""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, List, Optional

from kafka import KafkaConsumer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class EventConsumer:
    """Consumes and processes events from Kafka topics"""

    def __init__(self, bootstrap_servers: list = None, consumer_group: str = "todo-app"):
        self.bootstrap_servers = bootstrap_servers or ["localhost:9092"]
        self.consumer_group = consumer_group
        self.consumer: Optional[KafkaConsumer] = None
        self._handlers: Dict[str, List[Callable]] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def subscribe(self, topics: list):
        """
        Subscribe to Kafka topics

        Args:
            topics: List of topic names to subscribe to
        """
        self.consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.consumer_group,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            key_deserializer=lambda k: k.decode("utf-8") if k else None,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            consumer_timeout_ms=1000,  # Return from iterator if no message for 1s
        )
        logger.info(f"Subscribed to topics: {topics}")

    def register_handler(self, event_type: str, handler: Callable):
        """
        Register a handler for a specific event type

        Args:
            event_type: Type of event to handle (e.g., 'task.created')
            handler: Async function to handle the event
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.debug(f"Registered handler for event type: {event_type}")

    async def process_event(self, message: Dict[str, Any]):
        """
        Process a single event by dispatching to registered handlers

        Args:
            message: Event message from Kafka
        """
        event_type = message.get("event_type")

        if not event_type:
            logger.warning("Received message without event_type")
            return

        handlers = self._handlers.get(event_type, [])

        if not handlers:
            logger.debug(f"No handlers registered for event type: {event_type}")
            return

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                logger.error(f"Error processing event {event_type}: {e}")
                # Event will be retried on next poll due to auto-commit behavior

    async def start_consuming(self):
        """Start consuming events from Kafka"""
        if not self.consumer:
            raise RuntimeError("Must call subscribe() before start_consuming()")

        self._running = True
        logger.info("Starting event consumption")

        while self._running:
            try:
                # Poll for messages
                messages = self.consumer.poll(timeout_ms=1000)

                for topic_partition, records in messages.items():
                    for record in records:
                        await self.process_event(record.value)

            except KafkaError as e:
                logger.error(f"Kafka error while consuming: {e}")
                await asyncio.sleep(5)  # Back off before retrying
            except Exception as e:
                logger.error(f"Unexpected error consuming events: {e}")
                await asyncio.sleep(1)

    def stop_consuming(self):
        """Stop consuming events"""
        self._running = False
        logger.info("Stopping event consumption")

    def close(self):
        """Close the Kafka consumer"""
        self.stop_consuming()
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")


# Global instance
_consumer: Optional[EventConsumer] = None


def get_event_consumer(consumer_group: str = "todo-app") -> EventConsumer:
    """Get or create the global event consumer instance"""
    global _consumer
    if _consumer is None:
        _consumer = EventConsumer(consumer_group=consumer_group)
    return _consumer
