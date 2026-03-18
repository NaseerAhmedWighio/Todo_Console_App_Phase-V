# Recurring Tasks & Reminders Testing Guide
## Every Minute Testing Configuration ⚡

---

## 🚀 What Was Changed

### 1. **Celery Beat Schedule** - Every Minute Testing
**File:** `backend/app/workers/celery_app.py`

```python
# FOR TESTING - Both run every minute
beat_schedule={
    'process-reminders-every-minute': {
        'task': 'backend.app.workers.reminder_worker.process_due_reminders',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
    'generate-recurring-tasks-every-minute': {
        'task': 'backend.app.workers.recurring_worker.generate_recurring_instances',
        'schedule': crontab(minute='*/1'),  # Every minute
    },
}
```

### 2. **Reminder Worker** - Celery Task Added
**File:** `backend/app/workers/reminder_worker.py`

Added `process_due_reminders()` Celery task that:
- Runs every minute
- Checks for tasks due in the next **1 hour** (for testing)
- Sends email reminders
- Creates reminder records

### 3. **Email Service** - Already Configured ✅
**File:** `backend/app/services/email_service.py`

- `send_task_reminder_email()` method ready
- Beautiful HTML email template
- Priority color coding

---

## ⚙️ Setup Instructions

### Step 1: Configure SMTP Settings

Create/update `.env` in backend directory:

```bash
# SMTP Configuration for Email Reminders
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true

# For Gmail, you need an App Password:
# 1. Go to Google Account settings
# 2. Security → 2-Step Verification → App passwords
# 3. Generate new app password for "Mail"
```

**Alternative SMTP Providers:**
- **Outlook:** `smtp-mail.outlook.com`, port 587
- **Yahoo:** `smtp.mail.yahoo.com`, port 587
- **SendGrid:** `smtp.sendgrid.net`, port 587

### Step 2: Start Redis (Celery Broker)

```bash
# Windows (using Docker)
docker run -d -p 6379:6379 redis:alpine

# Or install Redis locally
redis-server
```

### Step 3: Start Celery Worker & Beat

```bash
# In backend directory
# Terminal 1: Celery Worker
celery -A backend.app.workers.celery_app worker --loglevel=info --pool=solo

# Terminal 2: Celery Beat (Scheduler)
celery -A backend.app.workers.celery_app beat --loglevel=info
```

**Windows Alternative (single command):**
```bash
# Start both worker and beat
celery -A backend.app.workers.celery_app worker --loglevel=info --pool=solo -B
```

### Step 4: Start FastAPI Backend

```bash
# In backend directory
python main.py
# Or
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Step 5: Start Frontend

```bash
# In frontend directory
npm run dev
```

---

## 🧪 Testing Recurring Tasks

### Test 1: Create a Daily Recurring Task

```bash
# Using curl
curl -X POST "http://localhost:8001/api/v1/todos/?auto_recurring=true" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Morning walk",
    "description": "Daily exercise routine",
    "priority": "medium",
    "due_date": "2026-03-11T07:00:00Z"
  }'
```

**Expected Result:**
- Task created with `is_recurring=true`
- `RecurringTask` record created
- Pattern: daily
- Next instance generated within 1 minute

### Test 2: Check Celery Logs

```
[2026-03-10 12:00:00,000] INFO: Starting recurring task generation...
[2026-03-10 12:00:01,000] INFO: Found 1 recurring tasks to process
[2026-03-10 12:00:02,000] INFO: Generated instance abc-123 for recurring task xyz-789
[2026-03-10 12:00:02,000] INFO: Processed 1 recurring tasks
```

### Test 3: Verify in Database

```sql
-- Check recurring task configuration
SELECT * FROM recurring_tasks 
WHERE task_id = 'YOUR_TASK_ID';

-- Check generated instances
SELECT id, title, due_date, is_recurring, recurring_task_id 
FROM todos 
WHERE recurring_task_id = 'YOUR_RECURRING_TASK_ID'
ORDER BY due_date;
```

---

## 📧 Testing Email Reminders

### Test 1: Create Task with Reminder

```bash
# 1. Create a task due in 30 minutes
curl -X POST "http://localhost:8001/api/v1/todos/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Take medicine",
    "description": "After lunch medication",
    "priority": "high",
    "due_date": "2026-03-10T13:30:00Z"
  }'

# 2. Create a reminder (15 minutes before)
curl -X POST "http://localhost:8001/api/v1/reminders/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "TASK_ID_FROM_STEP_1",
    "timing_minutes": 15,
    "timing_days": null,
    "delivery_channel": "email"
  }'
```

### Test 2: Wait for Reminder

- Celery Beat runs every minute
- When `scheduled_time <= now`, reminder is sent
- Check email inbox after 1 minute

### Test 3: Check Reminder Logs

```
[2026-03-10 12:15:00,000] INFO: Starting reminder processing...
[2026-03-10 12:15:01,000] INFO: Sent reminder email for task abc-123 to user xyz-789
[2026-03-10 12:15:01,000] INFO: Reminder processing completed: {'total': 1, 'sent': 1, 'failed': 0, 'skipped': 0}
```

### Test 4: Verify Reminder Record

```sql
-- Check reminder was created and sent
SELECT r.*, t.title as task_title, u.email
FROM reminders r
JOIN todos t ON r.task_id = t.id
JOIN users u ON r.user_id = u.id
ORDER BY r.created_at DESC
LIMIT 5;
```

---

## 🎯 Complete End-to-End Test

### Scenario: Bill Payment with Reminder

```bash
# 1. Login and get token
curl -X POST "http://localhost:8001/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Save the token from response

# 2. Create monthly recurring task
curl -X POST "http://localhost:8001/api/v1/todos/?auto_recurring=true" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Pay electricity bill",
    "description": "Monthly utility payment",
    "priority": "high",
    "due_date": "2026-03-15T18:00:00Z"
  }'

# Response should show is_recurring: true

# 3. Create reminder (1 day before)
TASK_ID="response.data.id"

curl -X POST "http://localhost:8001/api/v1/reminders/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "'$TASK_ID'",
    "timing_days": 1,
    "timing_minutes": 0,
    "delivery_channel": "email"
  }'

# 4. Wait and check:
# - Celery Beat generates next month's instance (within 1 minute)
# - Email reminder sent 1 day before due date
# - Check email inbox
```

---

## 📊 Monitoring & Debugging

### Check Celery Worker Status

```bash
# View active tasks
celery -A backend.app.workers.celery_app inspect active

# View registered tasks
celery -A backend.app.workers.celery_app inspect registered

# View worker stats
celery -A backend.app.workers.celery_app inspect stats
```

### View Task Results

```bash
# In Python shell
from celery.result import AsyncResult
from backend.app.workers.celery_app import celery_app

result = AsyncResult('TASK_ID', app=celery_app)
print(result.status)
print(result.result)
```

### Database Queries for Debugging

```sql
-- Check all recurring tasks
SELECT rt.*, t.title 
FROM recurring_tasks rt
JOIN todos t ON rt.task_id = t.id
WHERE rt.is_active = true;

-- Check all reminders
SELECT r.*, t.title, u.email, r.status, r.sent_at
FROM reminders r
JOIN todos t ON r.task_id = t.id
JOIN users u ON r.user_id = u.id
ORDER BY r.scheduled_time DESC;

-- Check tasks due in next hour (what reminder worker sees)
SELECT t.*, u.email, u.name
FROM todos t
JOIN users u ON t.user_id = u.id
WHERE t.is_completed = false
  AND t.due_date IS NOT NULL
  AND t.due_date >= NOW()
  AND t.due_date <= NOW() + INTERVAL '1 hour'
  AND u.is_email_verified = true;
```

---

## 🐛 Common Issues & Solutions

### Issue 1: Reminders Not Sending

**Check:**
1. SMTP credentials in `.env`
2. User email is verified (`is_email_verified = true`)
3. Task is not completed
4. Reminder `scheduled_time <= now`

**Solution:**
```sql
-- Manually verify user email for testing
UPDATE users 
SET is_email_verified = true, email_verified_at = NOW()
WHERE email = 'test@example.com';
```

### Issue 2: Recurring Tasks Not Generating

**Check:**
1. Celery Beat is running
2. `is_active = true` on recurring task
3. `next_due_date <= now`

**Solution:**
```sql
-- Manually trigger generation
SELECT generate_recurring_instances();

-- Or update next_due_date to past
UPDATE recurring_tasks
SET next_due_date = NOW() - INTERVAL '1 hour'
WHERE task_id = 'YOUR_TASK_ID';
```

### Issue 3: Celery Tasks Not Running

**Check:**
1. Redis is running: `redis-cli ping` → should return `PONG`
2. Worker is connected to correct broker
3. Beat scheduler is running

**Solution:**
```bash
# Restart Celery with verbose logging
celery -A backend.app.workers.celery_app worker --loglevel=debug --pool=solo
```

---

## 📈 Production Configuration

### Change Back to Hourly/Daily

**File:** `backend/app/workers/celery_app.py`

```python
beat_schedule={
    # Production: Check reminders every minute (OK to keep)
    'process-reminders-every-minute': {
        'task': 'backend.app.workers.reminder_worker.process_due_reminders',
        'schedule': crontab(minute='*/1'),
    },

    # Production: Generate recurring tasks hourly (NOT every minute)
    'generate-recurring-tasks-every-hour': {
        'task': 'backend.app.workers.recurring_worker.generate_recurring_instances',
        'schedule': crontab(minute='0'),  # Every hour
    },
    
    # ... rest of config
}
```

### Update Reminder Check Window

**File:** `backend/app/workers/reminder_worker.py`

```python
@shared_task
def process_due_reminders(self):
    # ...
    # Production: Check next 24 hours
    stats = worker.send_all_reminders(hours_ahead=24)
    # ...
```

---

## ✅ Testing Checklist

- [ ] Redis is running
- [ ] SMTP credentials configured
- [ ] Celery worker started
- [ ] Celery Beat started
- [ ] Backend API running
- [ ] Frontend running
- [ ] User email verified
- [ ] Created recurring task
- [ ] Verified recurring task in DB
- [ ] Waited 1 minute
- [ ] Checked new instance generated
- [ ] Created reminder
- [ ] Waited for scheduled time
- [ ] Received email reminder
- [ ] Checked reminder record in DB

---

## 🎉 Success Indicators

### Recurring Tasks Working:
```
✅ Task created with is_recurring=true
✅ RecurringTask record exists
✅ After 1 minute: new instance in todos table
✅ Celery logs show "Generated instance"
```

### Reminders Working:
```
✅ Reminder record created with status='pending'
✅ scheduled_time calculated correctly
✅ After scheduled time: email received
✅ Reminder status updated to 'sent'
✅ Celery logs show "Sent reminder email"
```

---

## 📝 Summary

| Feature | Schedule | Status |
|---------|----------|--------|
| **Recurring Generation** | Every minute (testing) | ✅ Configured |
| **Reminder Processing** | Every minute | ✅ Configured |
| **Email Service** | On-demand | ✅ Ready |
| **Celery Worker** | Continuous | ✅ Ready |
| **Celery Beat** | Every minute | ✅ Ready |

**Next Steps:**
1. Configure SMTP credentials
2. Start Redis, Celery Worker, Celery Beat
3. Create test task with recurring + reminder
4. Watch the magic happen! ✨
