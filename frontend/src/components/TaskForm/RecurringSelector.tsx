import React from 'react';
import { RecurringPattern } from '../../types';

interface RecurringSelectorProps {
  isRecurring: boolean;
  recurringPattern: RecurringPattern;
  recurringInterval: number;
  onIsRecurringChange: (value: boolean) => void;
  onPatternChange: (pattern: RecurringPattern) => void;
  onIntervalChange: (interval: number) => void;
}

const PATTERNS: RecurringPattern[] = ['minutely', 'daily', 'weekly', 'monthly', 'yearly'];

const RecurringSelector: React.FC<RecurringSelectorProps> = ({
  isRecurring,
  recurringPattern,
  recurringInterval,
  onIsRecurringChange,
  onPatternChange,
  onIntervalChange,
}) => {
  return (
    <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border border-gray-200 dark:border-gray-700">
      <div className="flex items-center gap-2 mb-3">
        <input
          type="checkbox"
          id="isRecurring"
          checked={isRecurring}
          onChange={(e) => onIsRecurringChange(e.target.checked)}
          className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
        />
        <label htmlFor="isRecurring" className="text-sm font-medium text-gray-700 dark:text-gray-300">
          🔄 This is a recurring task
        </label>
      </div>

      {isRecurring && (
        <div className="space-y-3">
          {/* Pattern Selection */}
          <div>
            <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
              Repeat Pattern
            </label>
            <div className="grid grid-cols-5 gap-2">
              {PATTERNS.map((pattern) => (
                <button
                  key={pattern}
                  type="button"
                  onClick={() => onPatternChange(pattern)}
                  className={`px-2 py-2 text-xs font-medium rounded-md border transition-all ${
                    recurringPattern === pattern
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  {pattern === 'minutely' && '⏱️ Minutely'}
                  {pattern === 'daily' && '📅 Daily'}
                  {pattern === 'weekly' && '📆 Weekly'}
                  {pattern === 'monthly' && '🗓️ Monthly'}
                  {pattern === 'yearly' && '🎂 Yearly'}
                </button>
              ))}
            </div>
          </div>

          {/* Interval Selection */}
          <div>
            <label className="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
              Repeat Every
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="1"
                max="365"
                value={recurringInterval}
                onChange={(e) => onIntervalChange(parseInt(e.target.value) || 1)}
                className="w-20 px-2 py-1 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded text-sm"
              />
              <span className="text-xs text-gray-600 dark:text-gray-400">
                {recurringInterval} {recurringPattern === 'minutely' && 'minute(s)'}
                {recurringInterval === 1 && recurringPattern === 'daily' && 'day'}
                {recurringInterval > 1 && recurringPattern === 'daily' && 'days'}
                {recurringInterval === 1 && recurringPattern === 'weekly' && 'week'}
                {recurringInterval > 1 && recurringPattern === 'weekly' && 'weeks'}
                {recurringInterval === 1 && recurringPattern === 'monthly' && 'month'}
                {recurringInterval > 1 && recurringPattern === 'monthly' && 'months'}
                {recurringInterval === 1 && recurringPattern === 'yearly' && 'year'}
                {recurringInterval > 1 && recurringPattern === 'yearly' && 'years'}
              </span>
            </div>
          </div>

          {/* Preview */}
          <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded text-xs text-blue-700 dark:text-blue-400">
            <strong>Preview:</strong> Task will repeat every {recurringInterval} {recurringPattern}
            {recurringPattern === 'minutely' && recurringInterval === 1 && ' (every minute)'}
            {recurringPattern === 'minutely' && recurringInterval > 1 && ` (every ${recurringInterval} minutes)`}
            {recurringPattern === 'daily' && recurringInterval === 1 && ' (every day)'}
            {recurringPattern === 'weekly' && recurringInterval === 1 && ' (every week on the same day)'}
            {recurringPattern === 'monthly' && recurringInterval === 1 && ' (every month on the same date)'}
            {recurringPattern === 'yearly' && recurringInterval === 1 && ' (every year on the same date)'}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecurringSelector;
