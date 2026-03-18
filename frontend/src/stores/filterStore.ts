import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type SortBy = 'created_at' | 'updated_at' | 'due_date' | 'priority' | 'title';
export type SortOrder = 'asc' | 'desc';

interface FilterState {
  // Filters
  status: boolean | null;
  priority: string | null;
  tagId: string | null;
  dueDateFrom: string | null;
  dueDateTo: string | null;
  
  // Sorting
  sortBy: SortBy;
  sortOrder: SortOrder;
  
  // Search
  searchQuery: string;
  
  // Pagination
  limit: number;
  offset: number;
  
  // Actions
  setStatus: (status: boolean | null) => void;
  setPriority: (priority: string | null) => void;
  setTagId: (tagId: string | null) => void;
  setDueDateRange: (from: string | null, to: string | null) => void;
  setSortBy: (sortBy: SortBy) => void;
  setSortOrder: (sortOrder: SortOrder) => void;
  setSearchQuery: (query: string) => void;
  setPagination: (limit: number, offset: number) => void;
  resetFilters: () => void;
  setFromParams: (params: URLSearchParams) => void;
}

const initialState = {
  status: null as boolean | null,
  priority: null as string | null,
  tagId: null as string | null,
  dueDateFrom: null as string | null,
  dueDateTo: null as string | null,
  sortBy: 'created_at' as SortBy,
  sortOrder: 'desc' as SortOrder,
  searchQuery: '',
  limit: 50,
  offset: 0,
};

export const useFilterStore = create<FilterState>()(
  persist(
    (set, get) => ({
      ...initialState,

      setStatus: (status) => set({ status }),
      
      setPriority: (priority) => set({ priority }),
      
      setTagId: (tagId) => set({ tagId }),
      
      setDueDateRange: (from, to) => set({ dueDateFrom: from, dueDateTo: to }),
      
      setSortBy: (sortBy) => set({ sortBy }),
      
      setSortOrder: (sortOrder) => set({ sortOrder }),
      
      setSearchQuery: (searchQuery) => set({ searchQuery }),
      
      setPagination: (limit, offset) => set({ limit, offset }),
      
      resetFilters: () => set({
        ...initialState,
        sortBy: 'created_at',
        sortOrder: 'desc',
        limit: get().limit,
        offset: 0,
      }),

      setFromParams: (params) => {
        const updates: Partial<FilterState> = {};
        
        const status = params.get('status');
        if (status !== null) {
          updates.status = status === 'true';
        }
        
        const priority = params.get('priority');
        if (priority !== null) {
          updates.priority = priority;
        }
        
        const tagId = params.get('tag_id');
        if (tagId !== null) {
          updates.tagId = tagId;
        }
        
        const dueDateFrom = params.get('due_date_from');
        if (dueDateFrom !== null) {
          updates.dueDateFrom = dueDateFrom;
        }
        
        const dueDateTo = params.get('due_date_to');
        if (dueDateTo !== null) {
          updates.dueDateTo = dueDateTo;
        }
        
        const sortBy = params.get('sort_by');
        if (sortBy && ['created_at', 'updated_at', 'due_date', 'priority', 'title'].includes(sortBy)) {
          updates.sortBy = sortBy as SortBy;
        }
        
        const sortOrder = params.get('sort_order');
        if (sortOrder && ['asc', 'desc'].includes(sortOrder)) {
          updates.sortOrder = sortOrder as SortOrder;
        }
        
        const searchQuery = params.get('q');
        if (searchQuery !== null) {
          updates.searchQuery = searchQuery;
        }
        
        const limit = params.get('limit');
        if (limit !== null) {
          updates.limit = parseInt(limit, 10) || 50;
        }
        
        const offset = params.get('offset');
        if (offset !== null) {
          updates.offset = parseInt(offset, 10) || 0;
        }
        
        set(updates);
      },
    }),
    {
      name: 'task-filters-storage',
      partialize: (state) => ({
        status: state.status,
        priority: state.priority,
        tagId: state.tagId,
        sortBy: state.sortBy,
        sortOrder: state.sortOrder,
        limit: state.limit,
      }),
    }
  )
);

// Helper to convert store state to URLSearchParams
export const filterStateToParams = (state: FilterState): URLSearchParams => {
  const params = new URLSearchParams();
  
  if (state.status !== null) {
    params.append('status', state.status.toString());
  }
  
  if (state.priority) {
    params.append('priority', state.priority);
  }
  
  if (state.tagId) {
    params.append('tag_id', state.tagId);
  }
  
  if (state.dueDateFrom) {
    params.append('due_date_from', state.dueDateFrom);
  }
  
  if (state.dueDateTo) {
    params.append('due_date_to', state.dueDateTo);
  }
  
  params.append('sort_by', state.sortBy);
  params.append('sort_order', state.sortOrder);
  
  if (state.searchQuery) {
    params.append('q', state.searchQuery);
  }
  
  params.append('limit', state.limit.toString());
  params.append('offset', state.offset.toString());
  
  return params;
};

export default useFilterStore;
