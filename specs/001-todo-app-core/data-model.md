# Data Model: Todo App Core Functionality

## Entity: Task

### Fields
- **id**: Integer (unique identifier, auto-incrementing)
- **description**: String (task description text)
- **completed**: Boolean (completion status, default: False)

### Validation Rules
- **id**: Must be unique within the task list, auto-generated
- **description**: Must be non-empty string, maximum 500 characters
- **completed**: Boolean value only (True/False)

### State Transitions
- **Incomplete → Complete**: When user marks task as complete
- **Complete → Incomplete**: When user marks task as incomplete

## Entity: TaskList

### Fields
- **tasks**: List of Task entities

### Operations
- **add_task**: Add a new Task to the list
- **get_task**: Retrieve a Task by id
- **update_task**: Modify a Task's description or completion status
- **delete_task**: Remove a Task from the list
- **get_all_tasks**: Retrieve all Tasks
- **clear_completed**: Remove all completed Tasks (optional future feature)

### Validation Rules
- **tasks**: Must maintain unique IDs across all tasks
- **operations**: Must validate task existence before operations