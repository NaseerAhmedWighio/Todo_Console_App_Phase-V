from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from ..database.session import get_session
from ..models.recurring_task import RecurringTask, RecurringTaskCreate, RecurringTaskUpdate, RecurringTaskResponse
from ..models.todo import Todo
from ..models.user import User
from ..api.todo_routes import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/recurring", tags=["recurring-tasks"])


@router.post("/tasks/{task_id}", response_model=RecurringTaskResponse)
def create_recurring_task(
    task_id: str,
    recurring_data: RecurringTaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
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
        end_condition=recurring_data.end_condition or 'never',
        end_occurrences=recurring_data.end_occurrences,
        end_date=recurring_data.end_date,
        is_active=True
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
    task_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
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
    session: Session = Depends(get_session)
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
    session: Session = Depends(get_session)
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
    active_only: bool = True,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> List[RecurringTaskResponse]:
    """List all recurring tasks for the current user"""
    statement = select(RecurringTask).join(Todo, RecurringTask.task_id == Todo.id).where(
        Todo.user_id == current_user.id
    )

    if active_only:
        statement = statement.where(RecurringTask.is_active == True)

    recurring_tasks = session.exec(statement).all()
    return [RecurringTaskResponse.model_validate(rt) for rt in recurring_tasks]
