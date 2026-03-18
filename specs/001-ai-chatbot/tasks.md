# Tasks: Todo AI Chatbot

## Phase 1: Setup

- [X] T001 Set up project dependencies for OpenAI SDK and MCP framework in backend/pyproject.toml
- [X] T002 Add environment variables for OpenAI API key to backend/.env
- [X] T003 [P] Create directory structure for new components: backend/app/models/conversation.py, backend/app/models/message.py, backend/app/api/chat_routes.py, backend/app/services/chat_service.py, backend/app/services/mcp_server.py

## Phase 2: Foundational Components

- [X] T004 Create Conversation model in backend/app/models/conversation.py with id, user_id, title, created_at, updated_at, metadata fields
- [X] T005 Create Message model in backend/app/models/message.py with id, conversation_id, role, content, timestamp, metadata fields
- [X] T006 Update database session to include Conversation and Message models in backend/app/database/session.py
- [X] T007 Create MCP server framework in backend/app/services/mcp_server.py with base tool definitions
- [X] T008 Implement JWT authentication middleware in backend/app/api/chat_routes.py for user validation
- [X] T009 Create chat service in backend/app/services/chat_service.py with conversation management functions

## Phase 3: User Story 1 - Add Task via Natural Language (Priority: P1)

- [X] T010 [US1] Implement add_task MCP tool in backend/app/services/mcp_server.py that creates tasks via natural language
- [X] T011 [US1] Create POST /api/{user_id}/chat endpoint in backend/app/api/chat_routes.py to handle chat requests
- [X] T012 [US1] Implement conversation history loading in backend/app/services/chat_service.py
- [X] T013 [US1] Store user and assistant messages in backend/app/services/chat_service.py
- [X] T014 [US1] Integrate OpenAI Agent with MCP tools in backend/app/services/chat_service.py
- [X] T015 [US1] Test add task functionality via chat: verify "Add a task to buy groceries tomorrow" creates task in user's list

## Phase 4: User Story 2 - List and View Tasks via Chat (Priority: P1)

- [X] T016 [US2] Implement list_tasks MCP tool in backend/app/services/mcp_server.py that retrieves user's tasks
- [X] T017 [US2] Integrate list_tasks tool with OpenAI Agent in backend/app/services/chat_service.py
- [X] T018 [US2] Test list tasks functionality via chat: verify "What are my tasks?" returns user's task list
- [X] T019 [US2] Handle case when user has no tasks in backend/app/services/chat_service.py

## Phase 5: User Story 3 - Update and Complete Tasks via Chat (Priority: P2)

- [X] T020 [US3] Implement update_task MCP tool in backend/app/services/mcp_server.py that updates existing tasks
- [X] T021 [US3] Implement complete_task MCP tool in backend/app/services/mcp_server.py that marks tasks as completed
- [X] T022 [US3] Implement delete_task MCP tool in backend/app/services/mcp_server.py that deletes tasks
- [X] T023 [US3] Integrate update/complete/delete tools with OpenAI Agent in backend/app/services/chat_service.py
- [X] T024 [US3] Test update task functionality via chat: verify "Mark the grocery task as done" updates task status
- [X] T025 [US3] Test update details functionality via chat: verify "Update my meeting task to next week" updates task details

## Phase 6: Frontend Integration

- [X] T026 Create ChatInterface component in frontend/src/components/ChatInterface.tsx using OpenAI ChatKit
- [X] T027 Implement chat service in frontend/src/services/chat.ts to communicate with backend API
- [X] T028 Connect frontend ChatInterface to backend chat endpoint in frontend/src/components/ChatInterface.tsx
- [X] T029 Display AI responses and confirmation messages in frontend/src/components/ChatInterface.tsx

## Phase 7: Validation and Testing

- [X] T030 Test all task operations (add/list/update/delete) via chat interface
- [X] T031 Test invalid task handling and error responses in backend/app/services/chat_service.py
- [X] T032 Test server restart recovery for conversation continuity
- [X] T033 Verify user data isolation: users cannot access other users' tasks or conversations
- [X] T034 Test JWT authentication enforcement for all chat endpoints
- [X] T035 Validate conversation and message persistence in database after server restart

## Phase 8: Polish & Cross-Cutting Concerns

- [X] T036 Add proper error handling and user-friendly messages throughout the chat flow
- [X] T037 Implement rate limiting for chat endpoints to prevent abuse
- [X] T038 Add logging for chat interactions and task operations
- [X] T039 Update documentation and add usage examples to quickstart guide
- [X] T040 Perform final integration testing of complete chatbot functionality

## Dependencies

User Story 2 (List tasks) depends on User Story 1 (Add task) foundational components being in place.
User Story 3 (Update/Complete tasks) depends on User Story 1 foundational components being in place.

## Parallel Execution Examples

- T004-T006 can be executed in parallel with T007-T009 (model creation and service creation)
- T010, T016, T020, T021, T022 can be implemented in parallel (MCP tools)
- T026-T029 can be executed in parallel with backend tasks (frontend implementation)

## Implementation Strategy

MVP scope includes User Story 1 (Add task via natural language) and basic chat endpoint functionality. Subsequent user stories can be implemented incrementally to add more capabilities.