'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '../../components/Auth/AuthProvider'
import TaskList from '../../components/TaskList/TaskList'
import TaskForm from '../../components/TaskForm/TaskForm'
import { TaskSearch } from '../../components/TaskSearch/TaskSearch'
import apiClient from '../../services/api'
import { connectWebSocket, subscribeToTaskUpdates, subscribeToTagUpdates } from '../../services/chat'
import ThemeToggle from '../../components/ThemeToggle'
import Link from 'next/link'
import { Tag } from '../../types'

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const [tasks, setTasks] = useState([])
  const [tags, setTags] = useState<Tag[]>([])
  const [loading, setLoading] = useState(true)
  const [searchResults, setSearchResults] = useState<any[] | null>(null)
  
  // Filter and sort state
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')
  const [statusFilter, setStatusFilter] = useState('all')
  const [tagFilter, setTagFilter] = useState('')

  useEffect(() => {
    if (user) {
      // Load tasks and tags when user is authenticated
      loadTasks()
      loadTags()

      // Setup WebSocket connection for real-time updates
      const ws = connectWebSocket(user.id)

      // Subscribe to task updates
      const unsubscribeTasks = subscribeToTaskUpdates((data) => {
        console.log('Received task update in dashboard:', data)
        // Reload tasks when we receive updates
        loadTasks()
      })

      // Subscribe to tag updates
      const unsubscribeTags = subscribeToTagUpdates((data) => {
        console.log('Received tag update in dashboard:', data)
        // Reload tags when we receive updates
        loadTags()
      })

      // Cleanup on unmount
      return () => {
        unsubscribeTasks()
        unsubscribeTags()
      }
    }
  }, [user])

  const loadTasks = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/api/v1/todos/')
      let loadedTasks = response.data.map((todo: any) => ({
        id: todo.id,
        title: todo.title,
        description: todo.description,
        completed: todo.is_completed,
        priority: todo.priority || 'medium',
        due_date: todo.due_date,
        tags: todo.task_tags?.map((tt: any) => ({
          id: tt.tag.id,
          name: tt.tag.name,
          color: tt.tag.color,
        })) || [],
        user_id: user?.id || '',
        created_at: todo.created_at,
        updated_at: todo.updated_at
      }))
      setTasks(loadedTasks)
      setSearchResults(null) // Clear search results when loading all tasks
    } catch (error) {
      console.error('Error loading tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadTags = async () => {
    try {
      const response = await apiClient.get('/api/v1/tags')
      setTags(response.data)
    } catch (error) {
      console.error('Error loading tags:', error)
    }
  }

  const handleSearchResults = (results: any[]) => {
    if (results.length > 0) {
      // Transform search results to match task format
      const formattedResults = results.map((todo: any) => ({
        id: todo.id,
        title: todo.title,
        description: todo.description,
        completed: todo.is_completed,
        priority: todo.priority || 'medium',
        due_date: todo.due_date,
        tags: todo.task_tags?.map((tt: any) => ({
          id: tt.tag.id,
          name: tt.tag.name,
          color: tt.tag.color,
        })) || [],
        user_id: user?.id || '',
        created_at: todo.created_at,
        updated_at: todo.updated_at
      }))
      setSearchResults(formattedResults)
    } else {
      setSearchResults([])
    }
  }

  // Apply filters and sorting to tasks
  const getFilteredAndSortedTasks = () => {
    let filtered = searchResults !== null ? searchResults : tasks

    // Apply status filter
    if (statusFilter === 'completed') {
      filtered = filtered.filter((task: any) => task.completed)
    } else if (statusFilter === 'pending') {
      filtered = filtered.filter((task: any) => !task.completed)
    }

    // Apply tag filter
    if (tagFilter) {
      filtered = filtered.filter((task: any) => 
        task.tags && task.tags.some((tag: Tag) => tag.id === tagFilter)
      )
    }

    // Apply sorting
    filtered = [...filtered].sort((a: any, b: any) => {
      let comparison = 0

      switch (sortBy) {
        case 'priority':
          const priorityOrder: any = { urgent: 0, high: 1, medium: 2, low: 3 }
          const aPriority = priorityOrder[a.priority as keyof typeof priorityOrder] || 4
          const bPriority = priorityOrder[b.priority as keyof typeof priorityOrder] || 4
          comparison = aPriority - bPriority
          break
        case 'title':
          comparison = a.title.localeCompare(b.title)
          break
        case 'created_at':
          comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
          break
        case 'due_date':
          const aDue = a.due_date ? new Date(a.due_date).getTime() : Infinity
          const bDue = b.due_date ? new Date(b.due_date).getTime() : Infinity
          comparison = aDue - bDue
          break
        default:
          comparison = 0
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })

    return filtered
  }

  const handleLogout = () => {
    logout()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-black">
        <div className="text-xl text-gray-800 dark:text-gray-200">Loading...</div>
      </div>
    )
  }

  const displayTasks = getFilteredAndSortedTasks()

  return (
    <div className="min-h-screen pt-4 bg-white dark:bg-[#0A0A0A] relative">
      {/* Additional floating aura elements for dashboard */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-400/20 dark:bg-blue-500/15 rounded-full blur-3xl animate-aura-slow"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-pink-400/20 dark:bg-orange-500/15 rounded-full blur-3xl animate-aura-medium" style={{ animationDelay: '-7s' }}></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-gradient-to-r from-cyan-400/15 to-purple-400/15 dark:from-blue-600/10 dark:to-cyan-600/10 rounded-full blur-3xl animate-aura-pulse" style={{ animationDelay: '-3s' }}></div>
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-yellow-400/15 dark:bg-yellow-500/5 rounded-full blur-3xl animate-aura-slow" style={{ animationDelay: '-5s' }}></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-indigo-400/15 dark:bg-indigo-500/5 rounded-full blur-3xl animate-aura-medium" style={{ animationDelay: '-10s' }}></div>
      </div>

      <header className="blur-header shadow-xl bg-white/80 dark:bg-[#151515]/80 border border-[#EBBDC0] dark:border-gray-700/40 rounded-lg mx-4 relative z-10">
        <div className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 flex justify-between items-center">
        <Link href="/" >
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white cursor-pointer gradient-text">Todo Dashboard</h1>
          </Link>
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            <span className="text-gray-800 dark:text-gray-300">Welcome, {user?.name || user?.email}</span>
            <button
              onClick={handleLogout}
              className="primary-gradient text-white px-4 py-2 rounded-md text-sm font-medium transition-all duration-300 glow-effect hover:opacity-90"
            >
              Logout
            </button>
          </div>
        </div>
      </header>
      <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-1 space-y-6">
            <TaskForm onTaskCreated={() => loadTasks()} />
          </div>
          <div className="md:col-span-2">
            {/* Search Bar with Filters and Sort */}
            <div className="mb-4">
              <TaskSearch
                onSearchResults={handleSearchResults}
                sortBy={sortBy}
                sortOrder={sortOrder}
                onSortChange={(newSortBy, newSortOrder) => {
                  setSortBy(newSortBy)
                  setSortOrder(newSortOrder)
                }}
                statusFilter={statusFilter}
                onStatusFilterChange={setStatusFilter}
                tagFilter={tagFilter}
                onTagFilterChange={setTagFilter}
                tags={tags}
              />
              {(searchResults !== null || statusFilter !== 'all' || tagFilter) && (
                <div className="mt-2 text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                  {searchResults !== null && (
                    <span>
                      {searchResults.length === 0
                        ? 'No tasks found matching your search.'
                        : `Found ${searchResults.length} task(s) from search.`}
                    </span>
                  )}
                  {statusFilter !== 'all' && (
                    <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 rounded text-xs text-blue-700 dark:text-blue-300">
                      Status: {statusFilter}
                    </span>
                  )}
                  {tagFilter && (
                    <span className="px-2 py-1 bg-green-100 dark:bg-green-900/30 rounded text-xs text-green-700 dark:text-green-300">
                      Tag: {tags.find(t => t.id === tagFilter)?.name}
                    </span>
                  )}
                  <button
                    onClick={() => {
                      setSearchResults(null)
                      setStatusFilter('all')
                      setTagFilter('')
                    }}
                    className="ml-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors"
                  >
                    Clear all filters
                  </button>
                </div>
              )}
            </div>
            <TaskList tasks={displayTasks} onTasksUpdate={() => loadTasks()} />
          </div>
        </div>
      </main>
    </div>
  )
}
