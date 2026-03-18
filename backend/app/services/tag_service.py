"""
Tag Service
Business logic for tag operations
"""

from typing import List, Optional
from sqlmodel import Session, select
import uuid
import logging

from ..models.tag import Tag, TagCreate, TagUpdate
from ..models.task_tag import TaskTag
from ..models.todo import Todo

logger = logging.getLogger(__name__)


class TagService:
    """Service for tag operations"""

    def __init__(self, session: Session):
        self.session = session

    def create_tag(self, user_id: uuid.UUID, name: str, color: str = "#6B7280") -> Tag:
        """
        Create a new tag

        Args:
            user_id: ID of the user
            name: Tag name
            color: Hex color code

        Returns:
            Created Tag

        Raises:
            ValueError: If tag with same name already exists for user
        """
        # Check for duplicate (case-insensitive)
        existing = self.session.exec(
            select(Tag).where(
                Tag.user_id == user_id,
                Tag.name.ilike(name)
            )
        ).first()

        if existing:
            raise ValueError(f'Tag "{name}" already exists')

        tag = Tag(user_id=user_id, name=name, color=color)
        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)
        logger.info(f"Created tag {tag.id} for user {user_id}")
        return tag

    def get_tags(self, user_id: uuid.UUID) -> List[Tag]:
        """
        Get all tags for a user with usage count

        Args:
            user_id: ID of the user

        Returns:
            List of Tags with usage_count
        """
        # Get all tags for user
        tags = self.session.exec(
            select(Tag).where(Tag.user_id == user_id).order_by(Tag.name)
        ).all()

        # Calculate usage count for each tag
        tags_with_count = []
        for tag in tags:
            usage_count = self.session.exec(
                select(TaskTag).where(TaskTag.tag_id == tag.id)
            ).all()
            tag.usage_count = len(usage_count)  # type: ignore
            tags_with_count.append(tag)

        return tags_with_count

    def get_tag_by_id(self, tag_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Tag]:
        """
        Get a single tag by ID

        Args:
            tag_id: ID of the tag
            user_id: ID of the user (for authorization)

        Returns:
            Tag or None
        """
        tag = self.session.get(Tag, tag_id)
        if tag and tag.user_id != user_id:
            return None
        return tag

    def update_tag(self, tag_id: uuid.UUID, user_id: uuid.UUID, update_data: TagUpdate) -> Optional[Tag]:
        """
        Update an existing tag

        Args:
            tag_id: ID of the tag
            user_id: ID of the user (for authorization)
            update_data: Fields to update

        Returns:
            Updated Tag or None
        """
        tag = self.session.get(Tag, tag_id)
        if not tag or tag.user_id != user_id:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if value is not None:
                setattr(tag, field, value)

        self.session.add(tag)
        self.session.commit()
        self.session.refresh(tag)
        logger.info(f"Updated tag {tag.id}")
        return tag

    def delete_tag(self, tag_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Delete a tag (cascade removes from tasks)

        Args:
            tag_id: ID of the tag
            user_id: ID of the user (for authorization)

        Returns:
            True if deleted, False if not found
        """
        tag = self.session.get(Tag, tag_id)
        if not tag or tag.user_id != user_id:
            return False

        self.session.delete(tag)
        self.session.commit()
        logger.info(f"Deleted tag {tag.id}")
        return True

    def assign_tag_to_task(self, task_id: uuid.UUID, tag_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Assign a tag to a task

        Args:
            task_id: ID of the task
            tag_id: ID of the tag
            user_id: ID of the user (for authorization)

        Returns:
            True if assigned, False if already assigned or not found
        """
        # Verify task and tag belong to user
        task = self.session.get(Todo, task_id)
        tag = self.session.get(Tag, tag_id)

        if not task or not tag:
            return False

        if task.user_id != user_id or tag.user_id != user_id:
            return False

        # Check if already assigned
        existing = self.session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_id
            )
        ).first()

        if existing:
            return False  # Already assigned

        assignment = TaskTag(task_id=task_id, tag_id=tag_id)
        self.session.add(assignment)
        self.session.commit()
        logger.info(f"Assigned tag {tag_id} to task {task_id}")
        return True

    def unassign_tag_from_task(self, task_id: uuid.UUID, tag_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Remove a tag from a task

        Args:
            task_id: ID of the task
            tag_id: ID of the tag
            user_id: ID of the user (for authorization)

        Returns:
            True if unassigned, False if not found
        """
        assignment = self.session.exec(
            select(TaskTag).where(
                TaskTag.task_id == task_id,
                TaskTag.tag_id == tag_id
            )
        ).first()

        if not assignment:
            return False

        # Verify ownership
        task = self.session.get(Todo, task_id)
        if not task or task.user_id != user_id:
            return False

        self.session.delete(assignment)
        self.session.commit()
        logger.info(f"Unassigned tag {tag_id} from task {task_id}")
        return True

    def get_tasks_by_tag(self, user_id: uuid.UUID, tag_id: uuid.UUID) -> List[Todo]:
        """
        Get all tasks with a specific tag

        Args:
            user_id: ID of the user
            tag_id: ID of the tag

        Returns:
            List of Tasks
        """
        # Get all task_ids with this tag
        task_tags = self.session.exec(
            select(TaskTag.task_id).where(TaskTag.tag_id == tag_id)
        ).all()

        if not task_tags:
            return []

        # Get tasks
        tasks = self.session.exec(
            select(Todo).where(
                Todo.user_id == user_id,
                Todo.id.in_(task_tags)
            )
        ).all()

        return tasks

    def get_tags_for_task(self, task_id: uuid.UUID, user_id: uuid.UUID) -> List[Tag]:
        """
        Get all tags assigned to a task

        Args:
            task_id: ID of the task
            user_id: ID of the user (for authorization)

        Returns:
            List of Tags
        """
        # Verify task ownership
        task = self.session.get(Todo, task_id)
        if not task or task.user_id != user_id:
            return []

        # Get tag_ids for this task
        task_tags = self.session.exec(
            select(TaskTag.tag_id).where(TaskTag.task_id == task_id)
        ).all()

        if not task_tags:
            return []

        # Get tags
        tags = self.session.exec(
            select(Tag).where(Tag.id.in_(task_tags))
        ).all()

        return tags


# Global instance
_tag_service: Optional[TagService] = None


def get_tag_service(session: Session) -> TagService:
    """Get or create the tag service instance"""
    global _tag_service
    if _tag_service is None:
        _tag_service = TagService(session)
    return _tag_service
