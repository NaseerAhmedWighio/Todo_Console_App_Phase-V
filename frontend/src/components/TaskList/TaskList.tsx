import React, { useState, useEffect } from 'react';
import TaskItem from '../TaskItem/TaskItem';
import { Task } from '../../types';
import apiClient from '../../services/api';

interface TaskListProps {
  tasks: Task[];
  onTasksUpdate: () => void;
}

const TaskList: React.FC<TaskListProps> = ({ tasks, onTasksUpdate }) => {
  const [loading, setLoading] = useState(false);

  const handleTaskToggle = async (taskId: string, completed: boolean) => {
    try {
      setLoading(true);
      // Optimistically update the UI
      const event = new CustomEvent('task-update', {
        detail: { taskId, updates: { completed } }
      });
      window.dispatchEvent(event);
      
      // Call the API to toggle the task completion
      await apiClient.patch(`/api/v1/todos/${taskId}/toggle`);
      onTasksUpdate();
    } catch (error) {
      console.error('Error updating task:', error);
      // Reload tasks to revert optimistic update on error
      onTasksUpdate();
    } finally {
      setLoading(false);
    }
  };

  const handleTaskDelete = async (taskId: string) => {
    try {
      setLoading(true);
      // Call the API to delete the task
      await apiClient.delete(`/api/v1/todos/${taskId}`);
      onTasksUpdate();
    } catch (error) {
      console.error('Error deleting task:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskEdit = async (
    taskId: string,
    title: string,
    description: string,
    priority?: string,
    due_date?: string
  ) => {
    try {
      setLoading(true);
      // Call the API to update the task
      const updateData: any = {
        title,
        description,
        priority: priority || 'medium'
      };

      // Convert due_date to ISO format if provided
      // The datetime-local input value is in local time, so we need to parse it correctly
      if (due_date) {
        // Create a date object from the local datetime string without timezone conversion
        const localDate = new Date(due_date);
        // Format as ISO string preserving the local time
        const year = localDate.getFullYear();
        const month = String(localDate.getMonth() + 1).padStart(2, '0');
        const day = String(localDate.getDate()).padStart(2, '0');
        const hours = String(localDate.getHours()).padStart(2, '0');
        const minutes = String(localDate.getMinutes()).padStart(2, '0');
        updateData.due_date = `${year}-${month}-${day}T${hours}:${minutes}:00`;
      } else {
        updateData.due_date = null;
      }

      await apiClient.put(`/api/v1/todos/${taskId}`, updateData);
      onTasksUpdate();
    } catch (error) {
      console.error('Error updating task:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-4 text-gray-800 dark:text-gray-200">Loading tasks...</div>;
  }

  if (tasks.length === 0) {
    return (
      <div className="bg-white dark:bg-[#151515] shadow p-6 rounded-lg border-glow">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">No tasks yet</h2>
        <p className="text-gray-600 dark:text-gray-300">Add a new task to get started!</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-[#151515] shadow-xl overflow-hidden rounded-lg border border-[#EBBDC0] dark:border-gray-700/40">
      <div className="border-b border-gray-200 dark:border-gray-700/40 p-4">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Your Tasks</h2>
      </div>
      <ul className="divide-y divide-gray-200 dark:divide-gray-700/40">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onToggle={handleTaskToggle}
            onDelete={handleTaskDelete}
            onEdit={handleTaskEdit}
          />
        ))}
      </ul>
    </div>
  );
};

export default TaskList;