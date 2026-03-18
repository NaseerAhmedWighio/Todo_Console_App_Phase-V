# Login 401 Error - Resolution Guide

## Problem
Getting `401 Unauthorized` error when trying to login at `http://localhost:3000/login`

## Root Cause
The 401 error occurs when the email/password combination entered doesn't match any user in the database.

## Solution

### Option 1: Use the Test Account
A test account has been created for you:

**Email:** `test@example.com`  
**Password:** `testpassword123`

### Option 2: Create a New Account

#### Method A: Via Web Interface
1. Go to `http://localhost:3000/register`
2. Fill in your details:
   - Name: Your name
   - Email: Your email
   - Password: At least 6 characters
3. Click "Register"
4. You'll be automatically logged in

#### Method B: Via Command Line
```bash
cd D:\Hackathon\todo-app-phase-V\backend
.venv\Scripts\python.exe create_user.py
```

Follow the prompts to create your account.

### Option 3: Via API Directly
```bash
curl -X POST http://localhost:7860/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"your@email.com\",\"password\":\"yourpassword\",\"name\":\"Your Name\"}"
```

## Verify Backend is Running

Check if the backend server is running on port 7860:
```bash
netstat -ano | findstr :7860
```

If not running, start it:
```bash
cd D:\Hackathon\todo-app-phase-V\backend
.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 7860
```

## Verify Frontend is Running

Check if the frontend server is running on port 3000:
```bash
netstat -ano | findstr :3000
```

If not running, start it:
```bash
cd D:\Hackathon\todo-app-phase-V\frontend
npm run dev
```

## Check Database Connection

Verify the database has users:
```bash
cd D:\Hackathon\todo-app-phase-V\backend
.venv\Scripts\python.exe -c "from sqlmodel import Session, select; from app.database.session import engine; from app.models.user import User; session = Session(engine); users = session.exec(select(User)).all(); print(f'Users: {len(users)}'); [print(f'  - {u.email}') for u in users]; session.close()"
```

## Debug Login Attempts

The backend now logs login attempts. Check the backend console for messages like:
```
Login attempt for email: your@email.com
User not found: your@email.com
```
or
```
Login attempt for email: your@email.com
Password validation result: False
```

## Current Database Users

To see all users in the database:
```bash
cd D:\Hackathon\todo-app-phase-V\backend
.venv\Scripts\python.exe -c "from sqlmodel import Session, select; from app.database.session import engine; from app.models.user import User; session = Session(engine); users = session.exec(select(User)).all(); print(f'Total users: {len(users)}'); [print(f'  - {u.email} ({u.name})') for u in users]; session.close()"
```

## Test Login API Directly

Test the login API directly from command line:
```bash
cd D:\Hackathon\todo-app-phase-V\backend
.venv\Scripts\python.exe -c "import requests; r = requests.post('http://localhost:7860/api/v1/auth/login', json={'email': 'test@example.com', 'password': 'testpassword123'}); print(f'Status: {r.status_code}'); print(r.json())"
```

Expected output:
```
Status: 200
{'success': True, 'data': {'user': {...}, 'token': '...'}}
```

## Configuration

### Backend (.env)
- `DATABASE_URL`: Neon PostgreSQL connection string ✅
- `JWT_SECRET`: Secure random secret ✅
- `OPENROUTER_API_KEY`: OpenRouter API key ✅

### Frontend (.env.local)
- `NEXT_PUBLIC_API_BASE_URL=http://localhost:7860` ✅

## Troubleshooting

### Still getting 401?

1. **Check the email address**: Make sure you're using the exact email you registered with
2. **Check the password**: Passwords are case-sensitive
3. **Check backend logs**: Look for "Login attempt" messages in the backend console
4. **Test with known credentials**: Try `test@example.com` / `testpassword123`

### CORS errors?

The backend is configured to allow requests from `http://localhost:3000`. If you see CORS errors:
1. Make sure you're accessing the frontend via `http://localhost:3000` (not `http://127.0.0.1:3000`)
2. Check backend CORS configuration in `backend/main.py`

### Database connection errors?

1. Check your internet connection (Neon is cloud-hosted)
2. Verify your `DATABASE_URL` in `backend/.env`
3. Test connection: `cd backend && .venv\Scripts\python.exe test_db_connection.py`

## Quick Start Commands

```bash
# Start backend (in one terminal)
cd D:\Hackathon\todo-app-phase-V\backend
.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 7860

# Start frontend (in another terminal)
cd D:\Hackathon\todo-app-phase-V\frontend
npm run dev

# Open browser to
http://localhost:3000/login

# Login with test account
Email: test@example.com
Password: testpassword123
```
