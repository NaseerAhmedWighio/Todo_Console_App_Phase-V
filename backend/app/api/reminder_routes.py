from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional
from ..database.session import get_session
from ..models.reminder import Reminder, ReminderCreate, ReminderUpdate, ReminderResponse
from ..models.todo import Todo
from ..models.user import User
from ..api.todo_routes import get_current_user
from ..workers.reminder_worker import TaskReminderWorker
from datetime import datetime, timedelta, timezone
import uuid

router = APIRouter(prefix="/api/v1/reminders", tags=["reminders"])


def calculate_scheduled_time(
    due_date: datetime,
    timing_minutes: int = 0,
    timing_days: Optional[int] = None
) -> datetime:
    """Calculate when reminder should be sent"""
    if timing_days is not None and timing_days > 0:
        return due_date - timedelta(days=timing_days)
    else:
        return due_date - timedelta(minutes=timing_minutes)


@router.post("/", response_model=ReminderResponse)
async def create_reminder(
    reminder_data: ReminderCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> ReminderResponse:
    """Create a reminder for a task"""
    # Verify task exists and belongs to user
    task = session.get(Todo, reminder_data.task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    if not task.due_date:
        raise HTTPException(status_code=400, detail="Task must have a due date to set a reminder")

    # Calculate scheduled time
    due_date = task.due_date
    if due_date.tzinfo is None:
        due_date = due_date.replace(tzinfo=timezone.utc)

    scheduled_time = calculate_scheduled_time(
        due_date,
        reminder_data.timing_minutes,
        reminder_data.timing_days
    )

    # Create reminder
    reminder = Reminder(
        task_id=reminder_data.task_id,
        timing_minutes=reminder_data.timing_minutes,
        timing_days=reminder_data.timing_days,
        delivery_channel=reminder_data.delivery_channel or 'in_app',
        scheduled_time=scheduled_time,
        status='pending'
    )

    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    # Publish Kafka event via Dapr Pub/Sub
    try:
        from app.services.event_service import get_event_service
        event_service = get_event_service()
        await event_service.publish_reminder_event(
            task_id=reminder.task_id,
            reminder_data={
                'id': str(reminder.id),
                'timing_minutes': reminder.timing_minutes,
                'timing_days': reminder.timing_days,
                'delivery_channel': reminder.delivery_channel,
                'scheduled_time': reminder.scheduled_time.isoformat(),
            },
            user_id=current_user.id
        )
    except Exception as e:
        print(f"Warning: Failed to publish reminder event: {e}")

    # Schedule reminder using Dapr Jobs API for exact-time trigger
    try:
        from app.dapr.jobs import get_jobs_client
        jobs_client = get_jobs_client()
        await jobs_client.schedule_job(
            job_name=f"reminder-{reminder.id}",
            due_time=reminder.scheduled_time,
            data={
                'reminder_id': str(reminder.id),
                'task_id': str(reminder.task_id),
                'user_id': str(current_user.id),
                'type': 'reminder'
            }
        )
    except Exception as e:
        print(f"Warning: Failed to schedule Dapr job: {e}")

    return ReminderResponse.model_validate(reminder)


@router.get("/", response_model=List[ReminderResponse])
def list_reminders(
    status: Optional[str] = Query(None, description="Filter by status (pending, sent, failed, cancelled)"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[ReminderResponse]:
    """List all reminders for current user"""
    # Get all tasks for user
    user_tasks_statement = select(Todo.id).where(Todo.user_id == current_user.id)
    user_task_ids = session.exec(user_tasks_statement).all()

    if not user_task_ids:
        return []

    # Get reminders for user's tasks
    statement = select(Reminder).where(Reminder.task_id.in_(user_task_ids))

    if status:
        statement = statement.where(Reminder.status == status)

    reminders = session.exec(statement.order_by(Reminder.scheduled_time)).all()

    # Build response with task titles
    result = []
    for reminder in reminders:
        task = session.get(Todo, reminder.task_id)
        reminder_dict = ReminderResponse.model_validate(reminder)
        if task:
            reminder_dict.task_title = task.title  # type: ignore
        result.append(reminder_dict)

    return result


@router.get("/{reminder_id}", response_model=ReminderResponse)
def get_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> ReminderResponse:
    """Get a specific reminder by ID"""
    try:
        reminder_uuid = uuid.UUID(reminder_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid reminder ID format")

    reminder = session.get(Reminder, reminder_uuid)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    # Verify ownership through task
    task = session.get(Todo, reminder.task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Reminder not found")

    reminder_dict = ReminderResponse.model_validate(reminder)
    reminder_dict.task_title = task.title  # type: ignore
    return reminder_dict


@router.delete("/{reminder_id}")
def delete_reminder(
    reminder_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Delete/cancel a reminder"""
    try:
        reminder_uuid = uuid.UUID(reminder_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid reminder ID format")

    reminder = session.get(Reminder, reminder_uuid)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    # Verify ownership through task
    task = session.get(Todo, reminder.task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Reminder not found")

    session.delete(reminder)
    session.commit()

    return {"message": "Reminder deleted successfully"}


@router.post("/send-reminders")
def send_reminders_now(
    hours_ahead: int = Query(default=24, description="Send reminders for tasks due within this many hours"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Manually trigger sending of task reminder emails
    Only sends reminders for verified users
    """
    try:
        worker = TaskReminderWorker(session)
        stats = worker.send_all_reminders(hours_ahead=hours_ahead)
        
        return {
            "success": True,
            "message": f"Sent {stats['sent']} reminder(s)",
            "data": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send reminders: {str(e)}"
        )


@router.put("/{reminder_id}", response_model=ReminderResponse)
def update_reminder(
    reminder_id: str,
    reminder_update: ReminderUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> ReminderResponse:
    """Update a reminder"""
    try:
        reminder_uuid = uuid.UUID(reminder_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid reminder ID format")

    reminder = session.get(Reminder, reminder_uuid)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    # Verify ownership through task
    task = session.get(Todo, reminder.task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Reminder not found")

    # Update fields
    update_data = reminder_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(reminder, field, value)

    # Recalculate scheduled time if timing changed
    if reminder_update.timing_minutes is not None or reminder_update.timing_days is not None:
        due_date = task.due_date
        if due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)

        reminder.scheduled_time = calculate_scheduled_time(
            due_date,
            reminder_update.timing_minutes or reminder.timing_minutes,
            reminder_update.timing_days or reminder.timing_days
        )

    session.add(reminder)
    session.commit()
    session.refresh(reminder)

    return ReminderResponse.model_validate(reminder)
