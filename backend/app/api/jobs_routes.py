"""
Dapr Jobs Callback Routes
Handles job trigger callbacks from Dapr Jobs API
"""

from fastapi import APIRouter, Request, Depends
from sqlmodel import Session
from ..database.session import get_session
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["dapr-jobs"])


@router.post("/trigger")
async def handle_job_trigger(request: Request, session: Session = Depends(get_session)):
    """
    Handle job trigger callback from Dapr Jobs API
    
    Dapr calls this endpoint when a scheduled job is due.
    """
    try:
        job_data = await request.json()
        
        logger.info(f"Received job trigger: {job_data}")
        
        # Extract job data
        data = job_data.get('data', {})
        job_type = data.get('type')
        
        if job_type == 'reminder':
            # Handle reminder notification
            reminder_id = data.get('reminder_id')
            task_id = data.get('task_id')
            user_id = data.get('user_id')
            
            logger.info(f"Processing reminder {reminder_id} for task {task_id}")
            
            # Send notification
            from ..services.email_service import email_service
            from ..models.reminder import Reminder
            from ..models.todo import Todo
            from ..models.user import User
            
            reminder = session.get(Reminder, reminder_id)
            if reminder:
                task = session.get(Todo, reminder.task_id)
                if task:
                    user = session.get(User, reminder.user_id or task.user_id)
                    if user and user.is_email_verified:
                        # Send email reminder
                        due_date_str = task.due_date.strftime("%B %d, %Y at %I:%M %p UTC") if task.due_date else "No due date"
                        
                        email_sent = email_service.send_task_reminder_email(
                            to_email=user.email,
                            user_name=user.name or user.email.split('@')[0],
                            task_title=task.title,
                            task_description=task.description,
                            due_date=due_date_str,
                            priority=task.priority or "medium"
                        )
                        
                        if email_sent:
                            reminder.status = "sent"
                            reminder.sent_at = data.get('sent_at')
                            reminder.message = f"Reminder sent via Dapr Jobs API"
                            session.add(reminder)
                            session.commit()
                            
                            logger.info(f"Sent reminder email for task {task_id} to user {user_id}")
                        else:
                            reminder.status = "failed"
                            reminder.error_message = "Email service returned False"
                            session.add(reminder)
                            session.commit()
                    else:
                        logger.warning(f"User not found or not verified for reminder {reminder_id}")
                else:
                    logger.warning(f"Task not found for reminder {reminder_id}")
            else:
                logger.warning(f"Reminder not found: {reminder_id}")
            
            return {
                "status": "SUCCESS",
                "message": "Reminder processed",
                "reminder_id": reminder_id
            }
        
        elif job_type == 'recurring_check':
            # Handle recurring task generation
            logger.info("Processing recurring task generation")
            
            from ..workers.recurring_worker import generate_recurring_instances
            
            # Trigger recurring task generation
            result = generate_recurring_instances.delay()
            
            return {
                "status": "SUCCESS",
                "message": "Recurring task generation triggered",
                "task_id": result.id
            }
        
        else:
            logger.warning(f"Unknown job type: {job_type}")
            return {
                "status": "SUCCESS",
                "message": f"Unknown job type: {job_type}"
            }
            
    except Exception as e:
        logger.error(f"Error processing job trigger: {e}")
        # Return SUCCESS anyway to prevent Dapr from retrying
        return {
            "status": "SUCCESS",
            "message": f"Error processed: {str(e)}"
        }
