import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '@/components/Auth/AuthProvider';
import { connectWebSocket, subscribeToTaskUpdates, disconnectWebSocket } from '@/services/chat';
import Image from 'next/image'
import Robot from "../../public/robot.png"
import './PopupChatInterface.css';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

interface ChatPopupProps {
  isOpen: boolean;
  onClose: () => void;
}

const PopupChatInterface: React.FC<ChatPopupProps> = ({ isOpen, onClose }) => {
  const [inputMessage, setInputMessage] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [showQuickActions, setShowQuickActions] = useState<boolean>(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const { user } = useAuth();

  // Quick action suggestions
  const quickActions = [
    { label: '📝 Create Task', prompt: 'Create a new task to buy groceries tomorrow with high priority' },
    { label: '📋 List Tasks', prompt: 'Show me all my pending tasks' },
    { label: '🏷️ Create Tag', prompt: 'Create a new tag called Work with color #3B82F6' },
    { label: '🔔 Set Reminder', prompt: 'Set a reminder for my task 30 minutes before due date' },
    { label: '🔍 Search Tasks', prompt: 'Search for tasks with high priority' },
    { label: '✅ Complete Task', prompt: 'Help me mark a task as completed' },
  ];

  // Setup WebSocket connection when user is available
  useEffect(() => {
    if (user && isOpen) {
      const ws = connectWebSocket(user.id);

      const unsubscribe = subscribeToTaskUpdates((data) => {
        console.log('Received task update:', data);

        // Add notification message to chat
        const updateMessage: Message = {
          id: `update-${Date.now()}`,
          role: 'assistant',
          content: `✓ Task updated: ${data.operation} operation completed.`,
          timestamp: new Date(),
        };

        setMessages(prev => [...prev, updateMessage]);
      });

      return () => {
        unsubscribe();
      };
    }
  }, [user, isOpen]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [isOpen]);

  // Hide quick actions when there are messages
  useEffect(() => {
    setShowQuickActions(messages.length === 0);
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await sendMessage();
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    if (!user) {
      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Please log in to use the AI task assistant.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    if (isLoading) return;

    // Add user message to UI immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setShowQuickActions(false);

    try {
      const { sendMessage: sendChatMessage } = await import('../services/chat');
      const response = await sendChatMessage(user.id, inputMessage, conversationId);

      // Update conversation ID if it's a new conversation
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant message to UI
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.message,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (prompt: string) => {
    setInputMessage(prompt);
    setTimeout(() => {
      sendMessage();
    }, 100);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleInputResize = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const textarea = e.target;
    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 80);
    textarea.style.height = newHeight + 'px';
    // Ensure the last line is visible by scrolling to bottom
    textarea.scrollTop = textarea.scrollHeight;
  };

  if (!isOpen) {
    return null;
  }

  return (
    <div className="chat-overlay">
      <div className="chat-container">
        <div className="chat-header">
          <div className="chat-header-content">
            {/* <div className="chat-header-icon">🤖</div> */}
            <Image src={Robot} alt="AI Chat Assistant" width={50} height={50}  />
            <div>
              <h3 className="chat-header-text">AI Task Assistant</h3>
              <p className="chat-header-subtitle">Manage tasks with natural language</p>
            </div>
          </div>
          <button className="chat-close-button" onClick={onClose} title="Close chat">
            ×
          </button>
        </div>

        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="chat-welcome-message">
              <p>👋 Hello! I'm your AI task assistant.</p>
              <p>I can help you manage tasks, tags, reminders, and more!</p>
              <div className="chat-welcome-list">
                <div className="chat-welcome-list-item">📝 <strong>Create tasks</strong> with titles, priorities, and due dates</div>
                <div className="chat-welcome-list-item">🏷️ <strong>Organize with tags</strong> to categorize your tasks</div>
                <div className="chat-welcome-list-item">🔔 <strong>Set reminders</strong> so you never miss a deadline</div>
                <div className="chat-welcome-list-item">🔍 <strong>Search & filter</strong> to find tasks quickly</div>
                <div className="chat-welcome-list-item">✅ <strong>Track progress</strong> by marking tasks complete</div>
              </div>
              <p style={{ marginTop: '16px', fontSize: '13px', opacity: 0.8 }}>
                Try clicking a quick action below or type your own message!
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`chat-message ${
                  message.role === 'user' ? 'chat-user-message' :
                  message.role === 'assistant' ? 'chat-assistant-message' :
                  'chat-system-message'
                }`}
              >
                <div className="chat-message-content">
                  {message.content}
                </div>
                <div className="chat-timestamp">
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="chat-message chat-assistant-message">
              <div className="chat-message-content">
                <div className="chat-typing-indicator">
                  <span className="chat-typing-dot"></span>
                  <span className="chat-typing-dot"></span>
                  <span className="chat-typing-dot"></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {showQuickActions && (
          <div className="chat-quick-actions">
            {quickActions.map((action, index) => (
              <button
                key={index}
                className="chat-action-button"
                onClick={() => handleQuickAction(action.prompt)}
                title={action.prompt}
              >
                {action.label}
              </button>
            ))}
          </div>
        )}

        <form onSubmit={handleSubmit} className="chat-input-form">
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => {
              setInputMessage(e.target.value);
              handleInputResize(e);
            }}
            onInput={(e) => {
              // Ensure last line is visible when typing
              const textarea = e.currentTarget;
              textarea.scrollTop = textarea.scrollHeight;
            }}
            onKeyDown={handleKeyPress}
            placeholder="Type your message..."
            rows={1}
            disabled={isLoading || !user}
            className="chat-input"
          />
          <button
            type="submit"
            disabled={!inputMessage.trim() || isLoading || !user}
            className="chat-send-button"
          >
            {isLoading ? '⏳' : '➤'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default PopupChatInterface;
