import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.connection_status: Dict[str, bool] = {}  # Track connection status per user
        self.heartbeat_tasks: Dict[str, asyncio.Task] = {}  # Track heartbeat tasks
        self.HEARTBEAT_INTERVAL = 30  # Send ping every 30 seconds
        self.HEARTBEAT_TIMEOUT = 60  # Disconnect if no pong within 60 seconds

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new WebSocket connection with heartbeat"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
            self.connection_status[user_id] = True
        self.active_connections[user_id].append(websocket)

        # Start heartbeat for this connection
        self._start_heartbeat(websocket, user_id)

        logger.info(f"[WebSocket] User {user_id} connected. Total connections: {len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection and cleanup heartbeat"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                logger.info(
                    f"[WebSocket] User {user_id} disconnected. Remaining connections: {len(self.active_connections[user_id])}"
                )

            # Cancel heartbeat task
            self._stop_heartbeat(user_id)

            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                self.connection_status.pop(user_id, None)
                logger.info(f"[WebSocket] User {user_id} has no more connections")

    def _start_heartbeat(self, websocket: WebSocket, user_id: str):
        """Start heartbeat task for a connection"""

        async def heartbeat_loop():
            try:
                while True:
                    await asyncio.sleep(self.HEARTBEAT_INTERVAL)
                    try:
                        # Send ping
                        await websocket.send_json({"type": "ping", "timestamp": datetime.utcnow().isoformat()})
                        # Wait for pong with timeout
                        async with asyncio.timeout(self.HEARTBEAT_TIMEOUT):
                            # Note: Actual pong handling is in receive loop
                            pass
                    except asyncio.TimeoutError:
                        logger.warning(f"[WebSocket] User {user_id} heartbeat timeout, disconnecting")
                        self.disconnect(websocket, user_id)
                        break
                    except Exception as e:
                        logger.error(f"[WebSocket] Heartbeat error for user {user_id}: {e}")
                        self.disconnect(websocket, user_id)
                        break
            except asyncio.CancelledError:
                pass  # Task cancelled, cleanup handled elsewhere

        # Store task reference
        if user_id in self.heartbeat_tasks:
            self.heartbeat_tasks[user_id].cancel()
        self.heartbeat_tasks[user_id] = asyncio.create_task(heartbeat_loop())

    def _stop_heartbeat(self, user_id: str):
        """Stop heartbeat task for a user"""
        if user_id in self.heartbeat_tasks:
            self.heartbeat_tasks[user_id].cancel()
            del self.heartbeat_tasks[user_id]

    async def handle_pong(self, user_id: str):
        """Handle pong response from client"""
        logger.debug(f"[WebSocket] Received pong from user {user_id}")
        # Reset connection status
        self.connection_status[user_id] = True

    async def broadcast_to_user(self, message: dict, user_id: str):
        """Send a message to all connections of a specific user with error handling"""
        if user_id not in self.active_connections:
            logger.debug(f"[WebSocket] No connections for user {user_id}")
            return

        disconnected = []
        message_json = json.dumps(message)

        for connection in self.active_connections[user_id]:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"[WebSocket] Failed to send to user {user_id}: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            if user_id in self.active_connections:
                try:
                    self.active_connections[user_id].remove(connection)
                    if not self.active_connections[user_id]:
                        del self.active_connections[user_id]
                        self.connection_status.pop(user_id, None)
                        self._stop_heartbeat(user_id)
                except ValueError:
                    pass  # Connection already removed

    async def broadcast_task_update(self, event_type: str, task_data: dict, user_id: str):
        """Broadcast task update event to a specific user"""
        message = {
            "type": "task_update",
            "event": event_type,
            "data": task_data,
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast_to_user(message, str(user_id))

    async def broadcast_tag_update(self, event_type: str, tag_data: dict, user_id: str):
        """Broadcast tag update event to a specific user"""
        message = {
            "type": "tag_update",
            "event": event_type,
            "data": tag_data,
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast_to_user(message, str(user_id))

    async def broadcast_reminder_update(self, event_type: str, reminder_data: dict, user_id: str):
        """Broadcast reminder update event to a specific user"""
        message = {
            "type": "reminder_update",
            "event": event_type,
            "data": reminder_data,
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast_to_user(message, str(user_id))

    async def broadcast_search_update(self, search_results: dict, user_id: str):
        """Broadcast search results to a specific user"""
        message = {
            "type": "search_results",
            "data": search_results,
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast_to_user(message, str(user_id))

    async def broadcast_notification(self, notification_type: str, message_text: str, user_id: str, data: dict = None):
        """Broadcast a general notification to a specific user"""
        message = {
            "type": "notification",
            "notification_type": notification_type,
            "message": message_text,
            "data": data or {},
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast_to_user(message, str(user_id))

    async def broadcast_error(self, error_message: str, error_code: str, user_id: str):
        """Broadcast an error message to a specific user"""
        message = {
            "type": "error",
            "error_code": error_code,
            "message": error_message,
            "user_id": str(user_id),
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast_to_user(message, str(user_id))

    def get_connection_count(self, user_id: str) -> int:
        """Get the number of active connections for a user"""
        return len(self.active_connections.get(user_id, []))

    def get_total_connections(self) -> int:
        """Get total number of active connections across all users"""
        return sum(len(connections) for connections in self.active_connections.values())


manager = ConnectionManager()
