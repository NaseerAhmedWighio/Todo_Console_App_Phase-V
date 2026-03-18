# Backend Setup Complete ✅

## Quick Start

### Option 1: Using the Start Script (Recommended)
```bash
cd backend
start.bat
```

### Option 2: Using uvicorn directly
```bash
cd backend
uv run uvicorn main:app --reload --port 7860
```

### Option 3: Using Python
```bash
cd backend
python main.py
```

## Server Information

| Property | Value |
|----------|-------|
| **URL** | http://localhost:7860 |
| **API Docs** | http://localhost:7860/docs |
| **Health Check** | http://localhost:7860/health |
| **Database** | SQLite (todo_app.db) |

## Configuration

All configuration is in `backend/.env`:

```env
DATABASE_URL=sqlite:///./todo_app.db
JWT_SECRET=<your-secret-key>
OPENROUTER_API_KEY=<your-api-key>
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user

### Todos
- `GET /api/v1/todos` - List all todos
- `POST /api/v1/todos` - Create new todo
- `GET /api/v1/todos/{id}` - Get specific todo
- `PUT /api/v1/todos/{id}` - Update todo
- `DELETE /api/v1/todos/{id}` - Delete todo
- `PATCH /api/v1/todos/{id}/toggle` - Toggle completion

### Tags
- `GET /api/v1/tags` - List all tags
- `POST /api/v1/tags` - Create new tag
- `POST /api/v1/tags/{id}/assign` - Assign tag to task
- `DELETE /api/v1/tags/{id}/unassign` - Remove tag from task

### Chat (AI Agent)
- `POST /api/{user_id}/chat` - Send message to AI agent
- `GET /api/{user_id}/conversations` - List conversations
- `GET /api/{user_id}/conversations/{id}` - Get conversation history

### WebSocket
- `WS /ws/{user_id}` - Real-time updates

## Testing

### Test Health
```bash
curl http://localhost:7860/health
```

### Test Root
```bash
curl http://localhost:7860/
```

### Register a User
```bash
curl -X POST http://localhost:7860/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"name\":\"Test User\",\"password\":\"password123\"}"
```

## Troubleshooting

### Port already in use
If port 7860 is already in use, change it:
```bash
uv run uvicorn main:app --reload --port 8000
```

### Database errors
Delete the SQLite database and restart:
```bash
del todo_app.db
python main.py
```

### Module not found
Reinstall dependencies:
```bash
pip install -r requirements.txt
```

## Database

The backend uses **SQLite** for local development. The database file is created automatically at `backend/todo_app.db`.

To use **PostgreSQL** (Neon):
1. Get connection string from https://console.neon.tech/
2. Update `DATABASE_URL` in `.env`:
   ```env
   DATABASE_URL=postgresql://user:pass@host/neondb?sslmode=require
   ```

## API Key (Optional)

For AI chat features, add your OpenRouter API key to `.env`:
```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

Get a FREE key at: https://openrouter.ai/keys
