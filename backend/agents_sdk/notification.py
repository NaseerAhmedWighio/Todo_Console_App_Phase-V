"""Notification module for sending real-time updates to clients"""

import os
import sys

# Add the parent directory to the path to access the main backend modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import asyncio

from app.api.websocket_manager import manager as websocket_manager


async def notify_task_updated(user_id: str, task_data: dict, operation: str):
    """
    Send real-time update to the user about a task operation

    Args:
        user_id: ID of the user to notify
        task_data: Dictionary containing task information
        operation: Type of operation (create, update, complete, delete)
    """
    try:
        message = {
            "type": "task_update",
            "operation": operation,
            "task": task_data,
            "timestamp": asyncio.get_event_loop().time(),
        }

        await websocket_manager.broadcast_to_user(message, user_id)
    except Exception as e:
        print(f"Error sending websocket notification: {e}")


def notify_task_created_sync(user_id: str, task_data: dict):
    """Synchronous wrapper for task creation notification"""
    try:
        # Run the async function in a new event loop if no loop exists
        loop = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

        if loop and not loop.is_closed():
            # If there's a running loop, create a task
            asyncio.create_task(notify_task_updated(user_id, task_data, "create"))
        else:
            # Otherwise, run in a new loop
            asyncio.run(notify_task_updated(user_id, task_data, "create"))
    except Exception as e:
        print(f"Error sending task creation notification: {e}")


def notify_task_updated_sync(user_id: str, task_data: dict):
    """Synchronous wrapper for task update notification"""
    try:
        loop = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

        if loop and not loop.is_closed():
            asyncio.create_task(notify_task_updated(user_id, task_data, "update"))
        else:
            asyncio.run(notify_task_updated(user_id, task_data, "update"))
    except Exception as e:
        print(f"Error sending task update notification: {e}")


def notify_task_completed_sync(user_id: str, task_data: dict):
    """Synchronous wrapper for task completion notification"""
    try:
        loop = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

        if loop and not loop.is_closed():
            asyncio.create_task(notify_task_updated(user_id, task_data, "complete"))
        else:
            asyncio.run(notify_task_updated(user_id, task_data, "complete"))
    except Exception as e:
        print(f"Error sending task completion notification: {e}")


def notify_task_deleted_sync(user_id: str, task_data: dict):
    """Synchronous wrapper for task deletion notification"""
    try:
        loop = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

        if loop and not loop.is_closed():
            asyncio.create_task(notify_task_updated(user_id, task_data, "delete"))
        else:
            asyncio.run(notify_task_updated(user_id, task_data, "delete"))
    except Exception as e:
        print(f"Error sending task deletion notification: {e}")
