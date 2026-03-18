"use client";

import React from "react";
import { Tag } from "../../types";

interface TaskSortProps {
  sortBy: string;
  sortOrder: "asc" | "desc";
  onSortChange: (sortBy: string, sortOrder: "asc" | "desc") => void;
  statusFilter: string;
  onStatusFilterChange: (status: string) => void;
  tagFilter: string;
  onTagFilterChange: (tagId: string) => void;
  tags: Tag[];
}

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

export const TaskSort: React.FC<TaskSortProps> = ({
  sortBy,
  sortOrder,
  onSortChange,
  statusFilter,
  onStatusFilterChange,
  tagFilter,
  onTagFilterChange,
  tags,
}) => {
  const handleSortByChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onSortChange(e.target.value, sortOrder);
  };

  const handleSortOrderChange = () => {
    onSortChange(sortBy, sortOrder === "asc" ? "desc" : "asc");
  };

  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onStatusFilterChange(e.target.value);
  };

  const handleTagChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    onTagFilterChange(e.target.value);
  };

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {/* Status Filter */}
      <select
        value={statusFilter}
        onChange={handleStatusChange}
        className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
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
        onChange={handleTagChange}
        className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
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
        onChange={handleSortByChange}
        className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
      >
        {sortOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>

      {/* Sort Order Toggle */}
      <button
        onClick={handleSortOrderChange}
        className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all duration-300"
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
  );
};

export default TaskSort;
