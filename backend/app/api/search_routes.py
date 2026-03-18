from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List, Optional
from ..database.session import get_session
from ..models.user import User
from ..services.search_service import SearchService, get_search_service
from ..api.todo_routes import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/search", tags=["search"])


def get_search_svc(session: Session = Depends(get_session)) -> SearchService:
    """Get search service instance"""
    return SearchService(session)


@router.get("")
def search_tasks(
    q: str = Query(..., description="Search query"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    status: Optional[bool] = Query(None, description="Filter by completion status"),
    tag_id: Optional[str] = Query(None, description="Filter by tag ID"),
    due_date_from: Optional[str] = Query(None, description="Filter by due date from (ISO format)"),
    due_date_to: Optional[str] = Query(None, description="Filter by due date to (ISO format)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Result offset"),
    current_user: User = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_svc)
):
    """
    Search tasks with full-text search and filters
    """
    # Parse optional parameters
    parsed_tag_id = None
    if tag_id:
        try:
            parsed_tag_id = uuid.UUID(tag_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tag_id format")

    parsed_due_date_from = None
    if due_date_from:
        try:
            parsed_due_date_from = datetime.fromisoformat(due_date_from.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date_from format")

    parsed_due_date_to = None
    if due_date_to:
        try:
            parsed_due_date_to = datetime.fromisoformat(due_date_to.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date_to format")

    # Perform search
    results = search_service.search_tasks(
        user_id=current_user.id,
        query=q,
        priority=priority,
        status=status,
        tag_id=parsed_tag_id,
        due_date_from=parsed_due_date_from,
        due_date_to=parsed_due_date_to,
        limit=limit,
        offset=offset
    )

    return {
        "success": True,
        "data": {
            "results": results,
            "total": len(results),
            "query": q,
            "limit": limit,
            "offset": offset
        }
    }


@router.get("/filter")
def filter_tasks(
    priority: Optional[str] = Query(None, description="Filter by priority"),
    status: Optional[bool] = Query(None, description="Filter by completion status"),
    tag_id: Optional[str] = Query(None, description="Filter by tag ID"),
    due_date_from: Optional[str] = Query(None, description="Filter by due date from (ISO format)"),
    due_date_to: Optional[str] = Query(None, description="Filter by due date to (ISO format)"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order (asc or desc)"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Result offset"),
    current_user: User = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_svc)
):
    """
    Filter tasks without full-text search
    """
    # Parse optional parameters
    parsed_tag_id = None
    if tag_id:
        try:
            parsed_tag_id = uuid.UUID(tag_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid tag_id format")

    parsed_due_date_from = None
    if due_date_from:
        try:
            parsed_due_date_from = datetime.fromisoformat(due_date_from.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date_from format")

    parsed_due_date_to = None
    if due_date_to:
        try:
            parsed_due_date_to = datetime.fromisoformat(due_date_to.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date_to format")

    # Perform filter
    results = search_service.filter_tasks(
        user_id=current_user.id,
        priority=priority,
        status=status,
        tag_id=parsed_tag_id,
        due_date_from=parsed_due_date_from,
        due_date_to=parsed_due_date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )

    return {
        "success": True,
        "data": {
            "results": results,
            "total": len(results),
            "limit": limit,
            "offset": offset
        }
    }
