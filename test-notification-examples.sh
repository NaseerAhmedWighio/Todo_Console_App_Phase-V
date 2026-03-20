# ============================================
# Dapr Notification System - Test Examples
# ============================================
# This file contains curl commands to test the notification system
# Replace YOUR_JWT_TOKEN with your actual JWT token from login

# ============================================
# 1. TEST EMAIL CONFIGURATION
# ============================================
# Verify your SMTP settings are working
curl -X POST "http://localhost:7860/api/v1/notifications/send-test-email" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"

# ============================================
# 2. SCHEDULE ONE-TIME NOTIFICATION
# ============================================
# Schedule notification for a specific task at a specific time
# Replace {task_id} with an actual task UUID
curl -X POST "http://localhost:7860/api/v1/notifications/tasks/{task_id}/schedule?scheduled_time=2026-03-21T09:00:00Z" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# 3. VIEW SCHEDULED NOTIFICATIONS
# ============================================
# See all your scheduled notifications
curl "http://localhost:7860/api/v1/notifications/scheduled" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# 4. CREATE RECURRING TASK - PAY BILLS MONTHLY
# ============================================
# Perfect for monthly bill payments on the 1st
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Pay%20Monthly%20Bills&recurrence_pattern=pay_bills&by_monthday=1&notification_time=2026-03-21T09:00:00Z&priority=high&task_description=Pay all monthly bills including electricity, water, and internet" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# 5. CREATE RECURRING TASK - WEEKLY REVIEW
# ============================================
# Weekly review every Monday at 10 AM
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Weekly%20Review&recurrence_pattern=weekly&by_weekday=0&interval=1&notification_time=2026-03-24T10:00:00Z&priority=medium&task_description=Review weekly goals and plan next week" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# 6. CREATE RECURRING TASK - BIWEEKLY MEETING
# ============================================
# Team meeting every other Tuesday
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Biweekly%20Team%20Meeting&recurrence_pattern=biweekly&by_weekday=1&interval=1&notification_time=2026-03-25T14:00:00Z&priority=medium&task_description=Sprint planning and team sync" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# 7. CREATE RECURRING TASK - QUARTERLY TAXES
# ============================================
# Quarterly tax payment on the 15th
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Pay%20Quarterly%20Taxes&recurrence_pattern=quarterly&by_monthday=15&interval=1&notification_time=2026-04-15T08:00:00Z&priority=urgent&task_description=Submit quarterly tax payment" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# 8. CREATE RECURRING TASK - DAILY EXERCISE
# ============================================
# Daily morning exercise reminder
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Morning%20Exercise&recurrence_pattern=daily&interval=1&notification_time=2026-03-21T06:00:00Z&priority=medium&task_description=30 minutes of exercise" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# 9. CREATE RECURRING TASK - YEARLY SUBSCRIPTION
# ============================================
# Annual subscription renewal on January 1st
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Renew%20Annual%20Subscriptions&recurrence_pattern=yearly&by_month=1&by_monthday=1&notification_time=2027-01-01T09:00:00Z&priority=high&task_description=Renew all annual software subscriptions" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# 10. CREATE RECURRING TASK WITH END DATE
# ============================================
# Weekly task that ends on specific date
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=12-Week%20Project&recurrence_pattern=weekly&by_weekday=0&interval=1&end_condition=on_date&end_date=2026-06-30T23:59:59Z&notification_time=2026-03-21T09:00:00Z&priority=medium" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# 11. CREATE RECURRING TASK WITH END COUNT
# ============================================
# Task that repeats exactly 10 times
curl -X POST "http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=10-Week%20Challenge&recurrence_pattern=weekly&interval=1&end_condition=after_occurrences&end_occurrences=10&notification_time=2026-03-21T09:00:00Z&priority=medium" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# 12. VIEW ALL RECURRING TASKS
# ============================================
# List all your recurring task configurations
curl "http://localhost:7860/api/v1/recurring" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# 13. CANCEL SCHEDULED NOTIFICATION
# ============================================
# Cancel a scheduled notification for a task
curl -X POST "http://localhost:7860/api/v1/notifications/tasks/{task_id}/cancel" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# 14. GET RECURRING TASK DETAILS
# ============================================
# Get configuration for a specific recurring task
curl "http://localhost:7860/api/v1/recurring/tasks/{task_id}" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# 15. UPDATE RECURRING TASK CONFIGURATION
# ============================================
# Update the recurrence pattern or end conditions
curl -X PUT "http://localhost:7860/api/v1/recurring/tasks/{task_id}" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "interval": 2,
    "end_condition": "never"
  }'

# ============================================
# 16. DELETE RECURRING CONFIGURATION
# ============================================
# Remove recurring setup (optionally delete all instances)
curl -X DELETE "http://localhost:7860/api/v1/recurring/tasks/{task_id}?delete_all_instances=false" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ============================================
# HELPER: GET JWT TOKEN (Login)
# ============================================
# First login to get your JWT token
curl -X POST "http://localhost:7860/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@example.com",
    "password": "your-password"
  }'

# Extract the token from response and use it in above commands
# Response format: {"access_token": "YOUR_JWT_TOKEN", "token_type": "bearer"}
