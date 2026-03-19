# CI/CD Deployment Fix - Oracle Server

## Problem Fixed
The SSH deployment step was failing because:
1. Workflow referenced non-existent `docker-compose.backend.yml` and `docker-compose.frontend.yml` files
2. Missing `.env` file configuration on the server
3. Secret name mismatch (`SSH_KEY` vs `DEPLOY_KEY`)

## Changes Made

### 1. Created Production Docker Compose Files
- **`docker-compose.backend.yml`** - Backend + Infrastructure (Kafka, Redis, Zookeeper)
- **`docker-compose.frontend.yml`** - Frontend + Backend + Infrastructure

### 2. Updated CI/CD Workflow (`.github/workflows/ci-cd.yml`)

**Key improvements:**
- Uses `appleboy/scp-action` to copy docker-compose files to server
- Creates `.env` file from GitHub secrets on the server
- Pulls latest images from Docker Hub
- Deploys all services with proper health checks
- Uses `DEPLOY_KEY` secret for SSH authentication

## Required GitHub Secrets

### ✅ Secrets You Already Have:
- `DATABASE_URL`
- `DEPLOY_KEY` (RSA private key)
- `DOCKERHUB_TOKEN`
- `DOCKERHUB_USERNAME`
- `FROM_EMAIL`
- `OPENROUTER_API_KEY`
- `SERVER_IP`
- `SMTP_PASSWORD`
- `SMTP_USERNAME`

### ❌ Secrets You Need to Add:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `SERVER_USER` | SSH username for Oracle server | `root` or `ubuntu` |
| `JWT_SECRET` | Secret key for JWT tokens | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `SMTP_SERVER` | SMTP server hostname | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port | `587` |
| `SMTP_USE_TLS` | Enable TLS | `true` |
| `API_PROVIDER` | LLM API provider | `openrouter` |
| `CHAT_MODEL` | LLM model to use | `meta-llama/llama-3.2-3b-instruct:free` |

### Optional Secrets:
- `GEMINI_API_KEY` - If using Google Gemini instead of OpenRouter

## How to Add Secrets

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret from the table above

## Deployment Flow

```
┌─────────────────────────────────────────────────────────────┐
│  GitHub Actions Pipeline (on push to master)                │
├─────────────────────────────────────────────────────────────┤
│  1. Lint → Test → Build Backend → Build Frontend → Scan    │
│  2. Push images to Docker Hub                               │
│  3. Copy docker-compose files to Oracle server via SCP      │
│  4. SSH into server and:                                    │
│     a. Create .env file from secrets                        │
│     b. Login to Docker Hub                                  │
│     c. Pull latest images                                   │
│     d. Stop existing containers                             │
│     e. Start new containers                                 │
│     f. Wait for health checks                               │
│     g. Cleanup old images                                   │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Oracle Server (/home/opc/hackathon)                               │
├─────────────────────────────────────────────────────────────┤
│  docker-compose.backend.yml (deployed)                      │
│  docker-compose.frontend.yml (available)                    │
│  .env (created from secrets)                                │
│                                                             │
│  Services running:                                          │
│  - todo-backend (port 7860)                                 │
│  - todo-frontend (port 3000)                                │
│  - kafka (port 9092)                                        │
│  - zookeeper (port 2181)                                    │
│  - redis (port 6379)                                        │
└─────────────────────────────────────────────────────────────┘
```

## Manual Deployment (Alternative)

If you want to deploy manually on the Oracle server:

```bash
cd /home/opc/hackathon

# Create .env file
cat > .env << EOF
DATABASE_URL=your-database-url
JWT_SECRET=your-jwt-secret
OPENROUTER_API_KEY=your-api-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
EOF

# Login to Docker Hub
docker login -u naseerahmedwighio

# Pull images
docker pull naseerahmedwighio/todo-console-app-v-backend:latest
docker pull naseerahmedwighio/todo-console-app-v-frontend:latest

# Deploy
docker compose -f docker-compose.backend.yml up -d

# Check status
docker ps -a
docker logs todo-backend
docker logs todo-frontend
```

## Access Your Application

After deployment:
- **Frontend**: `http://<SERVER_IP>:3000`
- **Backend API**: `http://<SERVER_IP>:7860`
- **Health Check**: `http://<SERVER_IP>:7860/health`

## Troubleshooting

### SSH Connection Fails
```bash
# Test SSH connection manually
ssh -i ~/.ssh/your-key <SERVER_USER>@<SERVER_IP>
```

### Docker Compose Files Not Found
```bash
# Check files exist on server
ls -la /home/opc/hackathon/docker-compose*.yml
```

### Containers Not Starting
```bash
# Check logs
docker compose -f docker-compose.backend.yml logs -f
```

### Environment Variables Missing
```bash
# Check .env file
cat /home/opc/hackathon/.env
```

## Next Steps

1. **Add missing secrets** to GitHub Actions
2. **Commit and push** the docker-compose files:
   ```bash
   git add docker-compose.backend.yml docker-compose.frontend.yml
   git commit -m "Add production docker-compose files for deployment"
   git push origin master
   ```
3. **Monitor the pipeline** in GitHub Actions tab
4. **Verify deployment** by accessing `http://<SERVER_IP>:3000`

---

**Last Updated:** 2026-03-19
**Author:** Naseer Ahmed
