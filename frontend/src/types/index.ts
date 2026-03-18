// User-related types
export interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
  updated_at: string;
}

// Tag-related types
export interface Tag {
  id: string;
  user_id: string;
  name: string;
  color: string;
  created_at: string;
  usage_count?: number;
}

// Task-related types
export interface Task {
  id: string;
  title: string;
  description?: string;
  completed: boolean;
  priority?: string;  // low, medium, high, urgent
  due_date?: string;
  tags?: Tag[];
  user_id: string;
  created_at: string;
  updated_at: string;
  is_overdue?: boolean;
}

// API response types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    code?: string;
    message: string;
  };
}

// Authentication-related types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  name: string;
  email: string;
  password: string;
}

// Task form data
export interface TaskFormData {
  title: string;
  description?: string;
  priority?: string;
  due_date?: string;
  tag_ids?: string[];
}

// Recurring pattern types
export type RecurringPattern = 'minutely' | 'daily' | 'weekly' | 'monthly' | 'yearly';

export interface RecurringTask {
  id: string;
  task_id: string;
  recurrence_pattern: RecurringPattern;
  interval: number;
  by_weekday?: string;
  by_monthday?: number;
  by_month?: string;
  end_condition: 'never' | 'after_occurrences' | 'on_date';
  end_occurrences?: number;
  end_date?: string;
  is_active: boolean;
  next_due_date?: string;
  created_at: string;
}

// Context types
export interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}
