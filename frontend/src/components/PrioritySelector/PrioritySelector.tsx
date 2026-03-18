"use client";

import React from "react";

interface PrioritySelectorProps {
  value: string;
  onChange: (priority: string) => void;
  disabled?: boolean;
}

const priorityOptions = [
  { value: "low", label: "Low", color: "#6B7280", bgColor: "bg-gray-500" },
  { value: "medium", label: "Medium", color: "#EAB308", bgColor: "bg-yellow-500" },
  { value: "high", label: "High", color: "#F97316", bgColor: "bg-orange-500" },
  { value: "urgent", label: "Urgent", color: "#EF4444", bgColor: "bg-red-500" },
];

export const PrioritySelector: React.FC<PrioritySelectorProps> = ({
  value,
  onChange,
  disabled = false,
}) => {
  const getPriorityColor = (priority: string) => {
    const option = priorityOptions.find((opt) => opt.value === priority);
    return option?.color || "#6B7280";
  };

  const getPriorityBgColor = (priority: string) => {
    const option = priorityOptions.find((opt) => opt.value === priority);
    return option?.bgColor || "bg-gray-500";
  };

  return (
    <div className="priority-selector">
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Priority
      </label>
      <div className="flex gap-2">
        {priorityOptions.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            disabled={disabled}
            className={`
              flex-1 px-3 py-2 rounded-lg text-sm font-medium
              transition-all duration-200
              ${
                value === option.value
                  ? `${option.bgColor} text-white shadow-md`
                  : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700"
              }
              ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}
            `}
            style={{
              borderColor: value === option.value ? option.color : "transparent",
            }}
          >
            {option.label}
          </button>
        ))}
      </div>
      {/* Visual indicator */}
      <div className="mt-2 flex items-center gap-2">
        <div
          className={`w-3 h-3 rounded-full ${getPriorityBgColor(value)}`}
          style={{ backgroundColor: getPriorityColor(value) }}
        />
        <span className="text-xs text-gray-500 dark:text-gray-400">
          Selected: {value.charAt(0).toUpperCase() + value.slice(1)}
        </span>
      </div>
    </div>
  );
};

export default PrioritySelector;
