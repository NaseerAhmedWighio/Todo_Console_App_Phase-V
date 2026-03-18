import apiClient from './api';

const getToken = async (): Promise<string | null> => {
  return typeof window !== 'undefined' ? localStorage.getItem('token') : null;
};

// WebSocket connection for real-time updates
let ws: WebSocket | null = null;
let wsCallbacks: {
  taskCallbacks: ((data: any) => void)[];
  tagCallbacks: ((data: any) => void)[];
  generalCallbacks: ((data: any) => void)[];
} = {
  taskCallbacks: [],
  tagCallbacks: [],
  generalCallbacks: []
};
let wsReconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000; // 3 seconds
let wsReconnectTimer: NodeJS.Timeout | null = null;
let wsConnectionStatus: 'disconnected' | 'connecting' | 'connected' = 'disconnected';
let wsCurrentUserId: string | null = null;

// Connection status getter
export const getWebSocketStatus = () => wsConnectionStatus;

export const connectWebSocket = (user_id: string) => {
  // Prevent multiple connections for same user
  if (ws && ws.readyState === WebSocket.OPEN && wsCurrentUserId === user_id) {
    console.log('WebSocket already connected for user', user_id);
    return ws;
  }

  // Close existing connection if switching users
  if (wsCurrentUserId && wsCurrentUserId !== user_id) {
    disconnectWebSocket();
  }

  wsCurrentUserId = user_id;
  wsConnectionStatus = 'connecting';

  const token = localStorage.getItem('token');
  // Extract the backend host and port from the API base URL
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:7860';
  const url = new URL(apiBaseUrl);
  const wsProtocol = url.protocol === 'https:' || url.protocol === 'wss:' ? 'wss' : 'ws';
  const wsUrl = `${wsProtocol}://${url.host}/ws/${user_id}`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    console.log('WebSocket connected');
    wsConnectionStatus = 'connected';
    wsReconnectAttempts = 0; // Reset reconnect attempts on successful connection
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);

      // Handle ping messages (heartbeat)
      if (data.type === 'ping') {
        // Send pong response
        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'pong', timestamp: new Date().toISOString() }));
          console.log('Sent pong response for heartbeat');
        }
        return;
      }

      // Route to appropriate callbacks based on message type
      if (data.type === 'task_update') {
        wsCallbacks.taskCallbacks.forEach(callback => callback(data));
      } else if (data.type === 'tag_update') {
        wsCallbacks.tagCallbacks.forEach(callback => callback(data));
      }

      // Also notify general callbacks
      wsCallbacks.generalCallbacks.forEach(callback => callback(data));
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };

  ws.onclose = (event) => {
    console.log('WebSocket disconnected', event.code, event.reason);
    wsConnectionStatus = 'disconnected';
    ws = null;
    
    // Attempt to reconnect if not intentionally closed
    if (wsCurrentUserId && event.code !== 1000 && wsReconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
      wsReconnectAttempts++;
      console.log(`Attempting to reconnect (${wsReconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
      
      if (wsReconnectTimer) {
        clearTimeout(wsReconnectTimer);
      }
      
      wsReconnectTimer = setTimeout(() => {
        connectWebSocket(wsCurrentUserId!);
      }, RECONNECT_DELAY * wsReconnectAttempts); // Exponential backoff
    } else if (wsReconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      console.error('Max WebSocket reconnect attempts reached');
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    wsConnectionStatus = 'disconnected';
  };

  return ws;
};

export const subscribeToTaskUpdates = (callback: (data: any) => void) => {
  wsCallbacks.taskCallbacks.push(callback);
  return () => {
    wsCallbacks.taskCallbacks = wsCallbacks.taskCallbacks.filter(cb => cb !== callback);
  };
};

export const subscribeToTagUpdates = (callback: (data: any) => void) => {
  wsCallbacks.tagCallbacks.push(callback);
  return () => {
    wsCallbacks.tagCallbacks = wsCallbacks.tagCallbacks.filter(cb => cb !== callback);
  };
};

export const subscribeToAllUpdates = (callback: (data: any) => void) => {
  wsCallbacks.generalCallbacks.push(callback);
  return () => {
    wsCallbacks.generalCallbacks = wsCallbacks.generalCallbacks.filter(cb => cb !== callback);
  };
};

export const disconnectWebSocket = () => {
  if (wsReconnectTimer) {
    clearTimeout(wsReconnectTimer);
    wsReconnectTimer = null;
  }
  
  if (ws) {
    ws.close(1000, 'Client disconnect'); // Normal closure
    ws = null;
  }
  wsCurrentUserId = null;
  wsConnectionStatus = 'disconnected';
  wsCallbacks = {
    taskCallbacks: [],
    tagCallbacks: [],
    generalCallbacks: []
  };
};

interface ChatMessage {
  message: string;
  conversation_id?: string;
}

interface ChatResponse {
  conversation_id: string;
  message: string;
  timestamp: string;
}

interface ConversationHistory {
  conversation_id: string;
  title?: string;
  messages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;
}

/**
 * Send a chat message to the backend API
 */
export const sendMessage = async (
  userId: string,
  message: string,
  conversationId?: string
): Promise<ChatResponse> => {
  const token = await getToken();

  if (!token) {
    throw new Error('No authentication token found');
  }

  console.log('Sending chat message:', { userId, tokenExists: !!token, conversationId }); // Debug log

  try {
    const response = await apiClient.post(`/api/${userId}/chat`, {
      message,
      conversation_id: conversationId,
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    console.log('Chat response received:', response.data); // Debug log
    return response.data;
  } catch (error: any) {
    console.error('Chat API error details:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      url: error.config?.url,
      method: error.config?.method
    }); // Debug log

    if (error.response?.status === 401) {
      throw new Error('Unauthorized: Please log in again');
    }
    if (error.response?.status === 403) {
      // The 403 error might be due to user ID mismatch
      if (error.response?.data?.detail?.includes('user ID mismatch')) {
        throw new Error('User ID mismatch: Your session may be out of sync. Please log out and log in again.');
      }
      throw new Error('Access forbidden: You do not have permission to access this resource');
    }
    if (error.response?.status === 404) {
      throw new Error('Chat endpoint not found. Please check your connection.');
    }
    const errorData = error.response?.data || error.message;
    throw new Error(`Failed to send message: ${error.response?.status} - ${errorData}`);
  }
};

/**
 * Get a list of conversations for the user
 */
export const getUserConversations = async (userId: string): Promise<Array<{
  id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}> | null> => {
  const token = await getToken();

  if (!token) {
    throw new Error('No authentication token found');
  }

  try {
    const response = await apiClient.get(`/api/${userId}/conversations`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw new Error('Unauthorized: Please log in again');
    }
    if (error.response?.status === 403) {
      throw new Error('Access forbidden: You do not have permission to access this resource');
    }
    if (error.response?.status === 404) {
      throw new Error('Conversations endpoint not found. Please check your connection.');
    }
    const errorData = error.response?.data || error.message;
    throw new Error(`Failed to get conversations: ${error.response?.status} - ${errorData}`);
  }
};

/**
 * Get the history of a specific conversation
 */
export const getConversationHistory = async (
  userId: string,
  conversationId: string
): Promise<ConversationHistory | null> => {
  const token = await getToken();

  if (!token) {
    throw new Error('No authentication token found');
  }

  try {
    const response = await apiClient.get(`/api/${userId}/conversations/${conversationId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    return response.data;
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw new Error('Unauthorized: Please log in again');
    }
    if (error.response?.status === 403) {
      throw new Error('Access forbidden: You do not have permission to access this resource');
    }
    if (error.response?.status === 404) {
      throw new Error('Conversation not found');
    }
    const errorData = error.response?.data || error.message;
    throw new Error(`Failed to get conversation history: ${error.response?.status} - ${errorData}`);
  }
};