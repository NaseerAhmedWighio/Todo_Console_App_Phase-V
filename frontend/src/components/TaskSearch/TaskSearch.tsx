"use client";

import React, { useState, useEffect, useRef } from "react";
import { searchService } from "../../services/search";
import { Tag } from "../../types";

interface TaskSearchProps {
  onSearchResults?: (results: any[]) => void;
  placeholder?: string;
  sortBy?: string;
  sortOrder?: "asc" | "desc";
  onSortChange?: (sortBy: string, sortOrder: "asc" | "desc") => void;
  statusFilter?: string;
  onStatusFilterChange?: (status: string) => void;
  tagFilter?: string;
  onTagFilterChange?: (tagId: string) => void;
  tags?: Tag[];
}

export const TaskSearch: React.FC<TaskSearchProps> = ({
  onSearchResults,
  placeholder = "Search tasks...",
  sortBy = "created_at",
  sortOrder = "desc",
  onSortChange = () => {},
  statusFilter = "all",
  onStatusFilterChange = () => {},
  tagFilter = "",
  onTagFilterChange = () => {},
  tags = [],
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const debounceRef = useRef<NodeJS.Timeout | null>(null);

  const sortOptions = [
    { value: "created_at", label: "Date Created" },
    { value: "priority", label: "Priority" },
    { value: "title", label: "Title (A-Z)" },
    { value: "due_date", label: "Due Date" },
  ];

  const statusOptions = [
    { value: "all", label: "All Tasks" },
    { value: "pending", label: "Pending" },
    { value: "completed", label: "Completed" },
  ];

  const performSearch = async (query: string) => {
    if (!query.trim()) {
      onSearchResults?.([]);
      return;
    }

    try {
      setIsSearching(true);
      
      // Build filter params
      const filterParams: any = {};
      if (statusFilter && statusFilter !== 'all') {
        filterParams.status = statusFilter === 'completed' ? 'true' : 'false';
      }
      if (tagFilter) {
        filterParams.tag_id = tagFilter;
      }
      
      const response = await searchService.searchTasks(query, filterParams);
      console.log('Search response:', response);
      
      // Extract results from the response
      const results = response.data?.results || response.data || [];
      onSearchResults?.(results);
    } catch (error) {
      console.error("Search error:", error);
      onSearchResults?.([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchQuery(value);

    // Debounce search (wait 300ms after user stops typing)
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      if (value.trim()) {
        performSearch(value);
      } else {
        onSearchResults?.([]);
      }
    }, 300);
  };

  const handleClearSearch = () => {
    setSearchQuery("");
    onSearchResults?.([]);
  };

  useEffect(() => {
    // Cleanup debounce on unmount
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  return (
    <div className="task-search relative">
      <div className="flex items-center gap-3">
        {/* Search Input */}
        <div className="relative flex-1 bg-white dark:bg-[#0A0A0A]">
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder={placeholder}
            className="w-full px-4 py-2 pl-10 pr-10 border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#0A0A0A] text-gray-900 dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
          />
          {/* Search icon */}
          <svg
            className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          {/* Clear button */}
          {searchQuery && (
            <button
              onClick={handleClearSearch}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-300"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clipRule="evenodd"
                />
              </svg>
            </button>
          )}
          {/* Searching indicator */}
          {isSearching && (
            <div className="absolute right-10 top-1/2 transform -translate-y-1/2">
              <svg
                className="animate-spin h-5 w-5 text-blue-500"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
          )}
        </div>

        {/* Filters and Sort - Always Visible */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => onStatusFilterChange(e.target.value)}
            className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#0A0A0A] text-gray-700 dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
            title="Filter by status"
          >
            {statusOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          {/* Tag Filter */}
          <select
            value={tagFilter}
            onChange={(e) => onTagFilterChange(e.target.value)}
            className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#0A0A0A] text-gray-700 dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
            title="Filter by tag"
          >
            <option value="">All Tags</option>
            {tags.map((tag) => (
              <option key={tag.id} value={tag.id}>
                {tag.name}
              </option>
            ))}
          </select>

          {/* Sort By */}
          <select
            value={sortBy}
            onChange={(e) => onSortChange(e.target.value, sortOrder)}
            className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#0A0A0A] text-gray-700 dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
          >
            {sortOptions.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>

          {/* Sort Order Toggle */}
          <button
            onClick={() => onSortChange(sortBy, sortOrder === "asc" ? "desc" : "asc")}
            className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 bg-white dark:bg-[#0A0A0A] text-gray-700 dark:text-white rounded-md shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
            title={`Sort ${sortOrder === "asc" ? "ascending" : "descending"}`}
          >
            {sortOrder === "asc" ? (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskSearch;
