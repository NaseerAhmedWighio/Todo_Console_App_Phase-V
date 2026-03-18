# Email Verification & Task Reminder System

## Overview
This implementation adds **real email verification** to ensure only legitimate users can access the system and receive task reminders. Users must verify their email address before they can log in and use the application.

## Features

### 1. Email Verification on Registration
- **Verification Token**: Secure random token generated for each registration
- **Email Delivery**: Professional HTML email sent via SMTP
- **Token Expiration**: Verification tokens expire after 24 hours
- **Resend Capability**: Users can request a new verification email

### 2. Login Protection
- **Email Verification Required**: Users cannot login without verified email
- **Clear Error Messages**: Users informed if email is not verified
- **Quick Resend**: Option to resend verification email from login page

### 3. Task Reminder Emails
- **Automated Reminders**: Sends email reminders for upcoming tasks
- **Verified Users Only**: Only sends to users with verified emails
- **Smart Deduplication**: Avoids sending duplicate reminders within 1 hour
- **Customizable Timeframe**: Configurable hours-ahead window

## Setup & Configuration

### 1. Configure SMTP Settings

Copy `.env.example` to `.env` and configure:

```bash
# SMTP Server Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true

# Email Credentials
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password-here

# From Email
FROM_EMAIL=your-email@gmail.com

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### 2. Gmail App Password Setup

If using Gmail:

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the generated 16-character password
3. **Use App Password** in `SMTP_PASSWORD` (not your regular Gmail password)

### 3. Database Migration

Run migrations to create the `email_verifications` table:

```bash
cd backend
python init_db.py
```

## API Endpoints

### Registration & Verification

#### POST `/api/v1/auth/register`
Register a new user (sends verification email automatically)

```json
{
  "name": "John Doe",
  "email": "john@gmail.com",
  "password": "securepassword",
  "google_email_only": false
}
```

Response:
```json
{
  "success": true,
  "message": "Registration successful. Please check your email to verify your account.",
  "data": {
    "user": { ... },
    "token": "jwt_token",
    "is_google_email": true,
    "email_sent": true
  }
}
```

#### POST `/api/v1/auth/verify-email`
Verify email with token

**Query Parameters:**
- `token`: Verification token from email

Response:
```json
{
  "success": true,
  "message": "Email verified successfully",
  "data": {
    "user": { ... },
    "token": "new_jwt_token_with_verified_status"
  }
}
```

#### POST `/api/v1/auth/resend-verification`
Resend verification email

**Query Parameters:**
- `email`: User's email address

Response:
```json
{
  "success": true,
  "message": "Verification email sent"
}
```

#### GET `/api/v1/auth/verification-status`
Get current user's verification status

**Headers:** `Authorization: Bearer <token>`

Response:
```json
{
  "success": true,
  "data": {
    "is_verified": true,
    "email_verified_at": "2026-03-05T12:00:00Z"
  }
}
```

### Task Reminders

#### POST `/api/v1/reminders/send-reminders`
Manually trigger sending task reminder emails

**Query Parameters:**
- `hours_ahead`: Send reminders for tasks due within this many hours (default: 24)

**Headers:** `Authorization: Bearer <token>`

Response:
```json
{
  "success": true,
  "message": "Sent 3 reminder(s)",
  "data": {
    "total": 3,
    "sent": 3,
    "failed": 0,
    "skipped": 0
  }
}
```

## Frontend Pages

### 1. Registration Page (`/register`)
- Email validation with Google email detection
- Success message directing user to check email
- Clear instructions for next steps

### 2. Email Verification Page (`/verify-email`)
- Automatic verification when user clicks email link
- Success/error states with clear messaging
- Option to resend verification email if needed

### 3. Login Page (`/login`)
- Checks email verification status on login
- Shows error if email not verified
- Provides "Resend Verification Email" button

## Email Templates

### 1. Verification Email
Professional HTML email with:
- Branded design with styling
- Clear "Verify Email" button
- Verification code as fallback
- Expiration notice (24 hours)
- Security notice

### 2. Task Reminder Email
Informative reminder with:
- Task title and description
- Priority badge (color-coded)
- Due date and time
- Link to dashboard
- Professional styling

## Automated Reminder Worker

### Running the Worker

The reminder worker can be run periodically via cron job or scheduler:

```python
from backend.app.workers.reminder_worker import run_reminder_worker

# Run every hour via cron
stats = run_reminder_worker()
print(f"Sent {stats['sent']} reminders")
```

### Cron Example (Linux/Mac)
Run every hour:
```bash
0 * * * * cd /path/to/backend && python -c "from app.workers.reminder_worker import run_reminder_worker; run_reminder_worker()"
```

### Windows Task Scheduler
Create a scheduled task to run hourly:
```powershell
python -c "from backend.app.workers.reminder_worker import run_reminder_worker; run_reminder_worker()"
```

## Database Schema

### EmailVerification Table
```sql
CREATE TABLE email_verifications (
    id UUID PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP
);
```

### Updated User Table
```sql
ALTER TABLE users ADD COLUMN is_email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE users ADD COLUMN email_verified_at TIMESTAMP;
```

### Updated Reminders Table
```sql
ALTER TABLE reminders ADD COLUMN user_id UUID REFERENCES users(id);
ALTER TABLE reminders ADD COLUMN reminder_type VARCHAR(20);
ALTER TABLE reminders ADD COLUMN message TEXT;
```

## Security Features

1. **Token Expiration**: Verification tokens expire after 24 hours
2. **One-Time Use**: Tokens can only be used once
3. **Secure Generation**: Uses `secrets.token_urlsafe(32)` for tokens
4. **Email Privacy**: Doesn't reveal if email exists on resend
5. **Rate Limiting**: Prevents duplicate reminders within 1 hour

## Testing

### Test Email Verification Flow

1. **Register a new user**:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@gmail.com","password":"password123"}'
```

2. **Check email** for verification link

3. **Verify email**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/verify-email?token=YOUR_TOKEN"
```

4. **Login** (should work now):
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","password":"password123"}'
```

### Test Task Reminders

1. **Create a task** with due date within 24 hours
2. **Verify your email**
3. **Trigger reminders**:
```bash
curl -X POST "http://localhost:8000/api/v1/reminders/send-reminders?hours_ahead=24" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### Email Not Sending

**Problem**: Verification email not received

**Solutions**:
1. Check SMTP credentials in `.env`
2. Verify SMTP credentials are correct (use App Password for Gmail)
3. Check spam/junk folder
4. Check server logs: `backend/logs/`
5. Test SMTP connection manually

**Test SMTP**:
```python
import smtplib
server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login('your-email@gmail.com', 'your-app-password')
print("SMTP connection successful!")
```

### Token Expired

**Problem**: "Verification token expired" error

**Solution**:
1. Use the "Resend Verification Email" feature
2. Check email for new token
3. Verify within 24 hours

### Login Fails - Email Not Verified

**Problem**: "Email not verified" error on login

**Solution**:
1. Check email for verification link
2. Click "Resend Verification Email" from login page
3. Complete verification before logging in

## Files Modified/Created

### Backend
- `backend/app/models/email_verification.py` - Verification token model
- `backend/app/models/user.py` - Added email verification fields
- `backend/app/models/reminder.py` - Enhanced reminder model
- `backend/app/services/email_service.py` - Email sending service
- `backend/app/workers/reminder_worker.py` - Reminder automation worker
- `backend/app/api/auth_routes.py` - Verification endpoints
- `backend/app/api/reminder_routes.py` - Reminder trigger endpoint
- `backend/.env.example` - SMTP configuration

### Frontend
- `frontend/src/app/register/page.tsx` - Registration with verification notice
- `frontend/src/app/verify-email/page.tsx` - Email verification page
- `frontend/src/app/login/page.tsx` - Login with resend verification
- `frontend/src/components/Auth/AuthProvider.tsx` - Auth context with verification

## Next Steps

1. **Configure SMTP** in `.env` file
2. **Run database migrations** to create new tables
3. **Test registration flow** end-to-end
4. **Set up automated reminder worker** (cron/scheduler)
5. **Customize email templates** for branding
6. **Monitor email delivery** and adjust as needed

## Support

For issues or questions:
- Check backend logs: `backend/logs/`
- Review SMTP configuration
- Test email sending manually
- Verify database schema is up to date
