import os
import uuid
from datetime import datetime
from typing import List, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session, select

from ..api.websocket_manager import manager as websocket_manager
from ..database.session import get_session
from ..models.recurring_task import RecurringTask
from ..models.task_tag import TaskTag
from ..models.todo import Todo, TodoCreate, TodoResponse, TodoUpdate
from ..models.user import User

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)
) -> User:
    """Get current user from JWT token"""
    try:
        import uuid

        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Convert string to UUID
        user_id = uuid.UUID(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


router = APIRouter(prefix="/api/v1/todos", tags=["todos"], redirect_slashes=False)


@router.post("/", response_model=TodoResponse)
async def create_todo(
    todo: TodoCreate,
    auto_recurring: bool = Query(default=True, description="Enable automatic recurring detection"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TodoResponse:
    """Create a new todo item with optional smart recurring detection"""
    from app.services.recurring_detection_service import get_recurring_detection_service

    # Create the todo with the current user's ID
    db_todo = Todo(**todo.model_dump(), user_id=current_user.id)
    session.add(db_todo)
    session.flush()  # Get ID before commit

    # AUTO-DETECT RECURRING PATTERN
    if auto_recurring:
        detection_service = get_recurring_detection_service()

        detection_result = detection_service.detect_recurring(
            title=todo.title, description=todo.description, due_date=todo.due_date
        )

        # If high confidence recurring detected, auto-configure
        if detection_result["is_recurring"] and detection_result["confidence"] >= 0.7:
            try:
                # Calculate next due date
                from dateutil.rrule import DAILY, MONTHLY, WEEKLY, YEARLY

                pattern_map = {
                    "daily": DAILY,
                    "weekly": WEEKLY,
                    "monthly": MONTHLY,
                    "yearly": YEARLY,
                }

                freq = pattern_map.get(detection_result["pattern"], MONTHLY)
                interval = detection_result["interval"] or 1

                # Calculate next occurrence
                from dateutil.rrule import rrule

                start_date = todo.due_date or datetime.now()
                if start_date.tzinfo is None:
                    start_date = start_date.replace(tzinfo=datetime.now().astimezone().tzinfo)

                rule = rrule(freq=freq, interval=interval, dtstart=start_date, count=2)
                occurrences = list(rule)
                next_due = occurrences[1] if len(occurrences) > 1 else start_date

                # Create recurring task configuration
                recurring_task = RecurringTask(
                    task_id=db_todo.id,
                    recurrence_pattern=detection_result["pattern"],
                    interval=interval,
                    is_active=True,
                    next_due_date=next_due,
                )

                # Mark base task as recurring
                db_todo.is_recurring = True
                db_todo.recurring_task_id = recurring_task.id

                session.add(recurring_task)
                session.add(db_todo)

                print(
                    f"Auto-detected recurring task: {detection_result['reason']} (confidence: {detection_result['confidence']:.2f})"
                )
            except Exception as e:
                print(f"Error creating recurring task config: {e}")
                # Continue with task creation even if recurring setup fails

    session.commit()
    session.refresh(db_todo)

    # Publish Kafka event via Dapr Pub/Sub
    try:
        from app.services.event_service import get_event_service

        event_service = get_event_service()
        await event_service.publish_task_created(
            task_id=db_todo.id,
            task_data={
                "id": str(db_todo.id),
                "title": db_todo.title,
                "description": db_todo.description,
                "is_completed": db_todo.is_completed,
                "priority": db_todo.priority,
                "due_date": db_todo.due_date.isoformat() if db_todo.due_date else None,
                "is_recurring": db_todo.is_recurring,
            },
            user_id=current_user.id,
        )
    except Exception as e:
        print(f"Warning: Failed to publish task created event: {e}")

    # Broadcast WebSocket event
    task_data = {
        "id": str(db_todo.id),
        "title": db_todo.title,
        "description": db_todo.description,
        "is_completed": db_todo.is_completed,
        "priority": db_todo.priority,
        "due_date": db_todo.due_date.isoformat() if db_todo.due_date else None,
        "created_at": db_todo.created_at.isoformat(),
        "updated_at": db_todo.updated_at.isoformat(),
        "is_recurring": db_todo.is_recurring,
    }
    await websocket_manager.broadcast_task_update("created", task_data, str(current_user.id))

    return TodoResponse.model_validate(db_todo)


@router.get("/", response_model=List[dict])
def read_todos(
    skip: int = 0,
    limit: int = 100,
    status: Optional[bool] = Query(None, description="Filter by completion status (true=completed, false=pending)"),
    priority: Optional[str] = Query(None, description="Filter by priority level (low, medium, high, urgent)"),
    tag_id: Optional[str] = Query(None, description="Filter by tag ID"),
    due_date_from: Optional[str] = Query(None, description="Filter by due date from (ISO format)"),
    due_date_to: Optional[str] = Query(None, description="Filter by due date to (ISO format)"),
    sort_by: str = Query(
        "created_at", description="Field to sort by (created_at, updated_at, due_date, priority, title)"
    ),
    sort_order: str = Query("desc", description="Sort order (asc or desc)"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> List[dict]:
    """Get current user's todo items with optional filtering, sorting, and pagination"""
    from sqlalchemy.orm import selectinload
    from sqlmodel import select as sql_select

    # Use selectinload to eagerly load task_tags relationship
    statement = (
        sql_select(Todo)
        .where(Todo.user_id == current_user.id)
        .options(selectinload(Todo.task_tags))
        .options(selectinload(Todo.task_tags).selectinload(TaskTag.tag))
    )

    # Apply status filter
    if status is not None:
        statement = statement.where(Todo.is_completed == status)

    # Apply priority filter
    if priority is not None:
        statement = statement.where(Todo.priority == priority)

    # Apply tag filter
    if tag_id is not None:
        try:
            tag_uuid = uuid.UUID(tag_id)
            tag_subquery = select(TaskTag.task_id).where(TaskTag.tag_id == tag_uuid)
            statement = statement.where(Todo.id.in_(tag_subquery))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tag_id format")

    # Apply due date range filter
    if due_date_from:
        try:
            due_date_from_dt = datetime.fromisoformat(due_date_from.replace("Z", "+00:00"))
            statement = statement.where(Todo.due_date >= due_date_from_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date_from format")

    if due_date_to:
        try:
            due_date_to_dt = datetime.fromisoformat(due_date_to.replace("Z", "+00:00"))
            statement = statement.where(Todo.due_date <= due_date_to_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date_to format")

    # Apply sorting
    from sqlmodel import col

    if sort_by == "due_date":
        statement = statement.order_by(col(Todo.due_date).asc() if sort_order == "asc" else col(Todo.due_date).desc())
    elif sort_by == "priority":
        # Custom priority ordering: urgent > high > medium > low
        if sort_order == "asc":
            priority_case = col(Todo.priority).case([("urgent", 1), ("high", 2), ("medium", 3), ("low", 4)], else_=5)
        else:
            priority_case = col(Todo.priority).case([("urgent", 4), ("high", 3), ("medium", 2), ("low", 1)], else_=0)
        statement = statement.order_by(priority_case)
    elif sort_by == "created_at":
        statement = statement.order_by(
            col(Todo.created_at).asc() if sort_order == "asc" else col(Todo.created_at).desc()
        )
    elif sort_by == "updated_at":
        statement = statement.order_by(
            col(Todo.updated_at).asc() if sort_order == "asc" else col(Todo.updated_at).desc()
        )
    elif sort_by == "title":
        statement = statement.order_by(col(Todo.title).asc() if sort_order == "asc" else col(Todo.title).desc())

    # Apply pagination
    statement = statement.offset(skip).limit(limit)

    todos = session.exec(statement).all()

    # Convert to response with tags
    result = []
    for todo in todos:
        todo_dict = {
            "id": str(todo.id),
            "title": todo.title,
            "description": todo.description,
            "is_completed": todo.is_completed,
            "priority": todo.priority,
            "due_date": todo.due_date.isoformat() if todo.due_date else None,
            "created_at": todo.created_at.isoformat(),
            "updated_at": todo.updated_at.isoformat(),
            "task_tags": [
                {
                    "tag": {
                        "id": str(tt.tag.id),
                        "name": tt.tag.name,
                        "color": tt.tag.color,
                    }
                }
                for tt in todo.task_tags or []
            ],
        }
        result.append(todo_dict)

    return result


@router.get("/{todo_id}", response_model=TodoResponse)
def read_todo(
    todo_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> TodoResponse:
    """Get a specific todo item by ID"""
    import uuid

    try:
        # Convert the string ID to UUID
        uuid_id = uuid.UUID(todo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid todo ID format")

    todo = session.get(Todo, uuid_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Check if the todo belongs to the current user
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: You can only access your own tasks")

    return TodoResponse.model_validate(todo)


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: str,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> TodoResponse:
    """Update a specific todo item"""
    import uuid
    from datetime import datetime

    try:
        # Convert the string ID to UUID
        uuid_id = uuid.UUID(todo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid todo ID format")

    db_todo = session.get(Todo, uuid_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Check if the todo belongs to the current user
    if db_todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: You can only update your own tasks")

    # Update the todo with provided values
    update_data = todo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        # Handle due_date parsing from string to datetime
        if field == "due_date" and isinstance(value, str):
            try:
                value = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                # Try parsing without timezone
                try:
                    value = datetime.fromisoformat(value)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid due_date format")
        setattr(db_todo, field, value)

    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)

    # Publish Kafka event via Dapr Pub/Sub
    try:
        from app.services.event_service import get_event_service

        event_service = get_event_service()
        await event_service.publish_task_updated(
            task_id=db_todo.id,
            task_data={
                "id": str(db_todo.id),
                "title": db_todo.title,
                "description": db_todo.description,
                "is_completed": db_todo.is_completed,
                "priority": db_todo.priority,
                "due_date": db_todo.due_date.isoformat() if db_todo.due_date else None,
            },
            user_id=current_user.id,
            changes=update_data,
        )
    except Exception as e:
        print(f"Warning: Failed to publish task updated event: {e}")

    # Broadcast WebSocket event
    task_data = {
        "id": str(db_todo.id),
        "title": db_todo.title,
        "description": db_todo.description,
        "is_completed": db_todo.is_completed,
        "priority": db_todo.priority,
        "due_date": db_todo.due_date.isoformat() if db_todo.due_date else None,
        "created_at": db_todo.created_at.isoformat(),
        "updated_at": db_todo.updated_at.isoformat(),
    }
    await websocket_manager.broadcast_task_update("updated", task_data, str(current_user.id))

    return TodoResponse.model_validate(db_todo)


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    """Delete a specific todo item"""
    import uuid

    try:
        # Convert the string ID to UUID
        uuid_id = uuid.UUID(todo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid todo ID format")

    todo = session.get(Todo, uuid_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Check if the todo belongs to the current user
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: You can only delete your own tasks")

    # Prepare task data for WebSocket event before deletion
    task_data = {
        "id": str(todo.id),
        "title": todo.title,
    }

    # Publish Kafka event via Dapr Pub/Sub
    try:
        from app.services.event_service import get_event_service

        event_service = get_event_service()
        await event_service.publish_task_deleted(
            task_id=todo.id,
            task_data={
                "id": str(todo.id),
                "title": todo.title,
            },
            user_id=current_user.id,
        )
    except Exception as e:
        print(f"Warning: Failed to publish task deleted event: {e}")

    session.delete(todo)
    session.commit()

    # Broadcast WebSocket event
    await websocket_manager.broadcast_task_update("deleted", task_data, str(current_user.id))

    return {"message": "Todo deleted successfully"}


@router.patch("/{todo_id}/toggle", response_model=TodoResponse)
async def toggle_todo_completion(
    todo_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> TodoResponse:
    """Toggle the completion status of a todo item"""
    import uuid

    try:
        # Convert the string ID to UUID
        uuid_id = uuid.UUID(todo_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid todo ID format")

    todo = session.get(Todo, uuid_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Check if the todo belongs to the current user
    if todo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied: You can only toggle your own tasks")

    todo.is_completed = not todo.is_completed
    session.add(todo)
    session.commit()
    session.refresh(todo)

    # Publish Kafka event via Dapr Pub/Sub
    try:
        from app.services.event_service import get_event_service

        event_service = get_event_service()
        await event_service.publish_task_completed(
            task_id=todo.id,
            task_data={
                "id": str(todo.id),
                "title": todo.title,
                "description": todo.description,
                "is_completed": todo.is_completed,
                "priority": todo.priority,
                "due_date": todo.due_date.isoformat() if todo.due_date else None,
            },
            user_id=current_user.id,
        )
    except Exception as e:
        print(f"Warning: Failed to publish task completed event: {e}")

    # Broadcast WebSocket event
    task_data = {
        "id": str(todo.id),
        "title": todo.title,
        "description": todo.description,
        "is_completed": todo.is_completed,
        "priority": todo.priority,
        "due_date": todo.due_date.isoformat() if todo.due_date else None,
        "created_at": todo.created_at.isoformat(),
        "updated_at": todo.updated_at.isoformat(),
    }
    await websocket_manager.broadcast_task_update("updated", task_data, str(current_user.id))

    return TodoResponse.model_validate(todo)


@router.post("/detect-recurring")
async def detect_recurring_pattern(
    title: str,
    description: Optional[str] = None,
    due_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """
    Detect if a task should be recurring based on title and description
    This endpoint is used by the UI to show smart suggestions
    """
    from app.services.recurring_detection_service import get_recurring_detection_service

    detection_service = get_recurring_detection_service()

    # Parse due date if provided
    parsed_due_date = None
    if due_date:
        try:
            parsed_due_date = datetime.fromisoformat(due_date.replace("Z", "+00:00"))
        except ValueError:
            pass

    # Detect recurring pattern
    result = detection_service.detect_recurring(title=title, description=description, due_date=parsed_due_date)

    return result
