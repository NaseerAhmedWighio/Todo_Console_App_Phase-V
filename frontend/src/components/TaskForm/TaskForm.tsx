import React, { useState, useEffect, useRef } from 'react';
import { TaskFormData, RecurringPattern } from '../../types';
import apiClient from '../../services/api';
import { tagsService, Tag } from '../../services/tags';
import PrioritySelector from '../PrioritySelector';
import RecurringSelector from './RecurringSelector';

interface TaskFormProps {
  onTaskCreated: () => void;
  onTagCreated?: () => void;
}

interface TagCreateModalProps {
  onClose: () => void;
  onTagCreated: (tag: Tag) => void;
  loading: boolean;
}

const TagCreateModal: React.FC<TagCreateModalProps> = ({ onClose, onTagCreated, loading }) => {
  const [name, setName] = useState('');
  const [color, setColor] = useState('#6B7280');

  const colorPresets = [
    '#6B7280', '#EF4444', '#F97316', '#EAB308',
    '#22C55E', '#3B82F6', '#8B5CF6', '#EC4899',
  ];

  const handleKeyDown = (e: React.KeyboardEvent) => {
    e.stopPropagation();
    if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <div
      className="relative z-50 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 p-3 shadow-lg rounded-lg"
      onClick={(e) => e.stopPropagation()}
      onKeyDown={handleKeyDown}
    >
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={name}
            onChange={(e) => {
              e.stopPropagation();
              setName(e.target.value);
            }}
            onClick={(e) => e.stopPropagation()}
            placeholder="Tag name"
            className="flex-1 px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
            autoFocus
          />
          <button
            type="button"
            onClick={async (e) => {
              e.stopPropagation();
              if (!name.trim()) return;
              try {
                const newTag = await tagsService.createTag({ name: name.trim(), color });
                onTagCreated(newTag);
                setName('');
              } catch (err) {
                console.error('Error creating tag:', err);
              }
            }}
            disabled={loading || !name.trim()}
            className="px-3 py-1 text-sm primary-gradient text-white rounded hover:opacity-90 disabled:opacity-50 transition-all"
          >
            Add
          </button>
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onClose();
            }}
            className="px-2 py-1 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
          >
            ✕
          </button>
        </div>
        <div className="flex gap-1 flex-wrap">
          {colorPresets.map((c) => (
            <button
              key={c}
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setColor(c);
              }}
              className={`w-5 h-5 rounded-full border-2 transition-transform ${
                color === c ? 'border-gray-900 dark:border-white scale-110' : 'border-transparent'
              }`}
              style={{ backgroundColor: c }}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

const TaskForm: React.FC<TaskFormProps> = ({ onTaskCreated, onTagCreated }) => {
  const [formData, setFormData] = useState<TaskFormData>({
    title: '',
    description: '',
    priority: 'medium',
    due_date: '',
    tag_ids: [],
  });
  
  // Recurring state
  const [isRecurring, setIsRecurring] = useState(false);
  const [recurringPattern, setRecurringPattern] = useState<RecurringPattern>('monthly');
  const [recurringInterval, setRecurringInterval] = useState(1);
  const [autoDetectedRecurring, setAutoDetectedRecurring] = useState<{
    detected: boolean;
    pattern: RecurringPattern;
    confidence: number;
    reason: string;
  } | null>(null);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [tags, setTags] = useState<Tag[]>([]);
  const [showTagDropdown, setShowTagDropdown] = useState(false);
  const [showCreateTag, setShowCreateTag] = useState(false);
  const [tagLoading, setTagLoading] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowTagDropdown(false);
        setShowCreateTag(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Auto-detect recurring pattern when title/description changes
  useEffect(() => {
    const detectRecurring = async () => {
      if (!formData.title || formData.title.length < 3) {
        setAutoDetectedRecurring(null);
        return;
      }

      try {
        const response = await apiClient.post('/api/v1/todos/detect-recurring', null, {
          params: {
            title: formData.title,
            description: formData.description || undefined,
            due_date: formData.due_date || undefined,
          },
        });

        const detection = response.data;
        
        if (detection.is_recurring && detection.confidence >= 0.7) {
          setAutoDetectedRecurring({
            detected: true,
            pattern: detection.pattern,
            confidence: detection.confidence,
            reason: detection.reason,
          });
          
          // Auto-apply suggestion
          setIsRecurring(true);
          setRecurringPattern(detection.pattern);
        } else {
          setAutoDetectedRecurring(null);
        }
      } catch (err) {
        console.error('Error detecting recurring:', err);
      }
    };

    // Debounce detection (wait 500ms after user stops typing)
    const timer = setTimeout(detectRecurring, 500);
    return () => clearTimeout(timer);
  }, [formData.title, formData.description, formData.due_date]);

  // Load tags on mount
  useEffect(() => {
    loadTags();
  }, []);

  const loadTags = async () => {
    try {
      const fetchedTags = await tagsService.listTags();
      setTags(fetchedTags);
    } catch (err) {
      console.error('Error loading tags:', err);
    }
  };

  const handleTagCreated = (newTag: Tag) => {
    setTags(prev => [newTag, ...prev]);
    setShowCreateTag(false);
    if (onTagCreated) {
      onTagCreated();
    }
  };

  const handleDeleteTag = async (tagId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Delete this tag? It will be removed from all tasks.')) return;
    
    try {
      setTagLoading(true);
      await tagsService.deleteTag(tagId);
      setTags(prev => prev.filter(tag => tag.id !== tagId));
      setFormData(prev => ({
        ...prev,
        tag_ids: prev.tag_ids?.filter(id => id !== tagId) || []
      }));
    } catch (err) {
      console.error('Error deleting tag:', err);
    } finally {
      setTagLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePriorityChange = (priority: string) => {
    setFormData(prev => ({
      ...prev,
      priority
    }));
  };

  const handleTagToggle = (tagId: string) => {
    setFormData(prev => {
      const currentTags = prev.tag_ids || [];
      const newTags = currentTags.includes(tagId)
        ? currentTags.filter(id => id !== tagId)
        : [...currentTags, tagId];
      return { ...prev, tag_ids: newTags };
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const payload: any = {
        title: formData.title,
        description: formData.description,
        is_completed: false,
        priority: formData.priority || 'medium',
      };

      // Add due_date if provided
      if (formData.due_date) {
        // The datetime-local input value is in local time, preserve it as-is
        const localDate = new Date(formData.due_date);
        const year = localDate.getFullYear();
        const month = String(localDate.getMonth() + 1).padStart(2, '0');
        const day = String(localDate.getDate()).padStart(2, '0');
        const hours = String(localDate.getHours()).padStart(2, '0');
        const minutes = String(localDate.getMinutes()).padStart(2, '0');
        payload.due_date = `${year}-${month}-${day}T${hours}:${minutes}:00`;
      }

      // Call the API to create a task (auto_recurring=true enables backend detection)
      const response = await apiClient.post('/api/v1/todos/', payload);
      const taskId = response.data.id;

      // If user manually enabled recurring (or it was auto-detected), create recurring config
      if (isRecurring && recurringPattern) {
        try {
          await apiClient.post(`/api/v1/recurring/tasks/${taskId}`, {
            recurrence_pattern: recurringPattern,
            interval: recurringInterval,
            end_condition: 'never',
          });
          console.log(`Recurring task configured: ${recurringPattern} every ${recurringInterval}`);
        } catch (err) {
          console.error('Error creating recurring config:', err);
          // Continue even if recurring setup fails
        }
      }

      // Assign tags if any
      if (formData.tag_ids && formData.tag_ids.length > 0) {
        for (const tagId of formData.tag_ids) {
          await apiClient.post(`/api/v1/tags/${tagId}/assign?task_id=${taskId}`);
        }
      }

      // Reset form
      setFormData({ title: '', description: '', priority: 'medium', due_date: '', tag_ids: [] });
      setIsRecurring(false);
      setAutoDetectedRecurring(null);
      onTaskCreated();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create task. Please try again.');
      console.error('Error creating task:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-[#151515] rounded-lg shadow-xl p-6 border border-[#EBBDC0] dark:border-gray-700/40">
      <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4">Add New Task</h2>
      {error && <div className="text-red-500 dark:text-red-400 mb-4">{error}</div>}
      
      {/* Auto-Detection Banner */}
      {autoDetectedRecurring && (
        <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-medium text-blue-900 dark:text-blue-300">
                🔄 Recurring task detected!
              </p>
              <p className="text-xs text-blue-700 dark:text-blue-400 mt-1">
                {autoDetectedRecurring.reason} (Confidence: {Math.round(autoDetectedRecurring.confidence * 100)}%)
              </p>
              <div className="mt-2 flex items-center gap-2">
                <span className="text-xs text-blue-700 dark:text-blue-400">
                  Pattern: <strong className="capitalize">{autoDetectedRecurring.pattern}</strong>
                </span>
                <button
                  type="button"
                  onClick={() => {
                    setIsRecurring(false);
                    setAutoDetectedRecurring(null);
                  }}
                  className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
                >
                  Disable
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Title *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            required
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#151515] text-gray-900 dark:text-gray-100 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
            placeholder="Task title"
          />
        </div>
        <div className="mb-4">
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Description
          </label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#151515] text-gray-900 dark:text-gray-100 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
            placeholder="Task description (optional)"
          />
        </div>

        {/* Due Date */}
        <div className="mb-4">
          <label htmlFor="due_date" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Due Date
          </label>
          <input
            type="datetime-local"
            id="due_date"
            name="due_date"
            value={formData.due_date}
            onChange={handleChange}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#151515] text-gray-900 dark:text-gray-100 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
          />
        </div>

        <div className="mb-4">
          <PrioritySelector
            value={formData.priority || 'medium'}
            onChange={handlePriorityChange}
          />
        </div>

        {/* Recurring Settings */}
        <RecurringSelector
          isRecurring={isRecurring}
          recurringPattern={recurringPattern}
          recurringInterval={recurringInterval}
          onIsRecurringChange={setIsRecurring}
          onPatternChange={setRecurringPattern}
          onIntervalChange={setRecurringInterval}
        />

        {/* Tag Selection */}
        <div className="mb-4" ref={dropdownRef}>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Tags
          </label>

          <div className="relative">
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setShowTagDropdown(!showTagDropdown);
              }}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#151515] text-gray-900 dark:text-gray-100 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 text-left"
            >
              {formData.tag_ids && formData.tag_ids.length > 0
                ? `${formData.tag_ids.length} tag(s) selected`
                : 'Select tags'}
            </button>

            {showTagDropdown && (
              <div
                className="relative z-50 w-full mt-1 bg-white dark:bg-[#151515] border border-gray-300 dark:border-gray-600 rounded-md shadow-lg overflow-hidden"
                onClick={(e) => e.stopPropagation()}
                style={{
                  scrollbarWidth: 'none',
                  msOverflowStyle: 'none'
                }}
              >
                <style>{`
                  div[style*="scrollbar-width: none"]::-webkit-scrollbar {
                    display: none;
                  }
                  div[style*="scrollbar-width: none"] {
                    -ms-overflow-style: none;
                    scrollbar-width: none;
                  }
                `}</style>

                {/* Create Tag Button at Top */}
                {!showCreateTag && (
                  <button
                    type="button"
                    onClick={() => setShowCreateTag(true)}
                    className="w-full flex items-center gap-2 px-3 py-2 bg-blue-50 dark:bg-blue-900/20 hover:bg-blue-100 dark:hover:bg-blue-900/30 border-b border-gray-200 dark:border-gray-700/50 transition-colors"
                  >
                    <svg className="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                    </svg>
                    <span className="text-sm font-medium text-blue-600 dark:text-blue-400">Create New Tag</span>
                  </button>
                )}

                {/* Create Tag Form */}
                {showCreateTag && (
                  <TagCreateModal
                    onClose={() => setShowCreateTag(false)}
                    onTagCreated={handleTagCreated}
                    loading={tagLoading}
                  />
                )}

                <div className="max-h-48 overflow-y-auto"
                  style={{
                    scrollbarWidth: 'none',
                    msOverflowStyle: 'none'
                  }}
                >
                  {tags.length === 0 && !showCreateTag ? (
                    <div className="px-3 py-2 text-sm text-gray-500 dark:text-gray-400">
                      No tags yet. Create your first tag!
                    </div>
                  ) : (
                    tags.map(tag => (
                      <div
                        key={tag.id}
                        className="flex items-center justify-between px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors border-b border-gray-100 dark:border-gray-700 last:border-0"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <label className="flex items-center flex-1 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={formData.tag_ids?.includes(tag.id) || false}
                            onChange={(e) => {
                              e.stopPropagation();
                              handleTagToggle(tag.id);
                            }}
                            onClick={(e) => e.stopPropagation()}
                            className="mr-2 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <span
                            className="w-3 h-3 rounded-full mr-2"
                            style={{ backgroundColor: tag.color }}
                          />
                          <span className="text-sm text-gray-700 dark:text-gray-300">{tag.name}</span>
                        </label>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteTag(tag.id, e);
                          }}
                          className="ml-2 text-gray-400 hover:text-red-500 dark:hover:text-red-400 transition-colors duration-300 p-1"
                          title="Delete tag"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Selected tags preview */}
          {formData.tag_ids && formData.tag_ids.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {tags
                .filter(tag => formData.tag_ids?.includes(tag.id))
                .map(tag => (
                  <span
                    key={tag.id}
                    className="inline-flex items-center px-2 py-1 rounded text-xs font-medium"
                    style={{ backgroundColor: tag.color, color: '#fff' }}
                  >
                    {tag.name}
                  </span>
                ))}
            </div>
          )}
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white primary-gradient hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 transition-all duration-300 glow-effect"
        >
          {loading ? 'Creating...' : 'Create Task'}
        </button>
      </form>
    </div>
  );
};

export default TaskForm;
