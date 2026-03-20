# Dapr Notification System Guide

## Overview

This guide explains how to use the Dapr-based notification system for sending scheduled and recurring email notifications to users. The system supports multiple patterns including daily, weekly, monthly, yearly, biweekly, quarterly, and custom patterns like "Pay Bills".

## Architecture

### Components

1. **Dapr Cron Bindings** - Trigger notification checks at regular intervals
   - `scheduled-notifications`: Runs every minute to check for due notifications
   - `recurring-tasks`: Runs every 5 minutes to process recurring task patterns

2. **Notification Handler** (`backend/app/dapr/notification_handler.py`)
   - Processes scheduled notifications
   - Handles recurring task patterns
   - Sends emails via the Email Service

3. **Email Service** (`backend/app/services/email_service.py`)
   - Sends HTML-formatted emails
   - Supports task reminders, verification, and recurring notifications

4. **API Routes**
   - `/api/v1/notifications/tasks/{task_id}/schedule` - Schedule one-time notification
   - `/api/v1/recurring/create-with-notifications` - Create recurring task with notifications

## Supported Recurring Patterns

| Pattern | Description | Example Use Case |
|---------|-------------|------------------|
| `daily` | Every day at the same time | Daily standup, exercise |
| `weekly` | Every week on specified day(s) | Weekly review, team meeting |
| `biweekly` | Every 2 weeks | Sprint planning, biweekly reports |
| `monthly` | Every month on specified day | Monthly reports, rent payment |
| `quarterly` | Every 3 months | Quarterly taxes, business reviews |
| `yearly` | Every year | Annual subscriptions, birthdays |
| `pay_bills` | Monthly bill payment pattern | Utility bills, credit card payments |

## Setup Instructions

### 1. Configure Email Settings

Add your SMTP credentials to `.env`:

```bash
# SMTP Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true

# Email Credentials (use App Password for Gmail)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here

# From Email
FROM_EMAIL=your-email@gmail.com
```

### 2. Start Dapr Sidecar

Run the backend with Dapr:

```bash
# From backend directory
dapr run --app-id todo-backend \
  --app-port 7860 \
  --dapr-http-port 3500 \
  --components-path ../dapr/components \
  --resources-path ../dapr/components \
  python -m uvicorn main:app --host 0.0.0.0 --port 7860
```

### 3. Verify Dapr Components

Check that Dapr components are loaded:

```bash
dapr components
```

You should see:
- `scheduled-notifications` (cron binding)
- `recurring-tasks` (cron binding)
- `notification-pubsub` (Kafka pub/sub)
- `kafka-pubsub` (main pub/sub)

## API Usage Examples

### Schedule One-Time Notification

```bash
# Schedule notification for a specific time
curl -X POST "http://localhost:7860/api/v1/notifications/tasks/{task_id}/schedule?scheduled_time=2026-03-21T09:00:00Z" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Create Recurring Task with Notifications

**Example 1: Monthly Bill Payment (Pay Bills on 1st of every month)**

```bash
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Pay%20Monthly%20Bills&recurrence_pattern=pay_bills&by_monthday=1&notification_time=2026-03-21T09:00:00Z&priority=high" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Example 2: Weekly Review (Every Monday)**

```bash
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Weekly%20Review&recurrence_pattern=weekly&by_weekday=0&interval=1&notification_time=2026-03-24T10:00:00Z&priority=medium" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Example 3: Biweekly Team Meeting**

```bash
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Team%20Meeting&recurrence_pattern=biweekly&by_weekday=1&interval=1&notification_time=2026-03-25T14:00:00Z&priority=medium" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Example 4: Quarterly Tax Payment**

```bash
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Pay%20Quarterly%20Taxes&recurrence_pattern=quarterly&by_monthday=15&interval=1&notification_time=2026-04-15T08:00:00Z&priority=urgent" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Example 5: Daily Exercise**

```bash
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Morning%20Exercise&recurrence_pattern=daily&interval=1&notification_time=2026-03-21T06:00:00Z&priority=medium" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### With End Conditions

**Recurring task that ends after 10 occurrences:**

```bash
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=10-Week%20Challenge&recurrence_pattern=weekly&end_condition=after_occurrences&end_occurrences=10&notification_time=2026-03-21T09:00:00Z" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Recurring task that ends on a specific date:**

```bash
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Project%20Deadline&recurrence_pattern=weekly&end_condition=on_date&end_date=2026-12-31T23:59:59Z&notification_time=2026-03-21T09:00:00Z" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Frontend Integration

### Using the NotificationScheduler Component

```tsx
import { NotificationScheduler } from '@/components/NotificationScheduler/NotificationScheduler';
import { taskService } from '@/services/tasks';

function TaskForm() {
  const handleNotificationChange = async (config) => {
    if (!config.is_recurring && config.scheduled_time) {
      // Schedule one-time notification
      await taskService.scheduleNotification(taskId, config.scheduled_time);
    } else if (config.is_recurring) {
      // Create recurring task
      await taskService.createRecurringTaskWithNotifications(taskTitle, {
        recurrence_pattern: config.recurrence_pattern,
        interval: config.interval,
        by_monthday: config.by_monthday,
        notification_time: config.scheduled_time,
      });
    }
  };

  return (
    <NotificationScheduler
      value={notificationConfig}
      onChange={handleNotificationChange}
    />
  );
}
```

### Using the RecurringConfig Component

```tsx
import { RecurringConfig } from '@/components/RecurringConfig/RecurringConfig';

function RecurringTaskForm() {
  const handleConfigChange = async (config) => {
    // Save recurring configuration
    await api.post('/api/v1/recurring/tasks/{task_id}', config);
  };

  return (
    <RecurringConfig
      value={recurringConfig}
      onChange={handleConfigChange}
    />
  );
}
```

## Testing

### Test Email Configuration

```bash
curl -X POST "http://localhost:7860/api/v1/notifications/send-test-email" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### View Scheduled Notifications

```bash
curl "http://localhost:7860/api/v1/notifications/scheduled" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### List Recurring Tasks

```bash
curl "http://localhost:7860/api/v1/recurring" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Troubleshooting

### Notifications Not Being Sent

1. **Check Dapr logs:**
   ```bash
   dapr logs --app-id todo-backend
   ```

2. **Verify cron bindings are active:**
   ```bash
   kubectl get components  # For Kubernetes
   ```

3. **Check email service configuration:**
   - Verify SMTP credentials in `.env`
   - Ensure email verification is enabled for user

4. **Check database for due notifications:**
   ```sql
   SELECT * FROM todos 
   WHERE scheduled_time <= NOW() 
   AND notification_sent = FALSE;
   ```

### Recurring Tasks Not Creating Instances

1. **Check recurring task configuration:**
   ```sql
   SELECT * FROM recurring_tasks WHERE is_active = TRUE;
   ```

2. **Verify the recurring task handler is running:**
   - Check logs for "Recurring notification processing completed"

3. **Check next_due_date:**
   ```sql
   SELECT id, next_due_date, last_generated_date 
   FROM recurring_tasks;
   ```

## Database Schema

### Todos Table (Notification Fields)

```sql
ALTER TABLE todos ADD COLUMN scheduled_time TIMESTAMPTZ;
ALTER TABLE todos ADD COLUMN notification_sent BOOLEAN DEFAULT FALSE;
ALTER TABLE todos ADD COLUMN notified_at TIMESTAMPTZ;
ALTER TABLE todos ADD COLUMN is_recurring BOOLEAN DEFAULT FALSE;
ALTER TABLE todos ADD COLUMN recurring_task_id UUID REFERENCES recurring_tasks(id);
ALTER TABLE todos ADD COLUMN timezone VARCHAR(50) DEFAULT 'UTC';
```

### Recurring Tasks Table

```sql
CREATE TABLE recurring_tasks (
    id UUID PRIMARY KEY,
    task_id UUID REFERENCES todos(id) ON DELETE CASCADE,
    recurrence_pattern VARCHAR(50) NOT NULL,
    interval INTEGER DEFAULT 1,
    by_weekday VARCHAR(50),
    by_monthday INTEGER,
    by_month VARCHAR(50),
    end_condition VARCHAR(20) DEFAULT 'never',
    end_occurrences INTEGER,
    end_date TIMESTAMPTZ,
    last_generated_date TIMESTAMPTZ,
    next_due_date TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Best Practices

1. **Email Verification**: Always verify user emails before sending notifications
2. **Timezone Handling**: Store and process all times in UTC, convert to user's timezone for display
3. **Notification Timing**: Schedule notifications 1 hour before the actual due time
4. **Error Handling**: Log all email sending failures for debugging
5. **Rate Limiting**: Implement rate limiting for email sending to avoid SMTP throttling
6. **Testing**: Send test emails to verify configuration before going live

## Production Deployment

### Kubernetes Deployment

The Dapr components are automatically deployed with the backend pod. Ensure the following annotations are present:

```yaml
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "todo-backend"
    dapr.io/app-port: "7860"
```

### Environment Variables

```bash
# Dapr Configuration
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
DAPR_PUBSUB_NAME=kafka-pubsub

# Notification Settings
NOTIFICATION_ENABLED=true
NOTIFICATION_CHECK_INTERVAL_MINUTES=1
RECURRING_NOTIFICATION_ENABLED=true
RECURRING_CHECK_INTERVAL_MINUTES=5
```

## Support

For issues or questions:
1. Check the logs: `dapr logs --app-id todo-backend`
2. Verify email configuration with test endpoint
3. Ensure Dapr sidecar is running alongside backend
4. Check database for scheduled notifications
