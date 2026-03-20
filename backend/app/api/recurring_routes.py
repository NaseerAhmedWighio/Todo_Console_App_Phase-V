import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from ..api.todo_routes import get_current_user
from ..database.session import get_session
from ..models.recurring_task import RecurringTask, RecurringTaskCreate, RecurringTaskResponse, RecurringTaskUpdate
from ..models.todo import Todo
from ..models.user import User
from ..services.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/recurring", tags=["recurring-tasks"])


@router.post("/tasks/{task_id}", response_model=RecurringTaskResponse)
def create_recurring_task(
    task_id: str,
    recurring_data: RecurringTaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> RecurringTaskResponse:
    """Configure a task as recurring"""
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    # Verify task exists and belongs to user
    task = session.get(Todo, task_uuid)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Create recurring task configuration
    recurring_task = RecurringTask(
        task_id=task_uuid,
        recurrence_pattern=recurring_data.recurrence_pattern,
        interval=recurring_data.interval or 1,
        by_weekday=recurring_data.by_weekday,
        by_monthday=recurring_data.by_monthday,
        by_month=recurring_data.by_month,
        end_condition=recurring_data.end_condition or "never",
        end_occurrences=recurring_data.end_occurrences,
        end_date=recurring_data.end_date,
        is_active=True,
    )

    # Mark the base task as recurring
    task.is_recurring = True
    session.add(recurring_task)
    session.add(task)
    session.commit()
    session.refresh(recurring_task)

    return RecurringTaskResponse.model_validate(recurring_task)


@router.get("/tasks/{task_id}", response_model=RecurringTaskResponse)
def get_recurring_task(
    task_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> RecurringTaskResponse:
    """Get recurring configuration for a task"""
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    # Find recurring task configuration
    statement = select(RecurringTask).where(RecurringTask.task_id == task_uuid)
    recurring_task = session.exec(statement).first()

    if not recurring_task:
        raise HTTPException(status_code=404, detail="Recurring configuration not found")

    # Verify ownership through the associated task
    task = session.get(Todo, task_uuid)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    return RecurringTaskResponse.model_validate(recurring_task)


@router.put("/tasks/{task_id}", response_model=RecurringTaskResponse)
def update_recurring_task(
    task_id: str,
    recurring_update: RecurringTaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> RecurringTaskResponse:
    """Update recurring configuration for a task"""
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    # Find recurring task configuration
    statement = select(RecurringTask).where(RecurringTask.task_id == task_uuid)
    recurring_task = session.exec(statement).first()

    if not recurring_task:
        raise HTTPException(status_code=404, detail="Recurring configuration not found")

    # Verify ownership
    task = session.get(Todo, task_uuid)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    update_data = recurring_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(recurring_task, field, value)

    session.add(recurring_task)
    session.commit()
    session.refresh(recurring_task)

    return RecurringTaskResponse.model_validate(recurring_task)


@router.delete("/tasks/{task_id}")
def delete_recurring_task(
    task_id: str,
    delete_all_instances: bool = False,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Remove recurring configuration from a task"""
    try:
        task_uuid = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")

    # Find recurring task configuration
    statement = select(RecurringTask).where(RecurringTask.task_id == task_uuid)
    recurring_task = session.exec(statement).first()

    if not recurring_task:
        raise HTTPException(status_code=404, detail="Recurring configuration not found")

    # Verify ownership
    task = session.get(Todo, task_uuid)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    # Delete all instances if requested
    if delete_all_instances:
        # Find all tasks that are instances of this recurring task
        instances_statement = select(Todo).where(Todo.recurring_task_id == recurring_task.id)
        instances = session.exec(instances_statement).all()
        for instance in instances:
            session.delete(instance)

    # Mark base task as non-recurring
    task.is_recurring = False
    task.recurring_task_id = None

    # Delete recurring configuration
    session.delete(recurring_task)
    session.add(task)
    session.commit()

    return {"message": "Recurring configuration deleted successfully"}


@router.get("/", response_model=List[RecurringTaskResponse])
def list_recurring_tasks(
    active_only: bool = True, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> List[RecurringTaskResponse]:
    """List all recurring tasks for the current user"""
    statement = (
        select(RecurringTask).join(Todo, RecurringTask.task_id == Todo.id).where(Todo.user_id == current_user.id)
    )

    if active_only:
        statement = statement.where(RecurringTask.is_active == True)

    recurring_tasks = session.exec(statement).all()
    return [RecurringTaskResponse.model_validate(rt) for rt in recurring_tasks]


@router.post("/create-with-notifications")
def create_recurring_task_with_notifications(
    task_title: str,
    task_description: Optional[str] = None,
    recurrence_pattern: str = Query(..., description="Pattern: daily, weekly, monthly, yearly, biweekly, quarterly, pay_bills"),
    interval: int = Query(1, ge=1, description="Interval between occurrences"),
    by_weekday: Optional[str] = Query(None, description="Comma-separated weekdays (0-6, 0=Monday)"),
    by_monthday: Optional[int] = Query(None, ge=1, le=31, description="Day of month (1-31)"),
    by_month: Optional[str] = Query(None, description="Comma-separated months (1-12)"),
    notification_time: Optional[datetime] = Query(None, description="Time to send notification (ISO 8601)"),
    end_condition: str = Query("never", description="End condition: never, after_occurrences, on_date"),
    end_occurrences: Optional[int] = Query(None, ge=1, description="Number of occurrences before ending"),
    end_date: Optional[datetime] = Query(None, description="End date for recurring task"),
    priority: str = Query("medium", description="Task priority: low, medium, high, urgent"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """
    Create a new recurring task with email notifications
    
    This endpoint:
    1. Creates the base task
    2. Configures recurring pattern
    3. Sets up email notifications at specified times
    4. Sends confirmation email to user
    
    Example patterns:
    - Pay bills monthly: pattern=pay_bills, by_monthday=1
    - Weekly review: pattern=weekly, by_weekday=0 (Monday)
    - Daily standup: pattern=daily, interval=1
    - Biweekly team meeting: pattern=biweekly, interval=1
    """
    try:
        # Validate pattern
        valid_patterns = ["daily", "weekly", "monthly", "yearly", "biweekly", "quarterly", "pay_bills", "custom"]
        if recurrence_pattern not in valid_patterns:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid pattern. Must be one of: {', '.join(valid_patterns)}"
            )
        
        # Validate pattern-specific requirements
        if recurrence_pattern in ["monthly", "pay_bills", "quarterly"] and not by_monthday:
            by_monthday = 1  # Default to 1st of month
            logger.info(f"Defaulting to day 1 for {recurrence_pattern} pattern")
        
        if recurrence_pattern == "weekly" and not by_weekday:
            by_weekday = "0"  # Default to Monday
        
        # Create base task
        now = datetime.now(timezone.utc)
        base_task = Todo(
            user_id=current_user.id,
            title=task_title,
            description=task_description,
            priority=priority,
            is_recurring=True,
            is_completed=False,
            notification_sent=False,
            timezone=current_user.timezone or "UTC",
        )
        
        session.add(base_task)
        session.commit()
        session.refresh(base_task)
        
        # Create recurring task configuration
        recurring_task = RecurringTask(
            task_id=base_task.id,
            recurrence_pattern=recurrence_pattern,
            interval=interval,
            by_weekday=by_weekday,
            by_monthday=by_monthday,
            by_month=by_month,
            end_condition=end_condition,
            end_occurrences=end_occurrences,
            end_date=end_date,
            is_active=True,
            next_due_date=now,  # Start immediately
        )
        
        session.add(recurring_task)
        
        # Create first occurrence if notification_time is provided
        first_occurrence = None
        if notification_time:
            # Ensure timezone
            if notification_time.tzinfo is None:
                notification_time = notification_time.replace(tzinfo=timezone.utc)
            
            first_occurrence = Todo(
                user_id=current_user.id,
                title=f"{task_title} (Recurring)",
                description=task_description,
                due_date=notification_time,
                scheduled_time=notification_time - timedelta(hours=1),  # Notify 1 hour before
                priority=priority,
                is_recurring=True,
                recurring_task_id=recurring_task.id,
                series_id=recurring_task.id,
                notification_sent=False,
                timezone=current_user.timezone or "UTC",
            )
            session.add(first_occurrence)
        
        session.commit()
        
        # Send confirmation email
        pattern_display = recurrence_pattern.replace("_", " ").title()
        email_sent = email_service.send_email(
            to_email=current_user.email,
            subject=f"Recurring Task Created: {task_title}",
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
                    .detail {{
                        background-color: white;
                        border: 1px solid #e5e7eb;
                        border-radius: 6px;
                        padding: 15px;
                        margin: 15px 0;
                    }}
                    .badge {{
                        display: inline-block;
                        background-color: #3b82f6;
                        color: white;
                        padding: 4px 12px;
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: 600;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2 class="success">✓ Recurring Task Created!</h2>
                    <p>Hello {current_user.name or current_user.email.split("@")[0]},</p>
                    <p>Your recurring task has been set up successfully.</p>
                    
                    <div class="detail">
                        <strong>Task:</strong> {task_title}<br/>
                        <span class="badge">{pattern_display}</span><br/><br/>
                        <strong>Pattern:</strong> {pattern_display} (every {interval} {recurrence_pattern})<br/>
                        <strong>First Occurrence:</strong> {notification_time.strftime("%B %d, %Y at %I:%M %p %Z") if notification_time else "Started immediately"}<br/>
                        {f'<strong>End Condition:</strong> {end_condition}' + (f' (after {end_occurrences} occurrences)' if end_occurrences else '') if end_condition != 'never' else ''}
                    </div>
                    
                    <p>You will receive email notifications at the scheduled times. You can manage your recurring tasks from the dashboard.</p>
                </div>
            </body>
            </html>
            """,
            text_content=f"""
            Recurring Task Created!
            
            Hello {current_user.name or current_user.email.split("@")[0]},
            
            Your recurring task has been set up successfully.
            
            Task: {task_title}
            Pattern: {pattern_display} (every {interval} {recurrence_pattern})
            First Occurrence: {notification_time.strftime("%B %d, %Y at %I:%M %p %Z") if notification_time else "Started immediately"}
            
            You will receive email notifications at the scheduled times.
            """,
        )
        
        if email_sent:
            logger.info(f"Sent confirmation email for recurring task {base_task.id} to {current_user.email}")
        
        return {
            "success": True,
            "message": "Recurring task created with notifications",
            "task_id": str(base_task.id),
            "recurring_task_id": str(recurring_task.id),
            "pattern": recurrence_pattern,
            "first_occurrence_id": str(first_occurrence.id) if first_occurrence else None,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create recurring task with notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create recurring task: {str(e)}")
