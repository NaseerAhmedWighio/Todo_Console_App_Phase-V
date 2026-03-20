"use client";

import React, { useState } from "react";

export interface NotificationScheduleData {
  scheduled_time?: string; // ISO 8601 datetime
  delivery_channel: string; // email, in_app, web_push
  is_recurring: boolean;
  recurrence_pattern?: string;
  interval?: number;
  by_monthday?: number;
}

interface NotificationSchedulerProps {
  value: NotificationScheduleData | null;
  onChange: (config: NotificationScheduleData) => void;
  disabled?: boolean;
}

const deliveryChannelOptions = [
  { value: "email", label: "Email Notification", icon: "📧", description: "Get notified via email" },
  { value: "in_app", label: "In-App Notification", icon: "🔔", description: "Browser notification" },
  { value: "web_push", label: "Web Push", icon: "📱", description: "Push notification" },
];

export const NotificationScheduler: React.FC<NotificationSchedulerProps> = ({
  value,
  onChange,
  disabled = false,
}) => {
  const [config, setConfig] = useState<NotificationScheduleData>(
    value || {
      delivery_channel: "email",
      is_recurring: false,
    }
  );

  const updateConfig = (updates: Partial<NotificationScheduleData>) => {
    const newConfig = { ...config, ...updates };
    setConfig(newConfig);
    onChange(newConfig);
  };

  const handleDateTimeChange = (dateTime: string) => {
    updateConfig({ scheduled_time: dateTime, is_recurring: false });
  };

  const handleRecurringToggle = (isRecurring: boolean) => {
    updateConfig({ 
      is_recurring: isRecurring,
      scheduled_time: isRecurring ? undefined : config.scheduled_time,
    });
  };

  return (
    <div className="notification-scheduler space-y-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Notification Type:
        </label>
        <div className="flex gap-4 mb-4">
          <button
            type="button"
            onClick={() => handleRecurringToggle(false)}
            disabled={disabled}
            className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all duration-200 ${
              !config.is_recurring
                ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                : "border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 hover:border-gray-400"
            } disabled:opacity-50`}
          >
            <span className="text-lg block mb-1">📅</span>
            <span className="text-sm font-medium">One-Time</span>
          </button>
          <button
            type="button"
            onClick={() => handleRecurringToggle(true)}
            disabled={disabled}
            className={`flex-1 px-4 py-3 rounded-lg border-2 transition-all duration-200 ${
              config.is_recurring
                ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                : "border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 hover:border-gray-400"
            } disabled:opacity-50`}
          >
            <span className="text-lg block mb-1">🔄</span>
            <span className="text-sm font-medium">Recurring</span>
          </button>
        </div>
      </div>

      {!config.is_recurring ? (
        // One-time notification
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Schedule notification for:
          </label>
          <input
            type="datetime-local"
            value={config.scheduled_time || ""}
            onChange={(e) => handleDateTimeChange(e.target.value)}
            disabled={disabled}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          />
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            You will receive an email notification at the scheduled time
          </p>
        </div>
      ) : (
        // Recurring notification
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Repeat:
            </label>
            <select
              value={config.recurrence_pattern || "monthly"}
              onChange={(e) => updateConfig({ recurrence_pattern: e.target.value })}
              disabled={disabled}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
            >
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="biweekly">Bi-Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="yearly">Yearly</option>
              <option value="pay_bills">Pay Bills (Monthly)</option>
            </select>
          </div>

          {(config.recurrence_pattern === "monthly" || 
            config.recurrence_pattern === "pay_bills" || 
            config.recurrence_pattern === "quarterly") && (
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                On day:
              </label>
              <input
                type="number"
                min="1"
                max="31"
                value={config.by_monthday || 1}
                onChange={(e) => updateConfig({ by_monthday: parseInt(e.target.value) || 1 })}
                disabled={disabled}
                className="w-24 px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
              />
              {config.recurrence_pattern === "pay_bills" && (
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                  Recommended: Day 1 for monthly bills
                </p>
              )}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Interval:
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="1"
                max="365"
                value={config.interval || 1}
                onChange={(e) => updateConfig({ interval: parseInt(e.target.value) || 1 })}
                disabled={disabled}
                className="w-24 px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
              />
              <span className="text-sm text-gray-600 dark:text-gray-400">
                {config.recurrence_pattern === "daily" && "day(s)"}
                {config.recurrence_pattern === "weekly" && "week(s)"}
                {config.recurrence_pattern === "biweekly" && "period(s)"}
                {config.recurrence_pattern === "monthly" && "month(s)"}
                {config.recurrence_pattern === "quarterly" && "quarter(s)"}
                {config.recurrence_pattern === "yearly" && "year(s)"}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Delivery channel */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Delivery method:
        </label>
        <div className="space-y-2">
          {deliveryChannelOptions.map((channel) => (
            <label
              key={channel.value}
              className={`flex items-center gap-3 p-3 rounded-md border cursor-pointer transition-all duration-200 ${
                config.delivery_channel === channel.value
                  ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                  : "border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              <input
                type="radio"
                name="delivery_channel"
                value={channel.value}
                checked={config.delivery_channel === channel.value}
                onChange={(e) => updateConfig({ delivery_channel: e.target.value })}
                disabled={disabled}
                className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
              />
              <span className="text-2xl">{channel.icon}</span>
              <div>
                <div className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {channel.label}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {channel.description}
                </div>
              </div>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};

export default NotificationScheduler;
