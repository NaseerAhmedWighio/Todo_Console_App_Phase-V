"""
Search Service
Full-text search for tasks using PostgreSQL tsvector
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select, text

from ..models.task_tag import TaskTag

logger = logging.getLogger(__name__)


class SearchService:
    """Service for full-text search operations"""

    def __init__(self, session: Session):
        self.session = session

    def search_tasks(
        self,
        user_id: uuid.UUID,
        query: str,
        priority: Optional[str] = None,
        status: Optional[bool] = None,
        tag_id: Optional[uuid.UUID] = None,
        due_date_from: Optional[datetime] = None,
        due_date_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Full-text search across tasks

        Args:
            user_id: ID of the user
            query: Search query string
            priority: Optional priority filter
            status: Optional completion status filter
            tag_id: Optional tag filter
            due_date_from: Optional due date range start
            due_date_to: Optional due date range end
            limit: Maximum results to return
            offset: Result offset for pagination

        Returns:
            List of matching tasks with relevance score
        """
        # Build search query with filters - use simple ILIKE search for better compatibility
        search_sql = text("""
            SELECT t.*
            FROM todos t
            WHERE t.user_id = :user_id
              AND (
                t.title ILIKE '%' || :query || '%' OR
                t.description ILIKE '%' || :query || '%'
              )
              AND (:priority IS NULL OR t.priority = :priority)
              AND (:status IS NULL OR t.is_completed = :status)
              AND (:tag_id IS NULL OR t.id IN (
                  SELECT task_id FROM task_tags WHERE tag_id = :tag_id
              ))
              AND (:due_date_from IS NULL OR t.due_date >= :due_date_from)
              AND (:due_date_to IS NULL OR t.due_date <= :due_date_to)
            ORDER BY
                CASE WHEN t.title ILIKE '%' || :query || '%' THEN 0 ELSE 1 END,
                t.created_at DESC
            LIMIT :limit OFFSET :offset
        """)

        # Convert status properly for SQL
        sql_status = None
        if status is not None:
            if isinstance(status, bool):
                sql_status = status
            elif isinstance(status, str):
                sql_status = status.lower() == "true"
            else:
                sql_status = bool(status)

        params = {
            "user_id": user_id,
            "query": query or "",
            "priority": priority,
            "status": sql_status,
            "tag_id": tag_id,
            "due_date_from": due_date_from,
            "due_date_to": due_date_to,
            "limit": limit,
            "offset": offset,
        }

        results = self.session.execute(search_sql, params)
        tasks = []
        for row in results:
            # Get tags for this task
            task_tags = self.session.exec(select(TaskTag).where(TaskTag.task_id == row.id)).all()

            task_dict = {
                "id": str(row.id),
                "title": row.title,
                "description": row.description,
                "is_completed": row.is_completed,
                "priority": row.priority,
                "due_date": row.due_date.isoformat() if row.due_date else None,
                "created_at": row.created_at.isoformat(),
                "updated_at": row.updated_at.isoformat(),
                "task_tags": [
                    {
                        "tag": {
                            "id": str(tt.tag.id),
                            "name": tt.tag.name,
                            "color": tt.tag.color,
                        }
                    }
                    for tt in task_tags
                ],
            }
            tasks.append(task_dict)

        logger.info(f"Search query '{query}' returned {len(tasks)} results")
        return tasks

    def filter_tasks(
        self,
        user_id: uuid.UUID,
        priority: Optional[str] = None,
        status: Optional[bool] = None,
        tag_id: Optional[uuid.UUID] = None,
        due_date_from: Optional[datetime] = None,
        due_date_to: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Filter tasks without full-text search

        Args:
            user_id: ID of the user
            priority: Optional priority filter
            status: Optional completion status filter
            tag_id: Optional tag filter
            due_date_from: Optional due date range start
            due_date_to: Optional due date range end
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)
            limit: Maximum results to return
            offset: Result offset for pagination

        Returns:
            List of filtered tasks
        """
        # Build filter query
        filter_sql = text("""
            SELECT t.*
            FROM todos t
            WHERE t.user_id = :user_id
              AND (:priority IS NULL OR t.priority = :priority)
              AND (:status IS NULL OR t.is_completed = :status)
              AND (:tag_id IS NULL OR t.id IN (
                  SELECT task_id FROM task_tags WHERE tag_id = :tag_id
              ))
              AND (:due_date_from IS NULL OR t.due_date >= :due_date_from)
              AND (:due_date_to IS NULL OR t.due_date <= :due_date_to)
            ORDER BY
                CASE WHEN :sort_by = 'due_date' THEN t.due_date END ASC,
                CASE WHEN :sort_by = 'priority' THEN
                    CASE t.priority
                        WHEN 'urgent' THEN 1
                        WHEN 'high' THEN 2
                        WHEN 'medium' THEN 3
                        WHEN 'low' THEN 4
                    END
                END ASC,
                CASE WHEN :sort_by = 'created_at' THEN t.created_at END ASC,
                CASE WHEN :sort_by = 'title' THEN t.title END ASC
            LIMIT :limit OFFSET :offset
        """)

        # Apply sort order
        if sort_order == "desc":
            filter_sql = text(str(filter_sql).replace("ASC", "DESC"))

        # Convert status properly for SQL
        sql_status = None
        if status is not None:
            if isinstance(status, bool):
                sql_status = status
            elif isinstance(status, str):
                sql_status = status.lower() == "true"
            else:
                sql_status = bool(status)

        params = {
            "user_id": user_id,
            "priority": priority,
            "status": sql_status,
            "tag_id": tag_id,
            "due_date_from": due_date_from,
            "due_date_to": due_date_to,
            "sort_by": sort_by,
            "limit": limit,
            "offset": offset,
        }

        results = self.session.execute(filter_sql, params)
        tasks = []
        for row in results:
            # Get tags for this task
            task_tags = self.session.exec(select(TaskTag).where(TaskTag.task_id == row.id)).all()

            task_dict = {
                "id": str(row.id),
                "title": row.title,
                "description": row.description,
                "is_completed": row.is_completed,
                "priority": row.priority,
                "due_date": row.due_date.isoformat() if row.due_date else None,
                "created_at": row.created_at.isoformat(),
                "updated_at": row.updated_at.isoformat(),
                "task_tags": [
                    {
                        "tag": {
                            "id": str(tt.tag.id),
                            "name": tt.tag.name,
                            "color": tt.tag.color,
                        }
                    }
                    for tt in task_tags
                ],
            }
            tasks.append(task_dict)

        logger.info(f"Filter returned {len(tasks)} results")
        return tasks

    def update_search_vector(self, task_id: uuid.UUID):
        """
        Update search vector for a task (called on task create/update)

        Args:
            task_id: ID of the task
        """
        update_sql = text("""
            UPDATE todos
            SET search_vector = setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
                                setweight(to_tsvector('english', coalesce(description, '')), 'B') ||
                                setweight(to_tsvector('english', coalesce(priority, '')), 'C')
            WHERE id = :task_id
        """)

        self.session.execute(update_sql, {"task_id": task_id})
        self.session.commit()
        logger.debug(f"Updated search vector for task {task_id}")


# Global instance
_search_service: Optional[SearchService] = None


def get_search_service(session: Session) -> SearchService:
    """Get or create the search service instance"""
    global _search_service
    if _search_service is None:
        _search_service = SearchService(session)
    return _search_service
