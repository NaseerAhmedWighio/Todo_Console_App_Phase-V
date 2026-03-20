'use client'

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import apiClient from '../../services/api'

// Define the user type
interface User {
  id: string;
  email: string;
  name?: string;
  created_at: string;
  updated_at: string;
  is_email_verified?: boolean;
  email_verified_at?: string;
}

// Define the context type
interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  verifyEmail: (token: string) => Promise<void>;
  resendVerification: (email: string) => Promise<void>;
  logout: () => void;
  getToken: () => Promise<string | null>;
}

// Create the context
const AuthContext = createContext<AuthContextType | undefined>(undefined)

// AuthProvider component
export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  // Check for existing token on initial load
  useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      // In a real app, we would validate the token by making a request to get user info
      // For now, we'll just assume the user is still logged in
      const storedUser = localStorage.getItem('user')
      if (storedUser) {
        setUser(JSON.parse(storedUser))
      }
    }
    setLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await apiClient.post('/api/v1/auth/login', {
        email,
        password,
      });

      const data = response.data;
      if (data.success) {
        const token = data.data.token;
        const userData = data.data.user;
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
        router.refresh();
      } else {
        throw new Error(data.message || 'Login failed');
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Login failed');
    }
  }

  const register = async (name: string, email: string, password: string) => {
    try {
      const response = await apiClient.post('/api/v1/auth/register', {
        name,
        email,
        password,
      });

      const data = response.data;
      if (data.success) {
        const token = data.data.token;
        const userData = data.data.user;
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
        router.refresh();
      } else {
        throw new Error(data.message || 'Registration failed');
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Registration failed');
    }
  }

  const verifyEmail = async (token: string) => {
    try {
      const response = await apiClient.post('/api/v1/auth/verify-email', null, {
        params: { token },
      });

      const data = response.data;
      if (data.success) {
        const newToken = data.data.token;
        const userData = data.data.user;
        localStorage.setItem('token', newToken);
        localStorage.setItem('user', JSON.stringify(userData));
        setUser(userData);
      } else {
        throw new Error(data.message || 'Verification failed');
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Verification failed');
    }
  }

  const resendVerification = async (email: string) => {
    try {
      const response = await apiClient.post('/api/v1/auth/resend-verification', null, {
        params: { email },
      });

      const data = response.data;
      if (!data.success) {
        throw new Error(data.message || 'Failed to resend verification');
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Failed to resend verification');
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
    router.push('/login')
    router.refresh()
  }

  const getToken = async (): Promise<string | null> => {
    return localStorage.getItem('token');
  }

  const value = {
    user,
    loading,
    login,
    register,
    verifyEmail,
    resendVerification,
    logout,
    getToken,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Custom hook to use the auth context
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}