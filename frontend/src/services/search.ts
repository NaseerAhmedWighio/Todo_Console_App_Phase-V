import apiClient from './api';

export interface SearchResponse {
  success: boolean;
  data: {
    results: any[];
    total: number;
    query?: string;
    limit: number;
    offset: number;
  };
}

export interface FilterParams {
  priority?: string;
  status?: string;
  tag_id?: string;
  due_date_from?: string;
  due_date_to?: string;
  sort_by?: string;
  sort_order?: string;
  limit?: number;
  offset?: number;
}

export const searchService = {
  async searchTasks(
    query: string,
    params?: FilterParams
  ): Promise<any> {
    const queryParams = new URLSearchParams({ q: query });

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, String(value));
        }
      });
    }

    const response = await apiClient.get(`/api/v1/search?${queryParams.toString()}`);
    return response.data;
  },

  async filterTasks(params?: FilterParams): Promise<any> {
    const queryParams = new URLSearchParams();

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          queryParams.append(key, String(value));
        }
      });
    }

    const response = await apiClient.get(`/api/v1/search/filter?${queryParams.toString()}`);
    return response.data;
  },
};
