# 🎯 Deployment Quick Start

## ✅ Files Created

Your project now has everything needed for Docker and Kubernetes deployment:

### Docker Files
- ✅ `backend/Dockerfile` - Backend container (FastAPI, port 7860)
- ✅ `frontend/Dockerfile` - Frontend container (Next.js, port 3000)
- ✅ `backend/.dockerignore` - Build exclusions
- ✅ `frontend/.dockerignore` - Build exclusions

### Build Scripts
- ✅ `build-docker-images.ps1` - PowerShell build script
- ✅ `build-docker-images.sh` - Bash build script

### Documentation
- ✅ `DEPLOYMENT_SUMMARY.md` - **START HERE** - Complete overview
- ✅ `DOCKER_BUILD_GUIDE.md` - Detailed Docker instructions
- ✅ `KUBERNETES_DEPLOYMENT_GUIDE.md` - K8s + Oracle OKE guide

### Kubernetes Configs
- ✅ `k8s/backend-deployment.yaml` - Updated to port 7860
- ✅ `k8s/frontend-deployment.yaml` - Frontend deployment
- ✅ `k8s/namespace.yaml` - Namespace definition
- ✅ `k8s/kafka-cluster.yaml` - Kafka cluster (Strimzi)
- ✅ `k8s/secrets.yaml` - Database secrets
- ✅ `dapr/components/kubernetes-components.yaml` - Dapr components

---

## 🚀 Build Docker Images

### Option 1: Use Build Script (Recommended)

```powershell
# Windows PowerShell
cd D:\Hackathon\todo-app-phase-V
.\build-docker-images.ps1
```

### Option 2: Manual Build Commands

```powershell
# Backend image
cd D:\Hackathon\todo-app-phase-V\backend
docker build -t todo-backend:latest .

# Frontend image
cd D:\Hackathon\todo-app-phase-V\frontend
docker build -t todo-frontend:latest .

# Verify
docker images | Select-String "todo-"
```

### ⚠️ If Build Fails

**Issue: Network errors or "no such host"**
- Check internet connection
- Restart Docker Desktop
- Try again later

**Issue: Docker Desktop not responding**
- Restart Docker Desktop
- Run: `docker system prune` (after restart)
- Try build again

**Issue: Port conflicts**
- Stop conflicting services
- Or use different ports: `-p 3001:3000`

---

## 📦 Deployment Options

### Option A: Local Testing (Docker Compose)

**Fastest way to test locally**

```powershell
# Start all services
docker-compose up -d

# Check status
docker ps

# Access application
# Frontend: http://localhost:3000
# Backend: http://localhost:8001
# Health: http://localhost:8001/health

# View logs
docker logs -f todo-backend
docker logs -f todo-frontend

# Stop
docker-compose down
```

---

### Option B: Minikube (Local Kubernetes)

**Test Kubernetes + Dapr locally**

```powershell
# 1. Start Minikube
minikube start --cpus=4 --memory=4096

# 2. Install Dapr
dapr init -k

# 3. Load images
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# 4. Deploy namespace
kubectl apply -f k8s/namespace.yaml

# 5. Deploy Dapr components
kubectl apply -f dapr/components/kubernetes-components.yaml -n todo-app

# 6. Deploy secrets (edit first with your DB credentials)
# Edit k8s/secrets.yaml with your Neon DB connection string
kubectl apply -f k8s/secrets.yaml -n todo-app

# 7. Deploy application
kubectl apply -f k8s/backend-deployment.yaml -n todo-app
kubectl apply -f k8s/frontend-deployment.yaml -n todo-app

# 8. Check status
kubectl get pods -n todo-app
kubectl get deployments -n todo-app

# 9. Access application
minikube service todo-frontend -n todo-app

# Or port forward
kubectl port-forward svc/todo-frontend 3000:3000 -n todo-app
```

---

### Option C: Oracle OKE (Cloud - Always Free)

**Production deployment on Oracle Cloud**

#### Prerequisites
1. Oracle Cloud account (https://www.oracle.com/cloud/free/)
2. OCI CLI installed: `choco install oracle-oci-cli`
3. Configure OCI: `oci setup config`

#### Steps

```powershell
# 1. Create OKE Cluster via Oracle Cloud Console
# Console → Kubernetes Clusters → Create Cluster
# Use "Quick Create" for simplicity

# 2. Download kubeconfig
oci ce cluster create-kubeconfig `
  --cluster-id <YOUR_CLUSTER_OCID> `
  --file $HOME\.kube\config `
  --region us-ashburn-1

# 3. Verify connection
kubectl get nodes

# 4. Push images to Oracle Registry
docker login registry.oraclecloud.io
docker tag todo-backend:latest registry.oraclecloud.io/YOUR_NAMESPACE/todo-backend:latest
docker tag todo-frontend:latest registry.oraclecloud.io/YOUR_NAMESPACE/todo-frontend:latest
docker push registry.oraclecloud.io/YOUR_NAMESPACE/todo-backend:latest
docker push registry.oraclecloud.io/YOUR_NAMESPACE/todo-frontend:latest

# 5. Update deployment YAML files
# Edit k8s/backend-deployment.yaml - change image to your Oracle registry URL
# Edit k8s/frontend-deployment.yaml - change image to your Oracle registry URL

# 6. Deploy to OKE
kubectl apply -f k8s/namespace.yaml
dapr init -k
kubectl apply -f dapr/components/kubernetes-components.yaml -n todo-app
kubectl apply -f k8s/secrets.yaml -n todo-app
kubectl apply -f k8s/backend-deployment.yaml -n todo-app
kubectl apply -f k8s/frontend-deployment.yaml -n todo-app

# 7. Expose via LoadBalancer
kubectl expose deployment todo-frontend `
  --type=LoadBalancer `
  --port=80 `
  --target-port=3000 -n todo-app

# 8. Get external IP (wait 2-5 minutes)
kubectl get svc -n todo-app

# Application accessible at: http://EXTERNAL-IP
```

---

## 🔧 Alternative: Azure AKS

```powershell
# 1. Install Azure CLI
choco install azure-cli

# 2. Login
az login

# 3. Create AKS cluster
az aks create `
  --resource-group todo-app-rg `
  --name todo-app-aks `
  --node-count 2

# 4. Get credentials
az aks get-credentials --resource-group todo-app-rg --name todo-app-aks

# 5. Deploy (same as Oracle OKE steps 5-8)
```

---

## 🧪 Testing After Deployment

### Test Health Endpoints

```powershell
# Get external IP (for cloud deployment)
$EXTERNAL_IP = kubectl get svc todo-frontend-lb -n todo-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Test backend health
curl http://$EXTERNAL_IP/health

# Test frontend health
curl http://$EXTERNAL_IP/health
```

### Create a Task

```powershell
curl -X POST "http://$EXTERNAL_IP/api/v1/todos/" `
  -H "Content-Type: application/json" `
  -d '{
    "title": "Test from Kubernetes",
    "description": "Testing deployment",
    "priority": "high"
  }'
```

### Verify Kafka Events

```powershell
# Port forward Kafka
kubectl port-forward svc/todo-kafka-kafka-bootstrap 9092:9092 -n todo-app

# In another terminal, consume events
docker run --rm -it -e BOOTSTRAP_SERVERS=host.docker.internal:9092 `
  confluentinc/cp-kafka:7.4.0 `
  kafka-console-consumer --bootstrap-server host.docker.internal:9092 `
  --topic todo-events --from-beginning
```

---

## 📊 Monitoring

### Dapr Dashboard

```powershell
kubectl port-forward svc/dapr-dashboard 8080:8080 -n dapr-system
# Visit: http://localhost:8080
```

### Kubernetes Logs

```powershell
# Backend logs
kubectl logs -f deployment/todo-backend -n todo-app

# Frontend logs
kubectl logs -f deployment/todo-frontend -n todo-app

# Dapr sidecar logs
kubectl logs -f deployment/todo-backend -c daprd -n todo-app
```

---

## 🛠️ Troubleshooting

### Docker Build Issues

**Problem: Build fails with network error**
```powershell
# Check Docker Desktop status
docker info

# Restart Docker Desktop
# Try build again
```

**Problem: No space left on device**
```powershell
# Clean up Docker
docker system prune -a --volumes
```

### Kubernetes Deployment Issues

**Problem: Pods in ImagePullBackOff**
```powershell
# Check pod details
kubectl describe pod <pod-name> -n todo-app

# Verify image names in deployment YAML
# Check registry credentials if using private registry
```

**Problem: LoadBalancer stuck in Pending**
```powershell
# Check service events
kubectl describe svc todo-frontend-lb -n todo-app

# Alternative: Use NodePort
kubectl expose deployment todo-frontend --type=NodePort --port=3000 -n todo-app
kubectl get svc -n todo-app
# Access via: http://NODE_PUBLIC_IP:NODEPORT
```

**Problem: Dapr sidecar not injected**
```powershell
# Check annotations
kubectl get pod <pod-name> -n todo-app -o yaml | grep dapr

# Re-annotate
kubectl annotate pod <pod-name> dapr.io/enabled=true -n todo-app --overwrite

# Restart deployment
kubectl rollout restart deployment/todo-backend -n todo-app
```

---

## 📚 Complete Documentation

| Document | When to Use |
|----------|-------------|
| **DEPLOYMENT_SUMMARY.md** | Start here for overview |
| **DOCKER_BUILD_GUIDE.md** | Building Docker images |
| **KUBERNETES_DEPLOYMENT_GUIDE.md** | Deploying to K8s + Oracle OKE |
| **PHASE_V_DEPLOYMENT.md** | Original Phase-V guide |
| **README.md** | Project overview |

---

## ✅ Checklist

### Before Building
- [ ] Docker Desktop installed and running
- [ ] Internet connection stable
- [ ] Disk space available (~3GB)

### Before Kubernetes
- [ ] Docker images built successfully
- [ ] kubectl installed
- [ ] Minikube or cloud cluster ready
- [ ] Dapr CLI installed

### Before Cloud (Oracle OKE)
- [ ] Oracle Cloud account created
- [ ] OCI CLI configured
- [ ] OKE cluster created
- [ ] Images pushed to registry
- [ ] Database secrets configured

---

## 🎯 Next Steps

1. **Build images** using `.\build-docker-images.ps1`
2. **Test locally** with Docker Compose
3. **Deploy to Minikube** for K8s testing
4. **Deploy to Oracle OKE** for production

---

**Need help?** Check the detailed guides:
- Docker issues → `DOCKER_BUILD_GUIDE.md`
- Kubernetes issues → `KUBERNETES_DEPLOYMENT_GUIDE.md`
- General deployment → `DEPLOYMENT_SUMMARY.md`

**Ready to deploy!** 🚀
