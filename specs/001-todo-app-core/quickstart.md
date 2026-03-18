# Quickstart Guide: Todo App Core Functionality

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Console/terminal access

### Setup
1. Navigate to the project directory
2. Run the application: `python src/main.py`

### Available Commands
- `add task <description>` - Add a new task
- `view tasks` - View all tasks
- `delete task <id>` - Delete a task by ID
- `update task <id> <new_description>` - Update a task description
- `mark complete <id>` - Mark a task as complete
- `mark incomplete <id>` - Mark a task as incomplete
- `help` - Show available commands
- `quit` or `exit` - Exit the application

### Example Usage
```
> add task Buy groceries
Task added successfully.

> add task Complete project
Task added successfully.

> view tasks
1. Buy groceries [Incomplete]
2. Complete project [Incomplete]

> mark complete 1
Task 1 marked as complete.

> view tasks
1. Buy groceries [Complete]
2. Complete project [Incomplete]

> quit
```

### Development
- Source code located in `src/` directory
- Tests located in `tests/` directory
- Run tests: `python -m pytest tests/`