"""
Dapr State Manager
Provides state management using Dapr sidecar
"""

import json
from contextlib import contextmanager
from typing import Any, Dict, Optional

from dapr.clients import DaprClient


class DaprStateManager:
    """Manages application state using Dapr state store"""

    def __init__(self, state_store_name: str = "todo-statestore"):
        self.state_store_name = state_store_name

    @contextmanager
    def _get_client(self):
        """Context manager for Dapr client"""
        client = DaprClient()
        try:
            yield client
        finally:
            client.close()

    async def save_state(self, key: str, value: Dict[str, Any]) -> bool:
        """
        Save state to Dapr state store

        Args:
            key: State key (e.g., 'user:{id}:settings')
            value: State value as dictionary

        Returns:
            True if successful
        """
        with self._get_client() as client:
            client.save_state(store_name=self.state_store_name, key=key, value=json.dumps(value))
            return True

    async def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve state from Dapr state store

        Args:
            key: State key

        Returns:
            State value as dictionary or None if not found
        """
        with self._get_client() as client:
            response = client.get_state(store_name=self.state_store_name, key=key)
            if response.data:
                return json.loads(response.data)
            return None

    async def delete_state(self, key: str) -> bool:
        """
        Delete state from Dapr state store

        Args:
            key: State key

        Returns:
            True if successful
        """
        with self._get_client() as client:
            client.delete_state(store_name=self.state_store_name, key=key)
            return True

    async def save_bulk_state(self, states: list) -> bool:
        """
        Save multiple states in a transaction

        Args:
            states: List of dicts with 'key' and 'value' fields

        Returns:
            True if successful
        """
        with self._get_client() as client:
            client.save_bulk_state(store_name=self.state_store_name, states=states)
            return True


# Global instance
_state_manager: Optional[DaprStateManager] = None


def get_state_manager() -> DaprStateManager:
    """Get or create the global state manager instance"""
    global _state_manager
    if _state_manager is None:
        _state_manager = DaprStateManager()
    return _state_manager
