# API Contracts: Todo Full-Stack Web Application - Phase II

## Overview
This document defines the API contracts for the Todo Full-Stack Web Application, specifying the endpoints, request/response formats, and authentication requirements.

## Authentication
All API endpoints (except authentication endpoints) require a valid JWT token in the Authorization header:
```
Authorization: Bearer {jwt_token}
```

## Common Response Format

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

## Endpoints

### Authentication Endpoints

#### POST /api/auth/register
Register a new user

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password",
  "name": "User Name"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "User Name"
    },
    "token": "jwt_token"
  },
  "message": "User registered successfully"
}
```

**Error Responses:**
- 400: Invalid input data
- 409: Email already exists

#### POST /api/auth/login
Login an existing user

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "email": "user@example.com",
      "name": "User Name"
    },
    "token": "jwt_token"
  },
  "message": "Login successful"
}
```

**Error Responses:**
- 400: Invalid input data
- 401: Invalid credentials

#### POST /api/auth/logout
Logout the current user

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Logout successful"
}
```

#### GET /api/auth/me
Get current user information

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "User Name",
    "created_at": "2023-01-01T00:00:00Z"
  }
}
```

**Error Responses:**
- 401: Unauthorized (invalid/expired token)

### Task Endpoints

#### GET /api/tasks
Get all tasks for the authenticated user

**Query Parameters:**
- `completed` (optional): Filter by completion status (true/false)
- `limit` (optional): Number of tasks to return (default: 50, max: 100)
- `offset` (optional): Number of tasks to skip (for pagination)

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": "uuid",
        "title": "Task title",
        "description": "Task description",
        "completed": false,
        "user_id": "uuid",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z"
      }
    ],
    "total": 1,
    "limit": 50,
    "offset": 0
  }
}
```

**Error Responses:**
- 401: Unauthorized (invalid/expired token)

#### POST /api/tasks
Create a new task for the authenticated user

**Request Body:**
```json
{
  "title": "Task title",
  "description": "Task description"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Task title",
    "description": "Task description",
    "completed": false,
    "user_id": "uuid",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  },
  "message": "Task created successfully"
}
```

**Error Responses:**
- 400: Invalid input data
- 401: Unauthorized (invalid/expired token)

#### GET /api/tasks/{task_id}
Get a specific task for the authenticated user

**Path Parameters:**
- `task_id`: UUID of the task

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Task title",
    "description": "Task description",
    "completed": false,
    "user_id": "uuid",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-01T00:00:00Z"
  }
}
```

**Error Responses:**
- 401: Unauthorized (invalid/expired token)
- 403: Forbidden (task doesn't belong to user)
- 404: Task not found

#### PUT /api/tasks/{task_id}
Update a specific task for the authenticated user

**Path Parameters:**
- `task_id`: UUID of the task

**Request Body:**
```json
{
  "title": "Updated task title",
  "description": "Updated task description",
  "completed": true
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Updated task title",
    "description": "Updated task description",
    "completed": true,
    "user_id": "uuid",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-02T00:00:00Z"
  },
  "message": "Task updated successfully"
}
```

**Error Responses:**
- 400: Invalid input data
- 401: Unauthorized (invalid/expired token)
- 403: Forbidden (task doesn't belong to user)
- 404: Task not found

#### DELETE /api/tasks/{task_id}
Delete a specific task for the authenticated user

**Path Parameters:**
- `task_id`: UUID of the task

**Success Response (200 OK):**
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

**Error Responses:**
- 401: Unauthorized (invalid/expired token)
- 403: Forbidden (task doesn't belong to user)
- 404: Task not found

#### PATCH /api/tasks/{task_id}/complete
Toggle the completion status of a task

**Path Parameters:**
- `task_id`: UUID of the task

**Request Body:**
```json
{
  "completed": true
}
```

**Success Response (200 OK):**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "title": "Task title",
    "description": "Task description",
    "completed": true,
    "user_id": "uuid",
    "created_at": "2023-01-01T00:00:00Z",
    "updated_at": "2023-01-02T00:00:00Z"
  },
  "message": "Task completion status updated"
}
```

**Error Responses:**
- 400: Invalid input data
- 401: Unauthorized (invalid/expired token)
- 403: Forbidden (task doesn't belong to user)
- 404: Task not found