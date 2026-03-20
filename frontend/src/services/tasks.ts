import apiClient from './api';

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
  scheduled_time?: string;
  notification_sent?: boolean;
  is_recurring?: boolean;
  recurring_task_id?: string;
  timezone?: string;
  priority?: string;
  due_date?: string;
}

interface GetTasksResponse {
  success: boolean;
  data: {
    tasks: Task[];
    total: number;
    limit: number;
    offset: number;
  };
}

interface CreateTaskResponse {
  success: boolean;
  data: Task;
  message?: string;
}

interface GetTaskResponse {
  success: boolean;
  data: Task;
}

interface UpdateTaskResponse {
  success: boolean;
  data: Task;
  message?: string;
}

interface DeleteTaskResponse {
  success: boolean;
  message?: string;
}

interface ToggleTaskCompletionResponse {
  success: boolean;
  data: Task;
  message?: string;
}

interface RecurringTaskConfig {
  id: string;
  task_id: string;
  recurrence_pattern: string;
  interval: number;
  by_weekday?: string;
  by_monthday?: number;
  by_month?: string;
  end_condition: string;
  end_occurrences?: number;
  end_date?: string;
  is_active: boolean;
  next_due_date?: string;
  last_generated_date?: string;
}

interface CreateRecurringTaskWithNotificationsResponse {
  success: boolean;
  message: string;
  task_id: string;
  recurring_task_id: string;
  pattern: string;
  first_occurrence_id?: string;
}

export const taskService = {
  async getTasks(
    completed?: boolean,
    limit: number = 50,
    offset: number = 0
  ): Promise<GetTasksResponse> {
    const params = new URLSearchParams();
    if (completed !== undefined) {
      params.append('completed', completed.toString());
    }
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const response = await apiClient.get(`/api/v1/todos?${params.toString()}`);
    return response.data;
  },

  async createTask(taskData: { title: string; description?: string }): Promise<CreateTaskResponse> {
    const response = await apiClient.post('/api/v1/todos', taskData);
    return response.data;
  },

  async getTask(taskId: string): Promise<GetTaskResponse> {
    const response = await apiClient.get(`/api/v1/todos/${taskId}`);
    return response.data;
  },

  async updateTask(taskId: string, taskData: Partial<Task>): Promise<UpdateTaskResponse> {
    const response = await apiClient.put(`/api/v1/todos/${taskId}`, taskData);
    return response.data;
  },

  async deleteTask(taskId: string): Promise<DeleteTaskResponse> {
    const response = await apiClient.delete(`/api/v1/todos/${taskId}`);
    return response.data;
  },

  async toggleTaskCompletion(taskId: string): Promise<ToggleTaskCompletionResponse> {
    const response = await apiClient.patch(`/api/v1/todos/${taskId}/toggle`);
    return response.data;
  },

  async scheduleNotification(taskId: string, scheduledTime: string): Promise<UpdateTaskResponse> {
    const response = await apiClient.post(`/api/v1/notifications/tasks/${taskId}/schedule`, null, {
      params: { scheduled_time: scheduledTime },
    });
    return response.data;
  },

  async cancelNotification(taskId: string): Promise<UpdateTaskResponse> {
    const response = await apiClient.post(`/api/v1/notifications/tasks/${taskId}/cancel`);
    return response.data;
  },

  async getScheduledNotifications(): Promise<Task[]> {
    const response = await apiClient.get('/api/v1/notifications/scheduled');
    return response.data;
  },

  async createRecurringTaskWithNotifications(
    taskTitle: string,
    params: {
      recurrence_pattern: string;
      interval?: number;
      by_weekday?: string;
      by_monthday?: number;
      by_month?: string;
      notification_time?: string;
      end_condition?: string;
      end_occurrences?: number;
      end_date?: string;
      priority?: string;
      description?: string;
    }
  ): Promise<CreateRecurringTaskWithNotificationsResponse> {
    const queryParams = new URLSearchParams();
    queryParams.append('task_title', taskTitle);
    queryParams.append('recurrence_pattern', params.recurrence_pattern);
    
    if (params.interval) queryParams.append('interval', params.interval.toString());
    if (params.by_weekday) queryParams.append('by_weekday', params.by_weekday);
    if (params.by_monthday) queryParams.append('by_monthday', params.by_monthday.toString());
    if (params.by_month) queryParams.append('by_month', params.by_month);
    if (params.notification_time) queryParams.append('notification_time', params.notification_time);
    if (params.end_condition) queryParams.append('end_condition', params.end_condition);
    if (params.end_occurrences) queryParams.append('end_occurrences', params.end_occurrences.toString());
    if (params.end_date) queryParams.append('end_date', params.end_date);
    if (params.priority) queryParams.append('priority', params.priority);
    if (params.description) queryParams.append('task_description', params.description);

    const response = await apiClient.post(
      `/api/v1/recurring/create-with-notifications?${queryParams.toString()}`
    );
    return response.data;
  },

  async getRecurringTasks(activeOnly: boolean = true): Promise<RecurringTaskConfig[]> {
    const response = await apiClient.get(`/api/v1/recurring?active_only=${activeOnly}`);
    return response.data;
  },
};