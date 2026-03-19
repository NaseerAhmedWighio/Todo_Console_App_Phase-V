"""
Kafka Event Publisher
Publishes domain events to Kafka topics via Dapr Pub/Sub
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes events to Kafka topics via Dapr Pub/Sub"""

    def __init__(self, bootstrap_servers: list = None, dapr_http_port: int = 3500, pubsub_name: str = "kafka-pubsub"):
        self.bootstrap_servers = bootstrap_servers or ["localhost:9092"]
        self.dapr_http_port = dapr_http_port
        self.pubsub_name = pubsub_name
        self.base_url = f"http://localhost:{dapr_http_port}"
        self.producer = None
        self._initialized = False
        self._use_dapr = True  # Prefer Dapr Pub/Sub

    def _ensure_initialized(self):
        """Lazy initialization of Kafka producer"""
        if not self._initialized:
            try:
                self.producer = KafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                    key_serializer=lambda k: k.encode("utf-8") if k else None,
                    acks="all",  # Wait for all replicas to acknowledge
                    retries=3,
                    retry_backoff_ms=100,
                    max_in_flight_requests_per_connection=1,  # Ensure idempotence
                )
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize Kafka producer: {e}")
                raise

    async def publish(
        self, topic: str, event_type: str, payload: Dict[str, Any], user_id: str, aggregate_id: str = None
    ) -> bool:
        """
        Publish an event to Kafka topic via Dapr Pub/Sub

        Args:
            topic: Kafka topic name (e.g., 'task-events')
            event_type: Type of event (e.g., 'task.created')
            payload: Event payload data
            user_id: ID of the user who triggered the event
            aggregate_id: ID of the aggregate (e.g., task_id)

        Returns:
            True if successful
        """
        message = {
            "event_type": event_type,
            "payload": payload,
            "user_id": user_id,
            "aggregate_id": aggregate_id,
            "timestamp": datetime.utcnow().isoformat(),
            "schema_version": "1.0",
        }

        # Try Dapr Pub/Sub first
        if self._use_dapr:
            try:
                async with httpx.AsyncClient() as client:
                    url = f"{self.base_url}/v1.0/publish/{self.pubsub_name}/{topic}"
                    response = await client.post(url, json=message, timeout=10.0)
                    if response.status_code == 200 or response.status_code == 204:
                        logger.debug(f"Event published to {topic} via Dapr")
                        return True
                    logger.warning(
                        f"Dapr publish failed with status {response.status_code}, falling back to direct Kafka"
                    )
            except Exception as e:
                logger.warning(f"Dapr publish failed: {e}, falling back to direct Kafka")

        # Fallback to direct Kafka
        self._ensure_initialized()

        try:
            # Use asyncio.to_thread() for non-blocking send
            future = await asyncio.to_thread(self.producer.send, topic, key=user_id, value=message)

            # Wait for send to complete (with timeout)
            record_metadata = future.get(timeout=10)

            logger.debug(
                f"Event published to {record_metadata.topic} "
                f"partition {record_metadata.partition} "
                f"offset {record_metadata.offset}"
            )

            return True

        except KafkaError as e:
            logger.error(f"Failed to publish event to Kafka: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error publishing event: {e}")
            return False

    async def publish_batch(self, topic: str, events: list) -> bool:
        """
        Publish multiple events to the same topic

        Args:
            topic: Kafka topic name
            events: List of event dicts with event_type, payload, user_id, aggregate_id

        Returns:
            True if all events were published successfully
        """
        self._ensure_initialized()

        try:
            for event_data in events:
                message = {
                    "event_type": event_data["event_type"],
                    "payload": event_data["payload"],
                    "user_id": event_data["user_id"],
                    "aggregate_id": event_data.get("aggregate_id"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "schema_version": "1.0",
                }

                await asyncio.to_thread(self.producer.send, topic, key=event_data["user_id"], value=message)

            # Flush all pending messages
            await asyncio.to_thread(self.producer.flush)

            return True

        except Exception as e:
            logger.error(f"Failed to publish batch events: {e}")
            return False

    def close(self):
        """Close the Kafka producer"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            self._initialized = False


# Global instance
_publisher: Optional[EventPublisher] = None


def get_event_publisher() -> EventPublisher:
    """Get or create the global event publisher instance"""
    global _publisher
    if _publisher is None:
        _publisher = EventPublisher()
    return _publisher
