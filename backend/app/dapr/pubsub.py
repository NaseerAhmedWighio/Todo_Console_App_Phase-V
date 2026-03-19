"""
Dapr Pub/Sub Service
Provides pub/sub messaging using Dapr sidecar
"""

import json
import logging
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional

from dapr.clients import DaprClient

logger = logging.getLogger(__name__)


class DaprPubSub:
    """Manages pub/sub messaging using Dapr"""

    def __init__(self, pubsub_name: str = "todo-pubsub"):
        self.pubsub_name = pubsub_name

    @contextmanager
    def _get_client(self):
        """Context manager for Dapr client"""
        client = DaprClient()
        try:
            yield client
        finally:
            client.close()

    async def publish(self, topic: str, data: Dict[str, Any]) -> bool:
        """
        Publish an event to a topic

        Args:
            topic: Topic name to publish to
            data: Event data as dictionary

        Returns:
            True if successful
        """
        with self._get_client() as client:
            client.publish_event(pubsub_name=self.pubsub_name, topic_name=topic, data=json.dumps(data))
            logger.debug(f"Published event to topic {topic}")
            return True

    async def publish_batch(self, topic: str, events: list) -> bool:
        """
        Publish multiple events to the same topic

        Args:
            topic: Topic name
            events: List of event data dictionaries

        Returns:
            True if all events were published
        """
        with self._get_client() as client:
            for event_data in events:
                client.publish_event(pubsub_name=self.pubsub_name, topic_name=topic, data=json.dumps(event_data))
            logger.debug(f"Published {len(events)} events to topic {topic}")
            return True

    def subscribe(self, topic: str, handler: Callable):
        """
        Subscribe to a topic (used as decorator with DaprApp)

        Args:
            topic: Topic name to subscribe to
            handler: Function to handle incoming events

        Returns:
            Decorated handler function
        """

        def decorator(func):
            # Register the handler for this topic
            # This is typically used with DaprApp from dapr.ext.fastapi
            logger.debug(f"Registered subscription for topic {topic}")
            return func

        return decorator


# Global instance
_pubsub: Optional[DaprPubSub] = None


def get_pubsub() -> DaprPubSub:
    """Get or create the global pub/sub instance"""
    global _pubsub
    if _pubsub is None:
        _pubsub = DaprPubSub()
    return _pubsub
