# Deploy Todo App to Minikube (PowerShell)
# This script builds images and deploys everything to Kubernetes

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Todo App - Kubernetes Deployment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Configuration
$PROFILE = "todo-app"
$NAMESPACE = "todo-app"
$RELEASE_NAME = "todo-app"

Write-Host ""
Write-Host "1. Building Docker images..." -ForegroundColor Yellow

# Build backend image
Write-Host "Building backend image..." -ForegroundColor Gray
docker-compose build backend

# Build frontend image
Write-Host "Building frontend image..." -ForegroundColor Gray
docker-compose build frontend

Write-Host "✓ Docker images built" -ForegroundColor Green

Write-Host ""
Write-Host "2. Loading images into Minikube..." -ForegroundColor Yellow

# Load images into Minikube
minikube image load todo-app-phase-v-backend:latest -p $PROFILE
minikube image load todo-app-phase-v-frontend:latest -p $PROFILE

Write-Host "✓ Images loaded into Minikube" -ForegroundColor Green

Write-Host ""
Write-Host "3. Creating namespace..." -ForegroundColor Yellow

# Create namespace
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

Write-Host "✓ Namespace created: $NAMESPACE" -ForegroundColor Green

Write-Host ""
Write-Host "4. Deploying infrastructure (Kafka, Redis, Zookeeper)..." -ForegroundColor Yellow

# Deploy infrastructure
helm upgrade --install infrastructure `
    ./k8s/helm/infrastructure `
    --namespace $NAMESPACE `
    --create-namespace `
    --wait `
    --timeout 10m

Write-Host "✓ Infrastructure deployed" -ForegroundColor Green

Write-Host ""
Write-Host "5. Applying Dapr components..." -ForegroundColor Yellow

# Apply Dapr components
kubectl apply -f k8s/manifests/dapr/ -n $NAMESPACE

Write-Host "✓ Dapr components applied" -ForegroundColor Green

Write-Host ""
Write-Host "6. Deploying backend..." -ForegroundColor Yellow

# Get environment variables
$DATABASE_URL = $env:DATABASE_URL ?: "postgresql://user:password@ep-xxx-xxx-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"
$JWT_SECRET = $env:JWT_SECRET ?: "change-me-in-production"
$OPENROUTER_API_KEY = $env:OPENROUTER_API_KEY ?: "your-api-key"
$SMTP_USERNAME = $env:SMTP_USERNAME ?: ""
$SMTP_PASSWORD = $env:SMTP_PASSWORD ?: ""
$FROM_EMAIL = $env:FROM_EMAIL ?: ""

# Deploy backend
helm upgrade --install "$RELEASE_NAME-backend" `
    ./k8s/helm/backend `
    --namespace $NAMESPACE `
    --set image.repository=todo-app-phase-v-backend `
    --set image.tag=latest `
    --set env.DATABASE_URL="$DATABASE_URL" `
    --set env.JWT_SECRET="$JWT_SECRET" `
    --set env.OPENROUTER_API_KEY="$OPENROUTER_API_KEY" `
    --set env.SMTP_USERNAME="$SMTP_USERNAME" `
    --set env.SMTP_PASSWORD="$SMTP_PASSWORD" `
    --set env.FROM_EMAIL="$FROM_EMAIL" `
    --wait `
    --timeout 5m

Write-Host "✓ Backend deployed" -ForegroundColor Green

Write-Host ""
Write-Host "7. Deploying frontend..." -ForegroundColor Yellow

# Deploy frontend
helm upgrade --install "$RELEASE_NAME-frontend" `
    ./k8s/helm/frontend `
    --namespace $NAMESPACE `
    --set image.repository=todo-app-phase-v-frontend `
    --set image.tag=latest `
    --set ingress.enabled=true `
    --set "ingress.hosts[0].host=todo.local" `
    --wait `
    --timeout 5m

Write-Host "✓ Frontend deployed" -ForegroundColor Green

Write-Host ""
Write-Host "8. Waiting for all pods to be ready..." -ForegroundColor Yellow

Start-Sleep -Seconds 10

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Services deployed:" -ForegroundColor Yellow
kubectl get services -n $NAMESPACE

Write-Host ""
Write-Host "Pods status:" -ForegroundColor Yellow
kubectl get pods -n $NAMESPACE

Write-Host ""
Write-Host "Access your application:" -ForegroundColor Yellow
Write-Host "  - Frontend: http://todo.local (add to hosts: 127.0.0.1 todo.local)"
Write-Host "  - Backend API: http://localhost:7860"
Write-Host "  - Dashboard: minikube dashboard -p $PROFILE"

Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  - View logs: kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=todo-backend -f"
Write-Host "  - Port forward: kubectl port-forward -n $NAMESPACE svc/todo-backend 7860:7860"
Write-Host "  - Delete: helm uninstall todo-app-backend todo-app-frontend infrastructure -n $NAMESPACE"
Write-Host ""
