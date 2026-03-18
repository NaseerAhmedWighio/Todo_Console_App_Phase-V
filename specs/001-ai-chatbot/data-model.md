# Data Model: Todo AI Chatbot

## Entity: Conversation
- **id**: UUID (primary key)
- **user_id**: UUID (foreign key to User, required)
- **title**: String (optional, auto-generated from first message)
- **created_at**: DateTime (required, default now)
- **updated_at**: DateTime (required, auto-updated)
- **metadata**: JSON (optional, for storing conversation context)

**Relationships**:
- Belongs to one User
- Has many Messages

**Validation**:
- user_id must exist in Users table
- created_at must be in past or present
- updated_at must be >= created_at

## Entity: Message
- **id**: UUID (primary key)
- **conversation_id**: UUID (foreign key to Conversation, required)
- **role**: String enum ('user'|'assistant'|'system', required)
- **content**: Text (required, max 10000 chars)
- **timestamp**: DateTime (required, default now)
- **metadata**: JSON (optional, for storing message context)

**Relationships**:
- Belongs to one Conversation
- Belongs to one User (through Conversation)

**Validation**:
- conversation_id must exist in Conversations table
- role must be one of allowed values
- content length must be > 0 and <= 10000 chars

## Entity: Task (Existing)
- **id**: UUID (primary key, unchanged)
- **user_id**: UUID (foreign key to User, required, unchanged)
- **title**: String (required, unchanged)
- **description**: Text (optional, unchanged)
- **completed**: Boolean (required, default false, unchanged)
- **created_at**: DateTime (required, unchanged)
- **updated_at**: DateTime (required, unchanged)

**Note**: Task entity remains unchanged as it already exists in the system with appropriate relationships to User.

## Entity: User (Existing)
- **id**: UUID (primary key, unchanged)
- **email**: String (required, unique, unchanged)
- **password_hash**: String (required, unchanged)
- **created_at**: DateTime (required, unchanged)
- **updated_at**: DateTime (required, unchanged)

**Note**: User entity remains unchanged as it already exists in the system.