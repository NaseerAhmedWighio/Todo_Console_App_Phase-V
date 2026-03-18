# Installation & Setup Guide
## Recurring Tasks & Reminders System

---

## 📋 Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for Redis)
- Git

---

## 🚀 Quick Installation

### Step 1: Install Backend Dependencies

```bash
cd backend

# Install Python packages including Celery & Redis
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed celery-5.x.x redis-4.x.x ...
```

### Step 2: Install Frontend Dependencies

```bash
cd frontend

# Install Node packages
npm install
```

**Expected Output:**
```
added XXX packages in XXs
```

### Step 3: Start Redis (Docker)

```bash
# Start Redis container
docker run -d -p 6379:6379 --name todo-redis redis:alpine

# Verify Redis is running
docker ps | grep redis
# Should show: todo-redis
```

**Alternative: Install Redis locally**
- Windows: Download from https://github.com/microsoftarchive/redis/releases
- Mac: `brew install redis`
- Linux: `sudo apt-get install redis-server`

---

## ⚙️ Configuration

### Backend Configuration

Create `backend/.env`:

```bash
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# JWT Secret
JWT_SECRET=your-super-secret-key-change-in-production

# Email/SMTP Configuration (for reminders)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
SMTP_USE_TLS=true

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

**Getting Gmail App Password:**
1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification"
3. Go to "App passwords"
4. Generate new password for "Mail"
5. Copy the 16-character password to `.env`

### Frontend Configuration

Ensure `frontend/.env.local` exists:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8001
```

---

## ▶️ Starting Services

### Option 1: Quick Start Script (Recommended)

```bash
# Windows
start-testing.bat

# This will start:
# - Redis (if not running)
# - Celery Worker
# - Celery Beat
# - FastAPI Backend
# - Frontend (Next.js)
```

### Option 2: Manual Start

#### Terminal 1: Celery Worker

```bash
cd backend
celery -A backend.app.workers.celery_app worker --loglevel=info --pool=solo
```

**Expected Output:**
```
 -------------- celery@YOURHOST v5.x.x
--- * -----
-- * ----- ****
- * ----- *******
- ---------------

[2026-03-10 12:00:00,000] INFO: Setting up worker...
[2026-03-10 12:00:00,000] INFO: Connected to Redis
[2026-03-10 12:00:00,000] INFO: Ready to process tasks
```

#### Terminal 2: Celery Beat (Scheduler)

```bash
cd backend
celery -A backend.app.workers.celery_app beat --loglevel=info
```

**Expected Output:**
```
celery beat v5.x.x is starting.
2026-03-10 12:00:00,000: INFO: Database: File-based database
2026-03-10 12:00:00,000: INFO: Scheduler: Starting scheduler...
2026-03-10 12:00:00,000: INFO: Scheduled tasks:
  - process-reminders-every-minute: Every minute
  - generate-recurring-tasks-every-minute: Every minute
```

#### Terminal 3: FastAPI Backend

```bash
cd backend
python main.py
# Or
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

**Expected Output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8001
```

#### Terminal 4: Frontend

```bash
cd frontend
npm run dev
```

**Expected Output:**
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
```

---

## ✅ Verification

### Check All Services

```bash
# 1. Check Redis
docker ps | grep redis
# Should show: todo-redis

# 2. Check Celery Worker
# Look for "Ready to process tasks" in Terminal 1

# 3. Check Celery Beat
# Look for "Starting scheduler" in Terminal 2

# 4. Check Backend
curl http://localhost:8001/health
# Should return: {"status":"healthy"}

# 5. Check Frontend
# Open http://localhost:3000 in browser
```

### Test Recurring Detection

```bash
cd backend
python -c "
from app.services.recurring_detection_service import get_recurring_detection_service
svc = get_recurring_detection_service()
result = svc.detect_recurring('Pay electricity bill', 'Monthly utility payment')
print(f'Detection: {result}')
"
```

**Expected Output:**
```
Detection: {'is_recurring': True, 'confidence': 0.95, 'pattern': 'monthly', ...}
```

---

## 🧪 First Test

### Create Test Account

1. Open http://localhost:3000
2. Click "Sign Up"
3. Create account with your email
4. Verify email (if required)

### Create Recurring Task

1. In dashboard, fill TaskForm:
   - Title: "Pay electricity bill"
   - Description: "Monthly utility payment"
   - Due Date: Any future date
   - Priority: High

2. Watch for auto-detection banner:
   ```
   🔄 Recurring task detected!
   Matched keywords: bill, electricity, monthly
   Pattern: monthly (Confidence: 95%)
   ```

3. Click "Create Task"

4. Check Celery Worker logs (Terminal 1):
   ```
   [INFO] Auto-detected recurring task: Matched recurring keywords...
   ```

5. Wait 1 minute

6. Check Celery Beat logs (Terminal 2):
   ```
   [INFO] Starting recurring task generation...
   [INFO] Generated instance abc-123 for recurring task xyz-789
   ```

### Create Reminder

```bash
# Get your task ID from database or API response
# Then create reminder:

curl -X POST "http://localhost:8001/api/v1/reminders/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "YOUR_TASK_ID",
    "timing_minutes": 30,
    "delivery_channel": "email"
  }'
```

Wait for scheduled time and check your email!

---

## 🐛 Troubleshooting

### Issue: Celery not starting

**Error:** `ModuleNotFoundError: No module named 'celery'`

**Solution:**
```bash
cd backend
pip install celery redis
```

### Issue: Redis connection refused

**Error:** `redis.exceptions.ConnectionError: Error connecting to Redis`

**Solution:**
```bash
# Start Redis container
docker run -d -p 6379:6379 --name todo-redis redis:alpine

# Or check if Redis is already running
docker ps | grep redis
```

### Issue: Email not sending

**Error:** `SMTPAuthenticationError`

**Solution:**
1. Use Gmail App Password (not regular password)
2. Enable 2-Step Verification in Google Account
3. Check SMTP credentials in `.env`

**Test SMTP:**
```bash
cd backend
python -c "
from app.services.email_service import email_service
result = email_service.send_email('your-email@gmail.com', 'Test', 'Test body')
print(f'Email sent: {result}')
"
```

### Issue: Recurring tasks not generating

**Check:**
```sql
-- Verify recurring task exists
SELECT * FROM recurring_tasks WHERE is_active = true;

-- Check next_due_date
SELECT task_id, next_due_date FROM recurring_tasks;
```

**Manually trigger:**
```bash
cd backend
python -c "
from app.workers.recurring_worker import generate_recurring_instances
result = generate_recurring_instances()
print(f'Generated: {result}')
"
```

### Issue: Frontend not detecting recurring

**Check browser console** for errors

**Verify API endpoint:**
```bash
curl -X POST "http://localhost:8001/api/v1/todos/detect-recurring?title=Pay%20electricity%20bill" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📊 Monitoring

### View Celery Tasks

```bash
# Active tasks
celery -A backend.app.workers.celery_app inspect active

# Task statistics
celery -A backend.app.workers.celery_app inspect stats

# Registered tasks
celery -A backend.app.workers.celery_app inspect registered
```

### Database Queries

```sql
-- Check recurring tasks
SELECT rt.id, rt.recurrence_pattern, rt.next_due_date, t.title
FROM recurring_tasks rt
JOIN todos t ON rt.task_id = t.id
WHERE rt.is_active = true;

-- Check reminders
SELECT r.id, r.status, r.scheduled_time, t.title, u.email
FROM reminders r
JOIN todos t ON r.task_id = t.id
JOIN users u ON r.user_id = u.id
ORDER BY r.scheduled_time DESC;

-- Check generated instances
SELECT id, title, due_date, created_at
FROM todos
WHERE recurring_task_id IS NOT NULL
ORDER BY created_at DESC;
```

---

## 🎯 Production Deployment

### Before Deploying:

1. **Change Celery Schedule:**
   ```python
   # backend/app/workers/celery_app.py
   'generate-recurring-tasks-every-hour': {
       'schedule': crontab(minute='0'),  # Change from */1 to 0
   },
   ```

2. **Update Reminder Window:**
   ```python
   # backend/app/workers/reminder_worker.py
   stats = worker.send_all_reminders(hours_ahead=24)  # Change from 1 to 24
   ```

3. **Set Production Environment Variables:**
   ```bash
   JWT_SECRET=strong-random-secret
   DATABASE_URL=production-database-url
   SMTP_PASSWORD=production-email-password
   ```

4. **Use Production-Ready WSGI Server:**
   ```bash
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

5. **Set Up Monitoring:**
   - Sentry for error tracking
   - Prometheus/Grafana for metrics
   - Log aggregation (ELK stack)

---

## ✅ Installation Checklist

- [ ] Python 3.11 installed
- [ ] Node.js 18+ installed
- [ ] Docker installed and running
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Redis container started
- [ ] Backend `.env` created with all variables
- [ ] Frontend `.env.local` created
- [ ] Celery Worker started successfully
- [ ] Celery Beat started successfully
- [ ] FastAPI Backend running
- [ ] Frontend running
- [ ] Test account created
- [ ] Test recurring task created
- [ ] Email reminder tested

---

## 🎉 Success!

If all services are running, you should see:

```
✅ Redis: Running on localhost:6379
✅ Celery Worker: Processing tasks
✅ Celery Beat: Scheduling every minute
✅ Backend: Running on http://localhost:8001
✅ Frontend: Running on http://localhost:3000
✅ Email Service: Configured and ready
```

**You're ready to test recurring tasks and reminders!** 🚀

For detailed testing instructions, see: `RECURRING_REMINDER_TESTING_GUIDE.md`
