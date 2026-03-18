import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

// Create an axios instance with base configuration
const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL|| 'http://localhost:7860', // Default to localhost if not set
  timeout: 50000, // Increased timeout to accommodate OpenAI Agents API calls
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token to all requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle responses globally
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    // Handle global error responses here if needed
    if (error.response?.status === 401) {
      // Check if this is a chat-related API call
      const isChatRelatedApiCall = error.config?.url?.includes('/chat') ||
                                  error.config?.url?.includes('/conversations');

      // Always remove the token and user data when receiving a 401
      // as the token is no longer valid
      localStorage.removeItem('token');
      localStorage.removeItem('user');

      if (!isChatRelatedApiCall) {
        // Redirect to login for non-chat API calls
        window.location.href = '/login';
      }
      // For chat API calls, don't redirect but let the error be handled by the caller
    }
    return Promise.reject(error);
  }
);

export default apiClient;