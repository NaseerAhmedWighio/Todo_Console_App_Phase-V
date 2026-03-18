# Docker Build Commands Quick Reference

## 📦 Service Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                   │
│                     Port: 3000                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                    │
│                     Port: 7860                          │
└───────┬──────────────────────┬──────────────────────────┘
        │                      │
        ▼                      ▼
┌───────────────┐    ┌─────────────────┐
│    Redis      │    │     Kafka       │
│   Port: 6379  │    │   Port: 9092    │
└───────────────┘    └────────┬────────┘
                              │
                              ▼
                       ┌───────────────┐
                       │  Zookeeper    │
                       │  Port: 2181   │
                       └───────────────┘
```

---

## 🚀 Quick Start Commands (Windows PowerShell)

### **Option 1: Build Everything at Once**
```powershell
.\build-all.ps1
```

### **Option 2: Build Step-by-Step**

#### **Step 1: Infrastructure Services** (Pre-built images - just pull)
```powershell
.\build-infrastructure.ps1
```
This pulls and starts:
- Zookeeper (localhost:2181)
- Kafka (localhost:9092)
- Redis (localhost:6379)

#### **Step 2: Backend Service** (Custom build)
```powershell
.\build-backend.ps1
```
Builds and starts:
- Backend API (localhost:7860)

#### **Step 3: Frontend Service** (Custom build)
```powershell
.\build-frontend.ps1
```
Builds and starts:
- Frontend UI (localhost:3000)

---

## 🔧 Manual Docker Compose Commands

### **Infrastructure Services**
```powershell
# Pull all infrastructure images
docker-compose pull zookeeper kafka redis

# Start infrastructure services
docker-compose up -d zookeeper kafka redis

# View logs
docker-compose logs -f zookeeper kafka redis
```

### **Backend Service**
```powershell
# Build backend image
docker-compose build backend

# Start backend (requires infrastructure running)
docker-compose up -d backend

# View logs
docker-compose logs -f backend
```

### **Frontend Service**
```powershell
# Build frontend image
docker-compose build frontend

# Start frontend (requires backend running)
docker-compose up -d frontend

# View logs
docker-compose logs -f frontend
```

---

## 📋 Service Health Checks

### **Check All Services Status**
```powershell
docker-compose ps
```

### **Check Individual Service**
```powershell
docker-compose ps backend
docker-compose ps frontend
docker-compose ps kafka
docker-compose ps redis
docker-compose ps zookeeper
```

### **View Service Logs**
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

---

## 🛑 Stop & Clean Commands

### **Stop All Services**
```powershell
docker-compose down
```

### **Stop & Remove Volumes**
```powershell
docker-compose down -v
```

### **Stop Specific Service**
```powershell
docker-compose stop backend
docker-compose stop frontend
```

### **Remove Build Cache**
```powershell
docker-compose build --no-cache backend
docker-compose build --no-cache frontend
```

---

## 🌐 Service Endpoints

| Service     | URL                      | Port  |
|-------------|--------------------------|-------|
| Frontend    | http://localhost:3000    | 3000  |
| Backend API | http://localhost:7860    | 7860  |
| API Docs    | http://localhost:7860/docs | 7860  |
| Kafka       | localhost:9092           | 9092  |
| Redis       | localhost:6379           | 6379  |
| Zookeeper   | localhost:2181           | 2181  |

---

## 🔍 Troubleshooting

### **Backend won't start**
```powershell
# Check if infrastructure is running
docker-compose ps zookeeper kafka redis

# View backend logs
docker-compose logs backend
```

### **Frontend can't connect to backend**
```powershell
# Check backend health
curl http://localhost:7860/health

# Restart backend
docker-compose restart backend
```

### **Rebuild everything from scratch**
```powershell
# Stop and remove all
docker-compose down -v

# Remove images
docker rmi todo-app-phase-v-backend
docker rmi todo-app-phase-v-frontend

# Rebuild all
.\build-all.ps1
```

---

## 📝 Notes

- **Infrastructure services** (Kafka, Zookeeper, Redis) use pre-built Docker images - they only need to be pulled, not built
- **Backend & Frontend** are custom images that need to be built from your code
- Build times may vary based on your internet connection speed
- The scripts include retry logic for network timeouts
