import apiClient from './api';

export interface Tag {
  id: string;
  user_id: string;
  name: string;
  color: string;
  created_at: string;
  usage_count?: number;
}

export interface TagCreate {
  name: string;
  color?: string;
}

export interface TagUpdate {
  name?: string;
  color?: string;
}

export const tagsService = {
  async listTags(): Promise<Tag[]> {
    try {
      const response = await apiClient.get('/api/v1/tags');
      console.log('Tags loaded:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error loading tags:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url
      });
      throw error;
    }
  },

  async createTag(tagData: TagCreate): Promise<Tag> {
    try {
      console.log('Creating tag:', tagData);
      const response = await apiClient.post('/api/v1/tags', tagData);
      console.log('Tag created:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Error creating tag:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url
      });
      throw error;
    }
  },

  async updateTag(tagId: string, tagData: TagUpdate): Promise<Tag> {
    const response = await apiClient.put(`/api/v1/tags/${tagId}`);
    return response.data;
  },

  async deleteTag(tagId: string): Promise<void> {
    await apiClient.delete(`/api/v1/tags/${tagId}`);
  },

  async assignTag(tagId: string, taskId: string): Promise<void> {
    await apiClient.post(`/api/v1/tags/${tagId}/assign?task_id=${taskId}`);
  },

  async unassignTag(tagId: string, taskId: string): Promise<void> {
    await apiClient.delete(`/api/v1/tags/${tagId}/unassign?task_id=${taskId}`);
  },

  async getTasksByTag(tagId: string): Promise<any[]> {
    const response = await apiClient.get(`/api/v1/tags/${tagId}/tasks`);
    return response.data;
  },
};
