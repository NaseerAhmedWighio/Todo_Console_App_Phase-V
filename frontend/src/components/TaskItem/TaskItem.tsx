import React, { useState, useEffect } from 'react';
import { Task, Tag } from '../../types';

interface TaskItemProps {
  task: Task;
  onToggle: (id: string, completed: boolean) => void;
  onDelete: (id: string) => void;
  onEdit: (id: string, title: string, description: string, priority?: string, due_date?: string) => void;
}

const TaskItem: React.FC<TaskItemProps> = ({ task, onToggle, onDelete, onEdit }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');
  const [editPriority, setEditPriority] = useState(task.priority || 'medium');
  const [editDueDate, setEditDueDate] = useState('');

  // Convert ISO date to local datetime-local format (YYYY-MM-DDTHH:MM)
  const formatDateTimeLocal = (isoString?: string) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  // Initialize editDueDate when entering edit mode
  useEffect(() => {
    setEditDueDate(formatDateTimeLocal(task.due_date));
  }, [task.due_date]);

  const handleToggle = () => {
    onToggle(task.id, !task.completed);
  };

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this task?')) {
      onDelete(task.id);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = () => {
    onEdit(task.id, editTitle, editDescription, editPriority, editDueDate);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setEditPriority(task.priority || 'medium');
    setEditDueDate(formatDateTimeLocal(task.due_date));
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      handleCancel();
    } else if (e.key === 'Enter' && e.ctrlKey) {
      handleSave();
    }
  };

  // Priority color mapping
  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      low: '#6B7280',
      medium: '#EAB308',
      high: '#F97316',
      urgent: '#EF4444',
    };
    return colors[priority] || '#6B7280';
  };

  const getPriorityLabel = (priority: string) => {
    return priority.charAt(0).toUpperCase() + priority.slice(1);
  };

  // Check if task is overdue
  const isOverdue = () => {
    if (!task.due_date || task.completed) return false;
    const dueDate = new Date(task.due_date);
    const now = new Date();
    return dueDate < now;
  };

  // Format due date for display
  const formatDueDate = (dateString?: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Format created date for display
  const formatCreatedDate = (dateString?: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isEditing) {
    return (
      <li className="p-4 hover:bg-gray-50 dark:hover:bg-gray-800 bg-blue-50 dark:bg-gray-800 rounded-lg transition-colors duration-300">
        <div className="flex flex-col space-y-3">
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            className="w-full px-3 py-1 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-300"
            placeholder="Task title"
            autoFocus
            onKeyDown={handleKeyDown}
          />
          <textarea
            value={editDescription}
            onChange={(e) => setEditDescription(e.target.value)}
            className="w-full px-3 py-1 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm transition-all duration-300"
            placeholder="Task description (optional)"
            rows={2}
            onKeyDown={handleKeyDown}
          />
          {/* Priority selector in edit mode */}
          <div className="flex gap-2">
            {['low', 'medium', 'high', 'urgent'].map((priority) => (
              <button
                key={priority}
                type="button"
                onClick={() => setEditPriority(priority)}
                className={`flex-1 px-2 py-1 rounded text-xs font-medium transition-all duration-200 ${
                  editPriority === priority
                    ? 'text-white'
                    : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300'
                }`}
                style={{
                  backgroundColor: editPriority === priority ? getPriorityColor(priority) : undefined
                }}
              >
                {getPriorityLabel(priority)}
              </button>
            ))}
          </div>
          {/* Due date input */}
          <div>
            <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">Due Date</label>
            <input
              type="datetime-local"
              value={editDueDate}
              onChange={(e) => setEditDueDate(e.target.value)}
              className="w-full px-2 py-1 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md text-sm"
            />
          </div>
          <div className="flex space-x-2 justify-end">
            <button
              onClick={handleCancel}
              className="text-gray-600 hover:text-gray-900 dark:text-gray-300 dark:hover:text-gray-100 text-sm font-medium transition-colors duration-300"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 text-sm font-medium transition-colors duration-300"
            >
              Save
            </button>
          </div>
        </div>
      </li>
    );
  }

  const overdue = isOverdue();

  return (
    <li className={`p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors duration-300 rounded-lg ${
      overdue ? 'bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500' : ''
    }`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3 flex-1 min-w-0">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={handleToggle}
            className="h-4 w-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500 dark:checked:bg-blue-500 dark:checked:border-blue-500 transition-colors duration-300 flex-shrink-0"
          />
          <div className="flex-1 min-w-0">
            <div className="flex items-center flex-wrap gap-2 mb-1">
              <p className={`text-sm font-medium ${task.completed ? 'line-through text-gray-500 dark:text-gray-400' : 'text-gray-900 dark:text-gray-100'}`}>
                {task.title}
              </p>
              {/* Priority indicator */}
              {task.priority && (
                <span
                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium text-white flex-shrink-0"
                  style={{ backgroundColor: getPriorityColor(task.priority) }}
                >
                  {getPriorityLabel(task.priority)}
                </span>
              )}
              {/* Overdue indicator */}
              {overdue && (
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-500 text-white flex-shrink-0">
                  Overdue
                </span>
              )}
            </div>
            {task.description && (
              <p className={`text-sm ${task.completed ? 'line-through text-gray-400 dark:text-gray-500' : 'text-gray-500 dark:text-gray-300'} mb-2`}>
                {task.description}
              </p>
            )}
            <div className="flex flex-wrap items-center gap-3 text-xs">
              {/* Due date display */}
              {task.due_date && (
                <span className={`flex items-center gap-1 ${overdue ? 'text-red-600 dark:text-red-400 font-medium' : 'text-gray-500 dark:text-gray-400'}`}>
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  Due: {formatDueDate(task.due_date)}
                </span>
              )}
              {/* Created date display */}
              {task.created_at && (
                <span className="text-gray-400 dark:text-gray-500 flex items-center gap-1">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Created: {formatCreatedDate(task.created_at)}
                </span>
              )}
              {/* Tags display */}
              {task.tags && task.tags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {task.tags.map((tag: Tag) => (
                    <span
                      key={tag.id}
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium"
                      style={{ backgroundColor: tag.color, color: '#fff' }}
                    >
                      {tag.name}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="flex space-x-2 ml-4 flex-shrink-0">
          <button
            onClick={handleEdit}
            className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 text-sm font-medium transition-colors duration-300"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300 text-sm font-medium transition-colors duration-300"
          >
            Delete
          </button>
        </div>
      </div>
    </li>
  );
};

export default TaskItem;
