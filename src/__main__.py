"""
Main entry point for the Todo App Core Functionality.
This module provides a console-based interface for managing tasks.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cli.todo_app import TodoApp


def main():
    """Main function to start the Todo application."""
    app = TodoApp()
    app.run()


if __name__ == "__main__":
    main()