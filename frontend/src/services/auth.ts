import apiClient from './api';

interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
  updated_at: string;
}

interface LoginResponse {
  success: boolean;
  data: {
    user: User;
    token: string;
  };
  message?: string;
}

interface RegisterResponse {
  success: boolean;
  data: {
    user: User;
    token: string;
  };
  message?: string;
}

interface GetUserResponse {
  success: boolean;
  data: User;
}

export const authService = {
  async login(email: string, password: string): Promise<LoginResponse> {
    const response = await apiClient.post('/api/v1/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  async register(name: string, email: string, password: string): Promise<RegisterResponse> {
    const response = await apiClient.post('/api/v1/auth/register', {
      name,
      email,
      password,
    });
    return response.data;
  },

  async logout(): Promise<void> {
    // In a real application, you might want to call a logout endpoint
    // For now, we just clear the local storage
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },

  async getCurrentUser(): Promise<GetUserResponse> {
    const response = await apiClient.get('/api/v1/auth/me');
    return response.data;
  },
};