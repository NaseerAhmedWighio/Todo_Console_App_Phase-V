"""
Dapr Notification Routes
API routes for Dapr event handlers and notification management
"""

import logging
from typing import Dict

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dapr", tags=["dapr-events"])


@router.post("/notifications/scheduled")
async def handle_scheduled_notification(request: dict) -> Dict[str, bool]:
    """
    Dapr callback endpoint for scheduled notifications
    Triggered by Dapr Cron binding every minute
    """
    logger.info(f"Received scheduled notification request from Dapr: {request}")

    try:
        from app.dapr.notification_handler import handle_scheduled_notification_event

        result = handle_scheduled_notification_event(request)

        if result.get("success"):
            return {"success": True}
        else:
            logger.error(f"Notification handler failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

    except Exception as e:
        logger.error(f"Failed to handle scheduled notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notifications/recurring")
async def handle_recurring_notification(request: dict) -> Dict[str, bool]:
    """
    Dapr callback endpoint for recurring task notifications
    Triggered by Dapr Cron binding for recurring patterns
    """
    logger.info(f"Received recurring notification request from Dapr: {request}")

    try:
        from app.dapr.notification_handler import handle_recurring_notification_event

        result = handle_recurring_notification_event(request)

        if result.get("success"):
            return {"success": True}
        else:
            logger.error(f"Recurring notification handler failed: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))

    except Exception as e:
        logger.error(f"Failed to handle recurring notification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def dapr_health_check() -> Dict[str, str]:
    """Health check endpoint for Dapr"""
    return {"status": "healthy"}
