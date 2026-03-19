import asyncio
import json
import os
from datetime import datetime
from typing import Optional
from uuid import UUID

import jwt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlmodel import Session, select

from ..database.session import get_session
from ..models.conversation import Conversation
from ..models.message import Message
from ..models.user import User
from ..services.mcp_server import MCPServer

# Load environment variables
load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize router
router = APIRouter(prefix="/api", tags=["chat"])

# Import ChatService lazily to avoid OpenAPI schema generation issues
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..services.chat_service import ChatService


def _get_chat_service(session: Session = Depends(get_session)):
    """Get ChatService instance (lazy import)"""
    from ..services.chat_service import ChatService

    mcp_server = MCPServer(session)
    return ChatService(mcp_server)


# Security scheme for JWT
security = HTTPBearer()

# Get JWT secret from environment
JWT_SECRET = os.getenv("JWT_SECRET")


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    timestamp: datetime


def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Verify JWT token and return decoded payload.
    This function acts as a dependency for routes that require authentication.
    """
    token = credentials.credentials

    try:
        # Decode the JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_user_from_token(payload: dict = Depends(verify_jwt_token), session: Session = Depends(get_session)) -> User:
    """
    Extract user information from JWT payload and verify user exists in database.
    """
    user_id = payload.get("sub")  # Use "sub" field as user_id (standard JWT claim)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing user_id",
        )

    try:
        user_uuid = UUID(user_id)
        user = session.get(User, user_uuid)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return user
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format",
        )


@router.post("/{user_id}/chat", response_model=ChatResponse)
@limiter.limit("10/minute")
async def chat_endpoint(
    request: Request,
    user_id: str,
    chat_request: ChatRequest,
    current_user: User = Depends(get_user_from_token),
    session: Session = Depends(get_session),
    chat_service: "ChatService" = Depends(_get_chat_service),
):
    """
    Enhanced chat endpoint with comprehensive task management
    """
    # Verify user ID matches
    if current_user.id != UUID(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: user ID mismatch")

    try:
        # Process message
        response_message = await chat_service.process_message(
            user_id=user_id, user_message=chat_request.message, conversation_id=chat_request.conversation_id
        )

        # Create or retrieve conversation
        if chat_request.conversation_id:
            try:
                conversation_uuid = UUID(chat_request.conversation_id)
                conversation = session.get(Conversation, conversation_uuid)

                if not conversation or str(conversation.user_id) != user_id:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conversation ID")
        else:
            conversation = Conversation(user_id=UUID(user_id))
            session.add(conversation)
            session.commit()
            session.refresh(conversation)

        # Save messages
        user_message = Message(conversation_id=conversation.id, role="user", content=chat_request.message)
        session.add(user_message)

        assistant_message = Message(conversation_id=conversation.id, role="assistant", content=response_message)
        session.add(assistant_message)

        # Update conversation
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)
        session.commit()

        return ChatResponse(conversation_id=str(conversation.id), message=response_message, timestamp=datetime.utcnow())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {str(e)}")


@router.get("/{user_id}/conversations", dependencies=[Depends(verify_jwt_token)])
@limiter.limit("20/minute")  # Allow 20 requests per minute per IP
async def list_user_conversations(
    request: Request,
    user_id: str,
    current_user: User = Depends(get_user_from_token),
    session: Session = Depends(get_session),
):
    """
    Retrieve all conversations for the authenticated user.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.id != UUID(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: user ID mismatch")

    try:
        conversations = session.exec(
            select(Conversation).where(Conversation.user_id == current_user.id).order_by(Conversation.updated_at.desc())
        ).all()

        return [
            {"id": str(conv.id), "title": conv.title, "created_at": conv.created_at, "updated_at": conv.updated_at}
            for conv in conversations
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving conversations: {str(e)}"
        )


@router.get("/{user_id}/conversations/{conversation_id}", dependencies=[Depends(verify_jwt_token)])
@limiter.limit("20/minute")  # Allow 20 requests per minute per IP
async def get_conversation_history(
    request: Request,
    user_id: str,
    conversation_id: str,
    current_user: User = Depends(get_user_from_token),
    session: Session = Depends(get_session),
):
    """
    Retrieve message history for a specific conversation.
    """
    # Verify that the user_id in the path matches the authenticated user
    if current_user.id != UUID(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: user ID mismatch")

    try:
        conversation_uuid = UUID(conversation_id)
        conversation = session.get(Conversation, conversation_uuid)

        if not conversation or conversation.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found or access denied")

        messages = session.exec(
            select(Message).where(Message.conversation_id == conversation_uuid).order_by(Message.timestamp.asc())
        ).all()

        return {
            "conversation_id": str(conversation.id),
            "title": conversation.title,
            "messages": [
                {"id": str(msg.id), "role": msg.role, "content": msg.content, "timestamp": msg.timestamp}
                for msg in messages
            ],
        }
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid conversation ID format")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error retrieving conversation history: {str(e)}"
        )


@router.post("/{user_id}/chat/stream", dependencies=[Depends(verify_jwt_token)])
@limiter.limit("5/minute")
async def stream_chat_endpoint(
    request: Request,
    user_id: str,
    chat_request: ChatRequest,
    current_user: User = Depends(get_user_from_token),
    session: Session = Depends(get_session),
):
    """
    Streaming chat endpoint for real-time token-by-token responses.
    Returns Server-Sent Events (SSE) stream.
    """
    # Verify user ID matches
    if current_user.id != UUID(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied: user ID mismatch")

    async def generate_stream():
        try:
            # Import chat service
            from ..services.chat_service import ChatService

            mcp_server = MCPServer(session)
            chat_service = ChatService(mcp_server)

            # Send start event
            yield f"data: {json.dumps({'type': 'start'})}\n\n"

            # Process message
            response_message = await chat_service.process_message(
                user_id=user_id, user_message=chat_request.message, conversation_id=chat_request.conversation_id
            )

            # Stream response word by word for real-time effect
            words = response_message.split()
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                await asyncio.sleep(0.05)  # 50ms delay between words for streaming effect

            # Send completion event
            yield f"data: {json.dumps({'type': 'end', 'content': response_message})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )
