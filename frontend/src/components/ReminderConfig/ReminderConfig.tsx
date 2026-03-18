"use client";

import React, { useState } from "react";

export interface ReminderConfigData {
  timing_minutes: number;
  timing_days?: number;
  delivery_channel: string; // in_app, email, web_push, sms
}

interface ReminderConfigProps {
  value: ReminderConfigData | null;
  onChange: (config: ReminderConfigData) => void;
  disabled?: boolean;
}

const timingPresets = [
  { label: "At time of", minutes: 0 },
  { label: "15 min before", minutes: 15 },
  { label: "30 min before", minutes: 30 },
  { label: "1 hour before", minutes: 60 },
  { label: "2 hours before", minutes: 120 },
  { label: "1 day before", days: 1 },
  { label: "2 days before", days: 2 },
];

const deliveryChannelOptions = [
  { value: "in_app", label: "In-App Notification", icon: "🔔" },
  { value: "email", label: "Email", icon: "📧" },
  { value: "web_push", label: "Web Push", icon: "📱" },
  { value: "sms", label: "SMS", icon: "💬" },
];

export const ReminderConfig: React.FC<ReminderConfigProps> = ({
  value,
  onChange,
  disabled = false,
}) => {
  const [config, setConfig] = useState<ReminderConfigData>(
    value || {
      timing_minutes: 15,
      delivery_channel: "in_app",
    }
  );

  const updateConfig = (updates: Partial<ReminderConfigData>) => {
    const newConfig = { ...config, ...updates };
    setConfig(newConfig);
    onChange(newConfig);
  };

  const handlePresetClick = (preset: typeof timingPresets[0]) => {
    if ("days" in preset) {
      updateConfig({ timing_days: preset.days, timing_minutes: 0 });
    } else {
      updateConfig({ timing_minutes: preset.minutes, timing_days: undefined });
    }
  };

  const isDaysSelected = config.timing_days !== undefined && config.timing_days > 0;

  return (
    <div className="reminder-config space-y-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Remind me:
        </label>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          {timingPresets.map((preset) => {
            const isSelected =
              ("days" in preset && isDaysSelected && config.timing_days === preset.days) ||
              ("minutes" in preset && !isDaysSelected && config.timing_minutes === preset.minutes);

            return (
              <button
                key={preset.label}
                type="button"
                onClick={() => handlePresetClick(preset)}
                disabled={disabled}
                className={`px-3 py-2 text-sm rounded-md font-medium transition-all duration-200 ${
                  isSelected
                    ? "bg-blue-600 text-white"
                    : "bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600"
                } disabled:opacity-50`}
              >
                {preset.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Custom timing */}
      <div className="flex items-center gap-3">
        <span className="text-sm text-gray-600 dark:text-gray-400">Or custom:</span>
        <div className="flex items-center gap-2">
          <input
            type="number"
            min="0"
            max="1440"
            value={isDaysSelected ? config.timing_days : config.timing_minutes}
            onChange={(e) => {
              const val = parseInt(e.target.value) || 0;
              if (isDaysSelected) {
                updateConfig({ timing_days: val });
              } else {
                updateConfig({ timing_minutes: val });
              }
            }}
            disabled={disabled}
            className="w-24 px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          />
          <select
            value={isDaysSelected ? "days" : "minutes"}
            onChange={(e) => {
              const val = parseInt(e.target.value) || 0;
              const currentVal = isDaysSelected ? config.timing_days : config.timing_minutes;
              if (e.target.value === "days") {
                updateConfig({ timing_days: currentVal || 1, timing_minutes: 0 });
              } else {
                updateConfig({ timing_minutes: currentVal || 15, timing_days: undefined });
              }
            }}
            disabled={disabled}
            className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 dark:bg-[#334155] dark:text-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
          >
            <option value="minutes">minutes</option>
            <option value="days">days</option>
          </select>
        </div>
      </div>

      {/* Delivery channel */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Delivery method:
        </label>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
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
              <span className="text-lg">{channel.icon}</span>
              <span className="text-sm text-gray-700 dark:text-gray-300">{channel.label}</span>
            </label>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ReminderConfig;
