import asyncio
import json
import logging
import traceback
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.auth_routes import router as auth_router
from app.api.chat_routes import limiter as chat_limiter
from app.api.chat_routes import router as chat_router
from app.api.jobs_routes import router as jobs_router
from app.api.recurring_routes import router as recurring_router
from app.api.reminder_routes import router as reminder_router
from app.api.search_routes import router as search_router
from app.api.tag_routes import router as tag_router
from app.api.todo_routes import router as todo_router
from app.database.session import create_db_and_tables

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    try:
        # Run database creation in a thread pool to avoid blocking
        await asyncio.get_event_loop().run_in_executor(None, create_db_and_tables)
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        print(traceback.format_exc())
    yield
    # Cleanup on shutdown if needed


def create_app():
    app = FastAPI(title="Todo API", version="1.0.0", lifespan=lifespan)

    # Add CORS middleware FIRST (before other middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://0.0.0.0:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Set the limiter on app.state for routes to use
    app.state.limiter = chat_limiter
    app.add_exception_handler(
        RateLimitExceeded,
        lambda r, e: JSONResponse(status_code=429, content={"detail": "Rate limit exceeded. Please try again later."}),
    )
    app.add_middleware(SlowAPIMiddleware)

    # Include API routes
    app.include_router(todo_router)
    app.include_router(auth_router)
    app.include_router(chat_router)
    app.include_router(tag_router)
    app.include_router(search_router)
    app.include_router(recurring_router)
    app.include_router(reminder_router)
    app.include_router(jobs_router)

    # Add WebSocket endpoint directly to the app
    @app.websocket("/ws/{user_id}")
    async def websocket_endpoint(websocket: WebSocket, user_id: str):
        """WebSocket endpoint for real-time updates with heartbeat support"""
        from app.api.websocket_manager import manager as websocket_manager

        await websocket_manager.connect(websocket, user_id)
        try:
            while True:
                # Keep the connection alive and handle messages
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    # Handle pong responses for heartbeat
                    if message.get("type") == "pong":
                        await websocket_manager.handle_pong(user_id)
                except json.JSONDecodeError:
                    # Non-JSON messages are ignored
                    pass
        except WebSocketDisconnect:
            websocket_manager.disconnect(websocket, user_id)
        except Exception as e:
            logger.error(f"WebSocket error for user {user_id}: {e}")
            websocket_manager.disconnect(websocket, user_id)

    @app.get("/")
    async def read_root():
        return {"message": "Todo API is running!"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    # Global exception handler to catch all unhandled exceptions
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # Log the error for debugging
        print(f"Unhandled exception: {str(exc)}")
        print(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(exc)}"},
            headers={
                "Access-Control-Allow-Origin": "http://localhost:3000",
                "Access-Control-Allow-Credentials": "true",
            },
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
