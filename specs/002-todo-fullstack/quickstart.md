# Quickstart Guide: Todo Full-Stack Web Application - Phase II

## Overview
This guide provides instructions for setting up and running the Todo Full-Stack Web Application locally, including both frontend and backend components.

## Prerequisites
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- PostgreSQL (or access to Neon PostgreSQL)
- Git

## Backend Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd todo-fullstack-app
```

### 2. Navigate to Backend Directory
```bash
cd backend
```

### 3. Set up Python Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Set up Environment Variables
Create a `.env` file in the backend directory:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here
BETTER_AUTH_URL=http://localhost:3000
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256
```

### 6. Set up Database
```bash
# Run database migrations
alembic upgrade head
```

### 7. Run the Backend Server
```bash
# Start the development server
uvicorn src.api.main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`.

## Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend  # From the project root
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Set up Environment Variables
Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

### 4. Run the Frontend Development Server
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Authentication Setup

### Better Auth Configuration
1. Install Better Auth in the frontend:
```bash
npm install better-auth
```

2. Configure Better Auth with your secret and database settings

3. The authentication endpoints will be available at `/api/auth/*`

## API Endpoints

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user info

### Task Endpoints
- `GET /api/tasks` - Get all tasks for the authenticated user
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{task_id}` - Get a specific task
- `PUT /api/tasks/{task_id}` - Update a task
- `DELETE /api/tasks/{task_id}` - Delete a task
- `PATCH /api/tasks/{task_id}/complete` - Mark task as complete/incomplete

## Development Workflow

### Backend Development
1. Make changes to Python files
2. The server will automatically reload due to `--reload` flag
3. Test API endpoints using the documentation at `http://localhost:8000/docs`

### Frontend Development
1. Make changes to React/Next.js components
2. The development server will automatically reload
3. Access the application at `http://localhost:3000`

## Testing

### Backend Tests
```bash
# Run all backend tests
pytest

# Run tests with coverage
pytest --cov=src
```

### Frontend Tests
```bash
# Run all frontend tests
npm test

# Run tests in watch mode
npm run test:watch
```

## Environment Configuration

### Development Environment
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Database: Local PostgreSQL or Neon dev instance

### Production Environment
- Backend: `https://api.yourdomain.com`
- Frontend: `https://yourdomain.com`
- Database: Neon production instance

## Deployment

### Backend Deployment
1. Deploy to platforms like Railway, Render, or Vercel
2. Set environment variables in the deployment platform
3. Run database migrations as part of deployment process

### Frontend Deployment
1. Deploy to Vercel, Netlify, or Cloudflare Pages
2. Set environment variables for API base URL
3. Build command: `npm run build`
4. Output directory: `out` (for Next.js)

## Troubleshooting

### Common Issues
1. **Port already in use**: Change the port in the startup commands
2. **Database connection errors**: Verify DATABASE_URL in .env
3. **Authentication errors**: Check that BETTER_AUTH_SECRET matches between frontend and backend
4. **CORS errors**: Ensure frontend URL is properly configured in backend settings

### Getting Help
- Check the API documentation at `/docs` endpoint
- Review the application logs
- Consult the project specification documents in the `specs/` directory