"use client";

import React from "react";

interface TaskFiltersProps {
  status: boolean | null;
  priority: string | null;
  onStatusChange: (status: boolean | null) => void;
  onPriorityChange: (priority: string | null) => void;
}

const priorityOptions = [
  { value: "", label: "All Priorities" },
  { value: "urgent", label: "Urgent" },
  { value: "high", label: "High" },
  { value: "medium", label: "Medium" },
  { value: "low", label: "Low" },
];

const statusOptions = [
  { value: "all", label: "All" },
  { value: "pending", label: "Pending" },
  { value: "completed", label: "Completed" },
];

export const TaskFilters: React.FC<TaskFiltersProps> = ({
  status,
  priority,
  onStatusChange,
  onPriorityChange,
}) => {
  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    if (value === "all") {
      onStatusChange(null);
    } else if (value === "pending") {
      onStatusChange(false);
    } else if (value === "completed") {
      onStatusChange(true);
    }
  };

  const handlePriorityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    onPriorityChange(value || null);
  };

  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="flex items-center gap-2">
        <label className="text-sm text-gray-600 dark:text-gray-400">Status:</label>
        <select
          value={status === null ? "all" : status ? "completed" : "pending"}
          onChange={handleStatusChange}
          className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
        >
          {statusOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-2">
        <label className="text-sm text-gray-600 dark:text-gray-400">Priority:</label>
        <select
          value={priority || ""}
          onChange={handlePriorityChange}
          className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 transition-all duration-300"
        >
          {priorityOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Clear filters button */}
      {(status !== null || priority) && (
        <button
          onClick={() => {
            onStatusChange(null);
            onPriorityChange(null);
          }}
          className="px-3 py-1.5 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium transition-colors duration-300"
        >
          Clear filters
        </button>
      )}
    </div>
  );
};

export default TaskFilters;
