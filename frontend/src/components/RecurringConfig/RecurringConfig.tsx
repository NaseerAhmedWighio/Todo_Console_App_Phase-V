"use client";

import React, { useState } from "react";

export interface RecurringConfigData {
  recurrence_pattern: string; // daily, weekly, monthly, yearly, biweekly, quarterly, pay_bills
  interval: number;
  by_weekday?: string; // Comma-separated: MO,TU,WE,TH,FR,SA,SU
  by_monthday?: number;
  by_month?: string; // Comma-separated: 1-12
  end_condition: string; // never, after_occurrences, on_date
  end_occurrences?: number;
  end_date?: string;
}

interface RecurringConfigProps {
  value: RecurringConfigData | null;
  onChange: (config: RecurringConfigData) => void;
  disabled?: boolean;
}

const patternOptions = [
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "biweekly", label: "Bi-Weekly" },
  { value: "monthly", label: "Monthly" },
  { value: "quarterly", label: "Quarterly" },
  { value: "yearly", label: "Yearly" },
  { value: "pay_bills", label: "Pay Bills (Monthly)" },
];

const weekdayOptions = [
  { value: "MO", label: "Mon" },
  { value: "TU", label: "Tue" },
  { value: "WE", label: "Wed" },
  { value: "TH", label: "Thu" },
  { value: "FR", label: "Fri" },
  { value: "SA", label: "Sat" },
  { value: "SU", label: "Sun" },
];

const endConditionOptions = [
  { value: "never", label: "Never" },
  { value: "after_occurrences", label: "After" },
  { value: "on_date", label: "On date" },
];

export const RecurringConfig: React.FC<RecurringConfigProps> = ({
  value,
  onChange,
  disabled = false,
}) => {
  const [config, setConfig] = useState<RecurringConfigData>(
    value || {
      recurrence_pattern: "daily",
      interval: 1,
      end_condition: "never",
    }
  );

  const updateConfig = (updates: Partial<RecurringConfigData>) => {
    const newConfig = { ...config, ...updates };
    setConfig(newConfig);
    onChange(newConfig);
  };

  const handlePatternChange = (pattern: string) => {
    const updates: Partial<RecurringConfigData> = { recurrence_pattern: pattern };
    // Clear pattern-specific fields when changing pattern
    if (pattern !== "weekly" && pattern !== "biweekly") updates.by_weekday = undefined;
    if (pattern !== "monthly" && pattern !== "pay_bills" && pattern !== "quarterly") updates.by_monthday = undefined;
    if (pattern !== "yearly") updates.by_month = undefined;
    
    // Set default interval for biweekly
    if (pattern === "biweekly") updates.interval = 1;
    
    updateConfig(updates);
  };

  const toggleWeekday = (weekday: string) => {
    const current = config.by_weekday || "";
    const days = current ? current.split(",") : [];
    const newDays = days.includes(weekday)
      ? days.filter((d) => d !== weekday)
      : [...days, weekday];
    updateConfig({ by_weekday: newDays.join(",") || undefined });
  };

  return (
    <div className="recurring-config space-y-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Repeat:
        </label>
        <select
          value={config.recurrence_pattern}
          onChange={(e) => handlePatternChange(e.target.value)}
          disabled={disabled}
          className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
        >
          {patternOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Interval */}
      {config.recurrence_pattern !== "biweekly" && config.recurrence_pattern !== "pay_bills" && (
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Every:
          </label>
          <input
            type="number"
            min="1"
            max="365"
            value={config.interval}
            onChange={(e) => updateConfig({ interval: parseInt(e.target.value) || 1 })}
            disabled={disabled}
            className="w-20 px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          />
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {config.recurrence_pattern === "daily" && "day(s)"}
            {config.recurrence_pattern === "weekly" && "week(s)"}
            {config.recurrence_pattern === "monthly" && "month(s)"}
            {config.recurrence_pattern === "quarterly" && "quarter(s)"}
            {config.recurrence_pattern === "yearly" && "year(s)"}
          </span>
        </div>
      )}

      {/* Weekly: Select weekdays */}
      {(config.recurrence_pattern === "weekly" || config.recurrence_pattern === "biweekly") && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            On:
          </label>
          <div className="flex gap-2">
            {weekdayOptions.map((day) => (
              <button
                key={day.value}
                type="button"
                onClick={() => toggleWeekday(day.value)}
                disabled={disabled}
                className={`w-10 h-10 rounded-full text-sm font-medium transition-all duration-200 ${
                  config.by_weekday?.includes(day.value)
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600"
                } disabled:opacity-50`}
              >
                {day.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Monthly/Quarterly/Pay Bills: Select day of month */}
      {(config.recurrence_pattern === "monthly" || config.recurrence_pattern === "pay_bills" || config.recurrence_pattern === "quarterly") && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            On day:
          </label>
          <input
            type="number"
            min="1"
            max="31"
            value={config.by_monthday || 1}
            onChange={(e) =>
              updateConfig({ by_monthday: parseInt(e.target.value) || 1 })
            }
            disabled={disabled}
            className="w-20 px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          />
          {config.recurrence_pattern === "pay_bills" && (
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              Recommended: Day 1 for monthly bills
            </p>
          )}
        </div>
      )}

      {/* Yearly: Select month */}
      {config.recurrence_pattern === "yearly" && (
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            In month:
          </label>
          <select
            value={config.by_month || "1"}
            onChange={(e) => updateConfig({ by_month: e.target.value })}
            disabled={disabled}
            className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          >
            {Array.from({ length: 12 }, (_, i) => ({
              value: String(i + 1),
              label: new Date(0, i).toLocaleString("en-US", { month: "long" }),
            })).map((month) => (
              <option key={month.value} value={month.value}>
                {month.label}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* End condition */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Ends:
        </label>
        <div className="space-y-2">
          {endConditionOptions.map((option) => (
            <label key={option.value} className="flex items-center gap-2">
              <input
                type="radio"
                name="end_condition"
                value={option.value}
                checked={config.end_condition === option.value}
                onChange={(e) =>
                  updateConfig({ end_condition: e.target.value })
                }
                disabled={disabled}
                className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                {option.label}
              </span>
            </label>
          ))}
        </div>

        {/* End occurrences input */}
        {config.end_condition === "after_occurrences" && (
          <div className="mt-2 flex items-center gap-2">
            <input
              type="number"
              min="1"
              max="1000"
              value={config.end_occurrences || 1}
              onChange={(e) =>
                updateConfig({
                  end_occurrences: parseInt(e.target.value) || 1,
                })
              }
              disabled={disabled}
              className="w-20 px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
            />
            <span className="text-sm text-gray-600 dark:text-gray-400">
              occurrence(s)
            </span>
          </div>
        )}

        {/* End date input */}
        {config.end_condition === "on_date" && (
          <div className="mt-2">
            <input
              type="date"
              value={config.end_date ? config.end_date.slice(0, 10) : ""}
              onChange={(e) =>
                updateConfig({ end_date: e.target.value })
              }
              disabled={disabled}
              className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default RecurringConfig;
