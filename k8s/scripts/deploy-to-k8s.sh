#!/bin/bash
# Deploy Todo App to Minikube
# This script builds images and deploys everything to Kubernetes

set -e

echo "========================================="
echo "Todo App - Kubernetes Deployment"
echo "========================================="

# Configuration
PROFILE="todo-app"
NAMESPACE="todo-app"
RELEASE_NAME="todo-app"

echo ""
echo "1. Building Docker images..."

# Build backend image
echo "Building backend image..."
docker-compose build backend

# Build frontend image
echo "Building frontend image..."
docker-compose build frontend

echo "✓ Docker images built"

echo ""
echo "2. Loading images into Minikube..."

# Load images into Minikube
minikube image load todo-app-phase-v-backend:latest -p $PROFILE
minikube image load todo-app-phase-v-frontend:latest -p $PROFILE

echo "✓ Images loaded into Minikube"

echo ""
echo "3. Creating namespace..."

# Create namespace if it doesn't exist
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

echo "✓ Namespace created: $NAMESPACE"

echo ""
echo "4. Deploying infrastructure (Kafka, Redis, Zookeeper)..."

# Deploy infrastructure using Helm
helm upgrade --install infrastructure \
    ./k8s/helm/infrastructure \
    --namespace $NAMESPACE \
    --create-namespace \
    --wait \
    --timeout 10m

echo "✓ Infrastructure deployed"

echo ""
echo "5. Applying Dapr components..."

# Apply Dapr components
kubectl apply -f k8s/manifests/dapr/ -n $NAMESPACE

echo "✓ Dapr components applied"

echo ""
echo "6. Deploying backend..."

# Deploy backend with environment variables
helm upgrade --install $RELEASE_NAME-backend \
    ./k8s/helm/backend \
    --namespace $NAMESPACE \
    --set image.repository=todo-app-phase-v-backend \
    --set image.tag=latest \
    --set env.DATABASE_URL="${DATABASE_URL:-postgresql://user:password@ep-xxx-xxx-xxx-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require}" \
    --set env.JWT_SECRET="${JWT_SECRET:-change-me-in-production}" \
    --set env.OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-your-api-key}" \
    --set env.SMTP_USERNAME="${SMTP_USERNAME:-}" \
    --set env.SMTP_PASSWORD="${SMTP_PASSWORD:-}" \
    --set env.FROM_EMAIL="${FROM_EMAIL:-}" \
    --wait \
    --timeout 5m

echo "✓ Backend deployed"

echo ""
echo "7. Deploying frontend..."

# Deploy frontend
helm upgrade --install $RELEASE_NAME-frontend \
    ./k8s/helm/frontend \
    --namespace $NAMESPACE \
    --set image.repository=todo-app-phase-v-frontend \
    --set image.tag=latest \
    --set ingress.enabled=true \
    --set ingress.hosts[0].host=todo.local \
    --wait \
    --timeout 5m

echo "✓ Frontend deployed"

echo ""
echo "8. Waiting for all pods to be ready..."

kubectl wait --for=condition=ready pod -l app.kubernetes.io/part-of=todo-app -n $NAMESPACE --timeout=300s || true

echo ""
echo "========================================="
echo "✅ Deployment Complete!"
echo "========================================="

echo ""
echo "Services deployed:"
kubectl get services -n $NAMESPACE

echo ""
echo "Pods status:"
kubectl get pods -n $NAMESPACE

echo ""
echo "Access your application:"
echo "  - Frontend: http://todo.local (add to hosts file: 127.0.0.1 todo.local)"
echo "  - Backend API: http://localhost:7860"
echo "  - Kubernetes Dashboard: minikube dashboard -p $PROFILE"

echo ""
echo "Useful commands:"
echo "  - View logs: kubectl logs -n $NAMESPACE -l app.kubernetes.io/name=todo-backend -f"
echo "  - Port forward backend: kubectl port-forward -n $NAMESPACE svc/todo-backend 7860:7860"
echo "  - Port forward frontend: kubectl port-forward -n $NAMESPACE svc/todo-frontend 3000:3000"
echo "  - Delete deployment: helm uninstall $RELEASE_NAME-backend $RELEASE_NAME-frontend infrastructure -n $NAMESPACE"
echo ""
