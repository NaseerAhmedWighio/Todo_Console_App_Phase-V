"""
Scheduled Notification Routes
API routes for managing scheduled task notifications
Allows users to set specific times to receive email notifications for tasks
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..api.todo_routes import get_current_user
from ..database.session import get_session
from ..models.todo import Todo, TodoResponse
from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["scheduled-notifications"])


@router.post("/tasks/{task_id}/schedule")
async def schedule_task_notification(
    task_id: str,
    scheduled_time: datetime,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TodoResponse:
    """
    Schedule a notification for a specific task at a specific time

    Args:
        task_id: UUID of the task
        scheduled_time: When to send the notification (ISO 8601 format)

    Returns:
        Updated task with scheduled notification time
    """
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    # Get the task
    task = session.get(Todo, task_uuid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify ownership
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this task")

    # Ensure scheduled_time has timezone info
    if scheduled_time.tzinfo is None:
        scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)

    # Update scheduled time and reset notification_sent flag
    task.scheduled_time = scheduled_time
    task.notification_sent = False
    task.notified_at = None
    session.add(task)
    session.commit()
    session.refresh(task)

    logger.info(f"Scheduled notification for task {task_id} at {scheduled_time}")

    return TodoResponse.model_validate(task)


@router.post("/tasks/{task_id}/cancel")
async def cancel_task_notification(
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """
    Cancel a scheduled notification for a task

    Args:
        task_id: UUID of the task

    Returns:
        Success message
    """
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    # Get the task
    task = session.get(Todo, task_uuid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Verify ownership
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this task")

    # Clear scheduled time
    task.scheduled_time = None
    task.notification_sent = False
    task.notified_at = None
    session.add(task)
    session.commit()

    logger.info(f"Cancelled scheduled notification for task {task_id}")

    return {"message": "Notification cancelled successfully"}


@router.get("/scheduled")
async def get_scheduled_notifications(
    status: Optional[str] = Query(
        None, description="Filter by notification status (pending, sent)"
    ),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[TodoResponse]:
    """
    Get all tasks with scheduled notifications for the current user

    Args:
        status: Filter by notification_sent status (pending=False, sent=True)

    Returns:
        List of tasks with scheduled notifications
    """
    statement = select(Todo).where(Todo.user_id == current_user.id)

    # Filter by scheduled_time existence
    statement = statement.where(Todo.scheduled_time != None)  # noqa: E711

    # Filter by status if provided
    if status == "pending":
        statement = statement.where(Todo.notification_sent == False)
    elif status == "sent":
        statement = statement.where(Todo.notification_sent == True)

    # Order by scheduled time
    statement = statement.order_by(Todo.scheduled_time)

    tasks = session.exec(statement).all()
    return [TodoResponse.model_validate(task) for task in tasks]


@router.post("/send-test-email")
async def send_test_notification_email(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """
    Send a test notification email to verify email configuration

    Returns:
        Success message
    """
    try:
        from ..services.email_service import email_service

        # Send test email
        user_name = current_user.name or "User"
        email_sent = email_service.send_email(
            to_email=current_user.email,
            subject="Test Notification - Todo App Phase V",
            html_content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .container {{
                        background-color: #f9fafb;
                        border-radius: 8px;
                        padding: 30px;
                        margin: 20px 0;
                    }}
                    .success {{
                        color: #10b981;
                        font-weight: 600;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2 class="success">✓ Test Email Successful!</h2>
                    <p>Hello {user_name},</p>
                    <p>This is a test notification email from your Todo App.</p>
                    <p>Your email configuration is working correctly. You will now receive task reminders and notifications at your scheduled times.</p>
                    <p>If you have any questions, please contact support.</p>
                </div>
            </body>
            </html>
            """,
            text_content=f"""
            Test Email Successful!

            Hello {user_name},

            This is a test notification email from your Todo App.

            Your email configuration is working correctly. You will now receive task reminders and notifications at your scheduled times.
            """,
        )

        if email_sent:
            logger.info(f"Test email sent successfully to {current_user.email}")
            return {"success": True, "message": "Test email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send test email")

    except Exception as e:
        logger.error(f"Failed to send test email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send test email: {str(e)}")
