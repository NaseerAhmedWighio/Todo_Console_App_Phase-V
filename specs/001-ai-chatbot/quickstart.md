# Quickstart Guide: Todo AI Chatbot

## Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- OpenAI API key
- MCP Server framework
- Existing todo app backend running

## Setup

### 1. Backend Configuration
```bash
# Navigate to backend directory
cd backend

# Install new dependencies
pip install openai python-multipart

# Add OpenAI API key to .env
echo "OPENAI_API_KEY=your_api_key_here" >> .env
```

### 2. Database Migration
```bash
# Run database migrations to add Conversation and Message tables
# (This will be handled by existing SQLModel setup)
```

### 3. MCP Server Setup
```bash
# Set up the MCP server for task operations
cd backend/agents-sdk
# Initialize the MCP server that exposes task operations as tools
```

### 4. Start Services
```bash
# Terminal 1: Start the main backend
cd backend
uvicorn main:app --reload

# Terminal 2: Start the MCP server
cd backend/agents-sdk
python mcp_server.py
```

## Usage

### 1. Initialize Chat Session
```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a task to buy groceries"}'
```

### 2. Continue Conversation
```bash
# Subsequent messages to the same conversation
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer {jwt_token}" \
  -H "Content-Type: application/json" \
  -d '{"message": "What are my tasks?", "conversation_id": "{conversation_uuid}"}'
```

## Example Interactions

### Adding Tasks
User: "Add a task to buy groceries tomorrow"
AI: "I've added the task 'buy groceries tomorrow' to your list."

### Listing Tasks
User: "What are my tasks?"
AI: "You have the following tasks:
- Buy groceries tomorrow
- Schedule dentist appointment"

### Updating Tasks
User: "Update my grocery task to say 'buy groceries including milk and bread'"
AI: "I've updated your grocery task to: 'buy groceries including milk and bread'"

### Completing Tasks
User: "Mark my grocery task as done"
AI: "I've marked your grocery task as completed."

### Deleting Tasks
User: "Delete my dentist appointment task"
AI: "I've deleted your dentist appointment task."

## Frontend Integration

To integrate the chat interface in your React application:

1. Make sure you have the AuthContext set up for authentication
2. Import and use the ChatInterface component:

```tsx
import ChatInterface from './components/ChatInterface';

function App() {
  return (
    <div className="app">
      <header>Todo App</header>
      <main>
        <ChatInterface />
      </main>
    </div>
  );
}
```

The ChatInterface component handles:
- Authentication via the AuthContext
- Sending messages to the backend API
- Displaying conversation history
- Showing loading states
- Error handling

## Key Components

### Chat Endpoint: `/api/{user_id}/chat`
- Handles authentication via JWT
- Loads conversation history from database
- Sends user message to AI agent
- Persists assistant response to database
- Returns formatted response to frontend

### MCP Tools
- `create_task`: Creates a new task
- `list_tasks`: Retrieves user's tasks
- `update_task`: Updates an existing task
- `complete_task`: Marks a task as completed
- `delete_task`: Deletes a task

## Environment Variables
- `OPENROUTER_API_KEY`: API key for OpenRouter services (using xiaomi/mimo-v2-flash:free model)
- `DATABASE_URL`: PostgreSQL connection string (inherits from main app)
- `JWT_SECRET`: Secret for JWT token verification (inherits from main app)