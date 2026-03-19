import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..api.todo_routes import get_current_user
from ..api.websocket_manager import manager as websocket_manager
from ..database.session import get_session
from ..models.tag import Tag, TagCreate, TagResponse, TagUpdate
from ..models.task_tag import TaskTag
from ..models.todo import Todo
from ..models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/tags", tags=["tags"])


@router.post("", response_model=TagResponse)
async def create_tag(
    tag_data: TagCreate, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> TagResponse:
    """Create a new tag"""
    try:
        logger.info(f"Creating tag for user {current_user.id}: name={tag_data.name}, color={tag_data.color}")

        # Check for duplicate (case-insensitive)
        existing = session.exec(
            select(Tag).where(Tag.user_id == current_user.id, Tag.name.ilike(tag_data.name))
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail=f'Tag "{tag_data.name}" already exists')

        # Create the tag
        tag = Tag(user_id=current_user.id, name=tag_data.name, color=tag_data.color or "#6B7280")
        session.add(tag)
        session.commit()
        session.refresh(tag)

        logger.info(f"Tag created successfully: {tag.id}")

        # Broadcast WebSocket event
        tag_dict = {
            "id": str(tag.id),
            "user_id": str(tag.user_id),
            "name": tag.name,
            "color": tag.color,
            "created_at": tag.created_at.isoformat(),
        }
        await websocket_manager.broadcast_tag_update("created", tag_dict, str(current_user.id))

        # Return response with usage_count=0 for new tags
        return TagResponse(
            id=tag.id, user_id=tag.user_id, name=tag.name, color=tag.color, created_at=tag.created_at, usage_count=0
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tag: {str(e)}")
        import traceback

        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create tag: {str(e)}")


@router.get("", response_model=List[dict])
def get_tags(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> List[dict]:
    """Get all tags for current user"""
    try:
        tags = session.exec(select(Tag).where(Tag.user_id == current_user.id).order_by(Tag.name)).all()

        # Convert to dict with usage count
        result = []
        for tag in tags:
            usage_count = session.exec(select(TaskTag).where(TaskTag.tag_id == tag.id)).all()
            tag_dict = {
                "id": str(tag.id),
                "user_id": str(tag.user_id),
                "name": tag.name,
                "color": tag.color,
                "created_at": tag.created_at.isoformat(),
                "usage_count": len(usage_count),
            }
            result.append(tag_dict)

        logger.info(f"Retrieved {len(result)} tags for user {current_user.id}")
        return result
    except Exception as e:
        logger.error(f"Error retrieving tags: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve tags: {str(e)}")


@router.get("/{tag_id}", response_model=dict)
def get_tag(
    tag_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
) -> dict:
    """Get a specific tag by ID"""
    try:
        uuid_id = uuid.UUID(tag_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid tag ID format")

    tag = session.get(Tag, uuid_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Get usage count
    usage_count = session.exec(select(TaskTag).where(TaskTag.tag_id == tag.id)).all()

    return {
        "id": str(tag.id),
        "user_id": str(tag.user_id),
        "name": tag.name,
        "color": tag.color,
        "created_at": tag.created_at.isoformat(),
        "usage_count": len(usage_count),
    }


@router.put("/{tag_id}", response_model=dict)
def update_tag(
    tag_id: str,
    tag_update: TagUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """Update an existing tag"""
    try:
        uuid_id = uuid.UUID(tag_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid tag ID format")

    tag = session.get(Tag, uuid_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Update fields
    update_data = tag_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(tag, field, value)

    session.add(tag)
    session.commit()
    session.refresh(tag)

    # Get usage count
    usage_count = session.exec(select(TaskTag).where(TaskTag.tag_id == tag.id)).all()

    return {
        "id": str(tag.id),
        "user_id": str(tag.user_id),
        "name": tag.name,
        "color": tag.color,
        "created_at": tag.created_at.isoformat(),
        "usage_count": len(usage_count),
    }


@router.delete("/{tag_id}")
async def delete_tag(
    tag_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    """Delete a tag (cascade removes from tasks)"""
    try:
        uuid_id = uuid.UUID(tag_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid tag ID format")

    tag = session.get(Tag, uuid_id)
    if not tag or tag.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Tag not found")

    # Prepare tag data for WebSocket event before deletion
    tag_dict = {
        "id": str(tag.id),
        "name": tag.name,
    }

    session.delete(tag)
    session.commit()

    # Broadcast WebSocket event
    await websocket_manager.broadcast_tag_update("deleted", tag_dict, str(current_user.id))

    return {"message": "Tag deleted successfully"}


@router.post("/{tag_id}/assign")
def assign_tag_to_task(
    tag_id: str, task_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    """Assign a tag to a task"""
    try:
        uuid_tag_id = uuid.UUID(tag_id)
        uuid_task_id = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    # Verify task and tag exist and belong to user
    task = session.get(Todo, uuid_task_id)
    tag = session.get(Tag, uuid_tag_id)

    if not task or not tag:
        raise HTTPException(status_code=404, detail="Task or tag not found")

    if task.user_id != current_user.id or tag.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check if already assigned
    existing = session.exec(
        select(TaskTag).where(TaskTag.task_id == uuid_task_id, TaskTag.tag_id == uuid_tag_id)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Tag already assigned to task")

    assignment = TaskTag(task_id=uuid_task_id, tag_id=uuid_tag_id)
    session.add(assignment)
    session.commit()

    return {"message": "Tag assigned successfully"}


@router.delete("/{tag_id}/unassign")
def unassign_tag_from_task(
    tag_id: str, task_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    """Remove a tag from a task"""
    try:
        uuid_tag_id = uuid.UUID(tag_id)
        uuid_task_id = uuid.UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    assignment = session.exec(
        select(TaskTag).where(TaskTag.task_id == uuid_task_id, TaskTag.tag_id == uuid_tag_id)
    ).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Tag assignment not found")

    # Verify ownership
    task = session.get(Todo, uuid_task_id)
    if not task or task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    session.delete(assignment)
    session.commit()

    return {"message": "Tag unassigned successfully"}


@router.get("/{tag_id}/tasks")
def get_tasks_by_tag(
    tag_id: str, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)
):
    """Get all tasks with a specific tag"""
    try:
        uuid_id = uuid.UUID(tag_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid tag ID format")

    # Get all task_ids with this tag
    task_tags = session.exec(select(TaskTag.task_id).where(TaskTag.tag_id == uuid_id)).all()

    if not task_tags:
        return []

    # Get tasks
    tasks = session.exec(select(Todo).where(Todo.user_id == current_user.id, Todo.id.in_(task_tags))).all()

    return [
        {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "is_completed": task.is_completed,
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat(),
            "updated_at": task.updated_at.isoformat(),
        }
        for task in tasks
    ]
