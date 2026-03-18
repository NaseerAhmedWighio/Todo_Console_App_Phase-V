import apiClient from './api';

interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
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
};