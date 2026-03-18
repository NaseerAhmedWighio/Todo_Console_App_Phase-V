# API Contracts: Todo App Core Functionality

## Command Interface Contracts

### Add Task Command
- **Command**: `add task <description>`
- **Input**: Task description string
- **Output**: Success message "Task added successfully."
- **Error Cases**:
  - Empty description → "Error: Task description cannot be empty"
- **Validation**: Description must be non-empty

### View Tasks Command
- **Command**: `view tasks`
- **Input**: None
- **Output**: Numbered list of tasks with completion status
- **Format**: `1. <description> [Complete/Incomplete]`
- **Error Cases**:
  - No tasks → "No tasks found."

### Delete Task Command
- **Command**: `delete task <id>`
- **Input**: Task ID (integer)
- **Output**: Success message "Task <id> deleted successfully."
- **Error Cases**:
  - Invalid ID → "Error: Task with ID <id> does not exist"

### Update Task Command
- **Command**: `update task <id> <new_description>`
- **Input**: Task ID (integer), new description string
- **Output**: Success message "Task <id> updated successfully."
- **Error Cases**:
  - Invalid ID → "Error: Task with ID <id> does not exist"
  - Empty description → "Error: Task description cannot be empty"

### Mark Complete Command
- **Command**: `mark complete <id>`
- **Input**: Task ID (integer)
- **Output**: Success message "Task <id> marked as complete."
- **Error Cases**:
  - Invalid ID → "Error: Task with ID <id> does not exist"

### Mark Incomplete Command
- **Command**: `mark incomplete <id>`
- **Input**: Task ID (integer)
- **Output**: Success message "Task <id> marked as incomplete."
- **Error Cases**:
  - Invalid ID → "Error: Task with ID <id> does not exist"