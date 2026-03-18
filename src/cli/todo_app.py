"""
Command-line interface for the Todo App Core Functionality.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from services.task_service import TaskService
from models.task import Task
from typing import List


class TodoApp:
    """Main application class for the Todo CLI application."""

    def __init__(self):
        """Initialize the TodoApp with a TaskService."""
        self.task_service = TaskService()
        self.running = True

    def run(self):
        """Run the main application loop."""
        print("Welcome to the Todo App!")
        print("Type 'help' for available commands or 'quit' to exit.")

        while self.running:
            try:
                command = input("\n> ").strip()
                self.process_command(command)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except EOFError:
                print("\nGoodbye!")
                break

    def process_command(self, command: str):
        """Process a user command."""
        if not command:
            return

        parts = command.split()
        main_cmd = parts[0].lower()

        if main_cmd == "quit" or main_cmd == "exit":
            self.handle_quit()
        elif main_cmd == "help":
            self.handle_help()
        elif main_cmd == "add" and len(parts) > 1 and parts[1].lower() == "task":
            self.handle_add_task(command)
        elif main_cmd == "view" and len(parts) > 1 and parts[1].lower() == "tasks":
            self.handle_view_tasks()
        elif main_cmd == "delete" and len(parts) > 1 and parts[1].lower() == "task":
            self.handle_delete_task(command)
        elif main_cmd == "update" and len(parts) > 1 and parts[1].lower() == "task":
            self.handle_update_task(command)
        elif main_cmd == "mark" and len(parts) > 1:
            self.handle_mark_task(command)
        else:
            print("Invalid command. Type 'help' for available commands.")

    def handle_add_task(self, command: str):
        """Handle the 'add task' command."""
        try:
            # Extract the task title and description after 'add task'
            # Format: add task "title" "description" or add task title description
            # We'll use a simple approach: first word is title, rest is description
            parts = command.split(' ', 2)  # Split into at most 3 parts: ['add', 'task', 'rest_of_command']

            if len(parts) < 3:
                print("Usage: add task <title> [description]")
                return

            # Extract title and description from the remaining command
            rest = parts[2]
            title, description = self._parse_title_description(rest)

            if not title:
                print("Error: Task title cannot be empty")
                return

            task = self.task_service.add_task(title, description)
            if task:
                print("Task added successfully.")
            else:
                print("Error: Task title cannot be empty")
        except Exception as e:
            print(f"Error adding task: {str(e)}")

    def _parse_title_description(self, text: str) -> tuple:
        """Parse title and description from input text.

        Args:
            text: Input text that may contain title and description

        Returns:
            tuple: (title, description)
        """
        text = text.strip()
        if not text:
            return "", ""

        # Check if the text is in quoted format like: "title" "description"
        if text.startswith('"'):
            # Find the first quoted string (title)
            first_quote_end = text.find('"', 1)
            if first_quote_end != -1:
                title = text[1:first_quote_end]  # Extract title from quotes
                description_part = text[first_quote_end+1:].strip()

                # Check if there's a second quoted string for description
                if description_part.startswith('"'):
                    second_quote_end = description_part.find('"', 1)
                    if second_quote_end != -1:
                        description = description_part[1:second_quote_end]
                        return title, description
                    else:
                        # If second quote is not properly closed, treat the rest as description
                        description = description_part[1:]  # Remove the opening quote
                        return title, description
                else:
                    # No second quoted string, use the rest as description
                    description = description_part
                    return title, description
            else:
                # Malformed quotes, treat as single word
                return text, ""

        # No quotes - for predictable behavior, we'll split at the first space
        # This means "Buy groceries milk and bread" will have title="Buy" and description="groceries milk and bread"
        # Users should use quotes if they want multi-word titles: "Buy groceries" "milk and bread"
        words = text.split(' ', 1)
        title = words[0] if words else ""
        description = words[1] if len(words) > 1 else ""
        return title, description

    def handle_view_tasks(self):
        """Handle the 'view tasks' command."""
        tasks = self.task_service.get_all_tasks()

        if not tasks:
            print("No tasks found.")
            return

        for task in tasks:
            print(task)

    def handle_delete_task(self, command: str):
        """Handle the 'delete task' command."""
        try:
            # Extract task ID after 'delete task'
            parts = command.split()
            if len(parts) < 3:
                print("Usage: delete task <id>")
                return

            task_id = int(parts[2])
            success = self.task_service.delete_task(task_id)

            if success:
                print(f"Task {task_id} deleted successfully.")
            else:
                print(f"Error: Task with ID {task_id} does not exist")
        except ValueError:
            print("Error: Task ID must be a number")
        except Exception as e:
            print(f"Error deleting task: {str(e)}")

    def handle_update_task(self, command: str):
        """Handle the 'update task' command."""
        try:
            # Extract task ID and new title/description from 'update task <id> <title> [description]'
            parts = command.split(' ', 3)  # Split into at most 4 parts
            if len(parts) < 4:
                print("Usage: update task <id> <new_title> [new_description]")
                return

            task_id = int(parts[2])
            rest = parts[3]
            new_title, new_description = self._parse_title_description(rest)

            success = self.task_service.update_task(task_id, new_title, new_description)

            if success:
                print(f"Task {task_id} updated successfully.")
            else:
                print(f"Error: Task with ID {task_id} does not exist")
        except ValueError:
            print("Error: Task ID must be a number")
        except Exception as e:
            print(f"Error updating task: {str(e)}")

    def handle_mark_task(self, command: str):
        """Handle the 'mark complete' or 'mark incomplete' command."""
        try:
            parts = command.split()
            if len(parts) < 3:
                print("Usage: mark complete <id> or mark incomplete <id>")
                return

            action = parts[1].lower()
            task_id = int(parts[2])

            if action == "complete":
                success = self.task_service.mark_complete(task_id)
                if success:
                    print(f"Task {task_id} marked as complete.")
                else:
                    print(f"Error: Task with ID {task_id} does not exist")
            elif action == "incomplete":
                success = self.task_service.mark_incomplete(task_id)
                if success:
                    print(f"Task {task_id} marked as incomplete.")
                else:
                    print(f"Error: Task with ID {task_id} does not exist")
            else:
                print("Usage: mark complete <id> or mark incomplete <id>")
        except ValueError:
            print("Error: Task ID must be a number")
        except Exception as e:
            print(f"Error marking task: {str(e)}")

    def handle_quit(self):
        """Handle the 'quit' command."""
        self.running = False
        print("Goodbye!")

    def handle_help(self):
        """Handle the 'help' command."""
        print("\nAvailable commands:")
        print("  add task <title> [desc]  - Add a new task with title and optional description")
        print("  view tasks               - View all tasks")
        print("  delete task <id>         - Delete a task by ID")
        print("  update task <id> <title> [desc]  - Update a task title and/or description")
        print("  mark complete <id>       - Mark a task as complete")
        print("  mark incomplete <id>     - Mark a task as incomplete")
        print("  help                     - Show this help message")
        print("  quit/exit                - Exit the application")