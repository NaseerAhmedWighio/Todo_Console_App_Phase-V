# Data Model: Todo Full-Stack Web Application - Phase II

## Overview
This document defines the data models for the Todo Full-Stack Web Application, including entities, their attributes, relationships, and validation rules.

## Entity: User

### Attributes
- **id** (UUID, Primary Key)
  - Type: UUID
  - Required: Yes
  - Unique: Yes
  - Description: Unique identifier for the user

- **email** (String)
  - Type: String (max 255 characters)
  - Required: Yes
  - Unique: Yes
  - Validation: Valid email format
  - Description: User's email address for authentication

- **name** (String)
  - Type: String (max 255 characters)
  - Required: No
  - Unique: No
  - Description: User's display name (optional)

- **created_at** (DateTime)
  - Type: DateTime
  - Required: Yes
  - Default: Current timestamp
  - Description: Timestamp when the user record was created

- **updated_at** (DateTime)
  - Type: DateTime
  - Required: Yes
  - Default: Current timestamp, auto-updating
  - Description: Timestamp when the user record was last updated

### Relationships
- One User has many Tasks (one-to-many relationship)

### Validation Rules
- Email must be a valid email format
- Email must be unique across all users
- Name, if provided, must not exceed 255 characters

## Entity: Task

### Attributes
- **id** (UUID, Primary Key)
  - Type: UUID
  - Required: Yes
  - Unique: Yes
  - Description: Unique identifier for the task

- **title** (String)
  - Type: String (max 255 characters)
  - Required: Yes
  - Unique: No
  - Description: Title or summary of the task

- **description** (Text)
  - Type: Text (optional)
  - Required: No
  - Unique: No
  - Description: Detailed description of the task

- **completed** (Boolean)
  - Type: Boolean
  - Required: Yes
  - Default: False
  - Description: Whether the task has been completed

- **user_id** (UUID, Foreign Key)
  - Type: UUID
  - Required: Yes
  - Reference: users.id
  - Description: ID of the user who owns this task

- **created_at** (DateTime)
  - Type: DateTime
  - Required: Yes
  - Default: Current timestamp
  - Description: Timestamp when the task was created

- **updated_at** (DateTime)
  - Type: DateTime
  - Required: Yes
  - Default: Current timestamp, auto-updating
  - Description: Timestamp when the task was last updated

### Relationships
- One Task belongs to one User (many-to-one relationship)

### Validation Rules
- Title is required and must not exceed 255 characters
- Description, if provided, can be longer text
- Completed status defaults to False
- Each task must be associated with a valid user
- Users can only access tasks that belong to them

## Database Schema

### SQL Schema
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_user_completed ON tasks(user_id, completed);
```

### Indexes
- `idx_tasks_user_id`: For efficient retrieval of tasks by user
- `idx_tasks_completed`: For efficient filtering of completed/incomplete tasks
- `idx_tasks_user_completed`: For efficient retrieval of user's completed/incomplete tasks

## State Transitions

### Task State Transitions
- **Incomplete → Complete**: When user marks task as complete
- **Complete → Incomplete**: When user unmarks task as complete

### Validation on State Changes
- Only the owner of a task can change its completion status
- Task completion status can only be changed by authenticated users
- Task updates must be validated against the user's ownership

## Data Access Patterns

### Common Queries
1. Get all tasks for a specific user
2. Get completed tasks for a specific user
3. Get incomplete tasks for a specific user
4. Create a new task for a user
5. Update a task for a user
6. Delete a task for a user

### Security Considerations
- All queries must be filtered by user_id to ensure data isolation
- Users cannot access tasks belonging to other users
- Authentication must be validated before any data access