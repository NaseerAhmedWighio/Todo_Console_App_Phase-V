# Research Summary: Todo AI Chatbot

## Decision: MCP Server Architecture for Task Operations
**Rationale**: MCP (Model Context Protocol) servers provide a standardized way to expose tools to AI agents, allowing the AI to understand and call specific functions. This aligns with the constitution requirement that AI agents must interact with tasks exclusively through MCP tools.

**Alternatives considered**:
- Direct database access (violates constitution principle III)
- REST API calls from agent (less standardized, harder to discover)
- GraphQL API (overly complex for simple task operations)

## Decision: OpenRouter API with Function Calling
**Rationale**: The OpenRouter API with function calling capabilities provides the best balance of natural language understanding and tool integration at no cost using the xiaomi/mimo-v2-flash:free model. It allows us to define specific functions (MCP tools) that the AI can call based on user intent.

**Alternatives considered**:
- OpenAI API (cost concerns)
- Anthropic Claude with tool use (vendor lock-in concerns)
- Self-hosted LLM with custom tool integration (higher complexity)

## Decision: Conversation Storage in PostgreSQL
**Rationale**: Using the existing Neon PostgreSQL database to store conversations and messages ensures consistency with the existing architecture and maintains the stateless backend requirement. The database will store conversation history to enable continuity after server restarts.

**Alternatives considered**:
- Redis for session storage (violates stateless requirement if used for persistence)
- File-based storage (less scalable and harder to manage)
- Separate document database (adds unnecessary complexity)

## Decision: JWT Authentication Integration
**Rationale**: Integrating with the existing Better Auth JWT system ensures that all chat interactions are properly authenticated and that users can only access their own tasks and conversations. This maintains the security model already established in the application.

**Alternatives considered**:
- Session-based authentication (requires server-side session storage, violating stateless requirement)
- API keys (less secure, harder to manage)
- OAuth tokens (overly complex for this use case)

## Decision: FastAPI Endpoint for Chat Interface
**Rationale**: Adding a new endpoint to the existing FastAPI application maintains consistency with the current architecture while providing a clean interface for the chat functionality. The endpoint will handle authentication, load conversation history, pass the request to the AI agent, and persist responses.

**Alternatives considered**:
- Separate microservice (adds deployment complexity)
- Serverless functions (may not maintain state properly)
- WebSocket connection (unnecessary complexity for this use case)