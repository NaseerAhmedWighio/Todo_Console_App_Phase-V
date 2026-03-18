# ADR: AI Chatbot Implementation with OpenRouter API and Real-time Updates

## Status
Accepted

## Date
2026-01-20

## Context
We needed to implement an AI chatbot for the todo application that allows users to manage tasks through natural language commands. The requirements included:
- Integration with OpenRouter API for AI capabilities
- Popup chat interface for easy access
- Real-time UI updates when tasks are modified through the AI agent
- Consistent data model between frontend, backend, and AI agents

## Decision
We decided to:
1. Use OpenRouter API with the "xiaomi/mimo-v2-flash:free" model for cost-effective AI capabilities
2. Implement a popup chat interface using React components with inline styling
3. Create an OpenAI Agents SDK with custom tools for task operations (create, update, complete, delete, list)
4. Implement real-time updates using WebSocket connections between frontend and backend
5. Ensure field name consistency across all components (using "is_completed" instead of "completed")

## Alternatives Considered
- Using OpenAI API directly vs OpenRouter API: Chose OpenRouter for cost-effectiveness
- Full-page chat interface vs popup: Chose popup for non-intrusive UX
- Polling vs WebSocket for real-time updates: Chose WebSocket for efficiency
- Different AI models: Chose the free model initially with ability to switch later

## Consequences
### Positive
- Cost-effective AI implementation with free tier
- Non-intrusive UI that doesn't disrupt workflow
- Real-time updates provide immediate feedback to users
- Consistent data model prevents runtime errors
- Modular architecture allows for easy enhancements

### Negative
- Dependency on third-party API (OpenRouter)
- Additional complexity with WebSocket management
- Need for consistent field naming across all components

## Implementation Details
- Backend: FastAPI with SQLModel and PostgreSQL
- Frontend: Next.js with React and TypeScript
- Real-time updates: WebSocket connections via FastAPI WebSocket support
- AI integration: OpenRouter API with OpenAI Agents SDK
- Data consistency: Proper field name mapping between models and agents