# ☁️ Kubernetes Deployment Guide - Oracle OKE

## Overview
This guide covers deploying the Todo App to Oracle Kubernetes Engine (OKE) with Dapr, Kafka, and all supporting services.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  ORACLE KUBERNETES ENGINE (OKE)                  │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐  │
│  │   Frontend   │    │   Backend    │    │   Kafka Cluster  │  │
│  │  Pod + Dapr  │───▶│  Pod + Dapr  │───▶│   (Strimzi)      │  │
│  │  (3000)      │    │  (7860)      │    │                  │  │
│  └──────────────┘    └──────┬───────┘    └──────────────────┘  │
│                             │                                   │
│                             ▼                                   │
│                      ┌─────────────┐                           │
│                      │  Neon DB    │ (External PostgreSQL)     │
│                      │  (Serverless)│                          │
│                      └─────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

### 1. Oracle Cloud Account

- Sign up at: https://www.oracle.com/cloud/free/
- **Always Free Tier**: 4 OCPUs, 24GB RAM, 200GB storage

### 2. Install Required Tools

```powershell
# Install OCI CLI (Oracle Cloud Infrastructure)
choco install oracle-oci-cli

# Install kubectl
choco install kubernetes-cli

# Install Helm (optional)
choco install kubernetes-helm

# Install Dapr CLI
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
```

### 3. Verify Installations

```powershell
oci --version
kubectl version --client
dapr --version
docker --version
```

---

## 🚀 Step-by-Step Deployment

### Phase 1: Oracle Cloud Setup

#### 1.1 Generate API Keys

```powershell
# Create directory for keys
mkdir $HOME\.oci
cd $HOME\.oci

# Generate private key
openssl genrsa -out oci_api_key.pem 2048

# Set permissions (Linux/Mac only)
chmod 600 oci_api_key.pem

# Generate public key
openssl rsa -pubout -in oci_api_key.pem -out oci_api_key_public.pem

# Upload public key to Oracle Cloud Console:
# Console → Profile → User Settings → API Keys → Add Public Key
```

#### 1.2 Configure OCI CLI

```powershell
oci setup config
```

**You'll be prompted for:**
- User OCID: (from Oracle Console → Profile → User Settings)
- Fingerprint: (from uploaded API key)
- Tenancy OCID: (from Console → Administration → Tenancy Details)
- Region: e.g., `us-ashburn-1`

**Config file location:** `$HOME\.oci\config`

**Example config:**
```ini
[DEFAULT]
user=ocid1.user.oc1..xxxxxx
fingerprint=xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx
tenancy=ocid1.tenancy.oc1..xxxxxx
region=us-ashburn-1
key_file=~/.oci/oci_api_key.pem
```

---

### Phase 2: Create OKE Cluster

#### 2.1 Create Cluster via Console (Recommended)

1. **Navigate to:** Oracle Cloud Console → Kubernetes Clusters (OKE)
2. **Click:** "Create Cluster"
3. **Select:** "Quick Create" (simpler) or "Custom Create" (more control)
4. **Configure:**
   - **Cluster Name:** `todo-app-cluster`
   - **Kubernetes Version:** Latest available (1.28+)
   - **Shape:** VM.Standard.E2.1.Micro (Always Free)
   - **Node Count:** 2-3 nodes
5. **Click:** "Create Cluster"

#### 2.2 Create Cluster via CLI (Advanced)

```powershell
# Create VCN (Virtual Cloud Network)
oci network vcn create \
  --compartment-id <YOUR_COMPARTMENT_OCID> \
  --display-name todo-app-vcn \
  --cidr-blocks '["10.0.0.0/16"]' \
  --dns-label todoappvcn

# Create OKE Cluster
oci ce cluster create \
  --compartment-id <YOUR_COMPARTMENT_OCID> \
  --vcn-id <YOUR_VCN_OCID> \
  --kubernetes-version "v1.28.5" \
  --name todo-app-cluster \
  --endpoint-config-type PUBLIC_ENDPOINTS \
  --options '{"serviceLbSubnetIds": [], "skip-service-lb-subnet-creation": true}'
```

#### 2.3 Download Kubeconfig

```powershell
# Create .kube directory
mkdir $HOME\.kube

# Download kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id <YOUR_CLUSTER_OCID> \
  --file $HOME\.kube\config \
  --region us-ashburn-1 \
  --token-version 2.0.0

# Verify connection
kubectl get nodes
```

**Expected output:**
```
NAME          STATUS   ROLES   AGE   VERSION
10.0.10.2     Ready    node    5m    v1.28.5
10.0.10.3     Ready    node    5m    v1.28.5
```

---

### Phase 3: Build and Push Docker Images

#### 3.1 Build Images

```powershell
cd D:\Hackathon\todo-app-phase-V

# Build backend
docker build -t todo-backend:latest ./backend

# Build frontend
docker build -t todo-frontend:latest ./frontend

# Verify
docker images | Select-String "todo-"
```

#### 3.2 Push to Oracle Container Registry

```powershell
# Login to Oracle Registry
docker login registry.oraclecloud.io

# Tag images (replace YOUR_NAMESPACE with your Oracle namespace)
docker tag todo-backend:latest registry.oraclecloud.io/YOUR_NAMESPACE/todo-backend:latest
docker tag todo-frontend:latest registry.oraclecloud.io/YOUR_NAMESPACE/todo-frontend:latest

# Push images
docker push registry.oraclecloud.io/YOUR_NAMESPACE/todo-backend:latest
docker push registry.oraclecloud.io/YOUR_NAMESPACE/todo-frontend:latest
```

#### 3.3 Alternative: Push to Docker Hub

```powershell
# Login to Docker Hub
docker login

# Tag images
docker tag todo-backend:latest yourusername/todo-backend:latest
docker tag todo-frontend:latest yourusername/todo-frontend:latest

# Push
docker push yourusername/todo-backend:latest
docker push yourusername/todo-frontend:latest
```

---

### Phase 4: Deploy to Kubernetes

#### 4.1 Create Namespace

```powershell
kubectl apply -f k8s/namespace.yaml
```

**Expected:**
```
namespace/todo-app created
```

#### 4.2 Install Dapr

```powershell
dapr init -k

# Verify
kubectl get pods -n dapr-system
```

**Expected:**
```
NAME                          READY   STATUS    RESTARTS   AGE
dapr-dashboard-xxxxx          1/1     Running   0          2m
dapr-operator-xxxxx           1/1     Running   0          2m
dapr-placement-server-0       1/1     Running   0          2m
dapr-sentry-xxxxx             1/1     Running   0          2m
dapr-sidecar-injector-xxxxx   1/1     Running   0          2m
```

#### 4.3 Deploy Kafka (Strimzi)

```powershell
# Install Strimzi Operator
kubectl apply -f https://strimzi.io/install/latest?namespace=todo-app -n todo-app

# Wait for operator
kubectl wait --for=condition=Available deployment/strimzi-cluster-operator -n todo-app --timeout=300s

# Deploy Kafka cluster
kubectl apply -f k8s/kafka-cluster.yaml -n todo-app

# Verify
kubectl get pods -n todo-app -l app.kubernetes.io/name=kafka
```

#### 4.4 Deploy Dapr Components

```powershell
# Deploy Dapr components (pubsub, statestore, secrets)
kubectl apply -f dapr/components/kubernetes-components.yaml -n todo-app

# Verify
kubectl get components.dapr.io -n todo-app
```

**Expected:**
```
NAME             AGE
kafka-pubsub     30s
statestore       30s
kubernetes-secrets 30s
```

#### 4.5 Create Database Secrets

**Edit `k8s/secrets.yaml` with your Neon DB connection string:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: todo-app
type: Opaque
stringData:
  connection-string: "postgresql://user:password@host.neon.tech/dbname?sslmode=require"
```

**Apply:**
```powershell
kubectl apply -f k8s/secrets.yaml -n todo-app
```

#### 4.6 Update Deployment Images

**Edit `k8s/backend-deployment.yaml`:**
```yaml
spec:
  containers:
  - name: backend
    image: registry.oraclecloud.io/YOUR_NAMESPACE/todo-backend:latest  # Update this
```

**Edit `k8s/frontend-deployment.yaml`:**
```yaml
spec:
  containers:
  - name: frontend
    image: registry.oraclecloud.io/YOUR_NAMESPACE/todo-frontend:latest  # Update this
```

#### 4.7 Deploy Application

```powershell
# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml -n todo-app

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml -n todo-app

# Verify deployments
kubectl get deployments -n todo-app
kubectl get pods -n todo-app
```

**Expected:**
```
NAME           READY   UP-TO-DATE   AVAILABLE   AGE
todo-backend   2/2     2            2           30s
todo-frontend  2/2     2            2           30s
```

---

### Phase 5: Expose Application

#### 5.1 Create LoadBalancer Service

**Create `k8s/loadbalancer.yaml`:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: todo-frontend-lb
  namespace: todo-app
spec:
  type: LoadBalancer
  selector:
    app: todo-frontend
  ports:
  - port: 80
    targetPort: 3000
    name: http
```

**Apply:**
```powershell
kubectl apply -f k8s/loadbalancer.yaml -n todo-app
```

#### 5.2 Get External IP

```powershell
kubectl get svc todo-frontend-lb -n todo-app
```

**Expected (wait 2-5 minutes):**
```
NAME               TYPE           CLUSTER-IP     EXTERNAL-IP      PORT(S)        AGE
todo-frontend-lb   LoadBalancer   10.96.xxx.xxx   129.xxx.xxx.xxx  80:30xxx/TCP   3m
```

**Your application is now accessible at:** `http://EXTERNAL-IP`

---

### Phase 6: Verify Deployment

#### 6.1 Check Dapr Sidecars

```powershell
kubectl get pods -n todo-app -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.metadata.annotations.dapr\.io/app-id}{"\n"}{end}'
```

#### 6.2 Check Dapr Status

```powershell
dapr status -k
```

#### 6.3 View Logs

```powershell
# Backend logs
kubectl logs -f deployment/todo-backend -n todo-app

# Frontend logs
kubectl logs -f deployment/todo-frontend -n todo-app

# Dapr sidecar logs
kubectl logs -f deployment/todo-backend -c daprd -n todo-app
```

#### 6.4 Test Health Endpoints

```powershell
# Get external IP
$EXTERNAL_IP = kubectl get svc todo-frontend-lb -n todo-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

# Test backend
curl http://$EXTERNAL_IP/health

# Test frontend
curl http://$EXTERNAL_IP/health
```

---

## 🔍 Monitoring and Debugging

### Dapr Dashboard

```powershell
# Port forward Dapr dashboard
kubectl port-forward svc/dapr-dashboard 8080:8080 -n dapr-system

# Visit: http://localhost:8080
```

### Kubernetes Dashboard

```powershell
# Install metrics server (if not already installed)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Access dashboard
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
kubectl proxy

# Visit: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/proxy/
```

### Check Events

```powershell
kubectl get events -n todo-app --sort-by='.lastTimestamp'
```

---

## 🧪 Testing the Application

### Create a Task

```powershell
$EXTERNAL_IP = kubectl get svc todo-frontend-lb -n todo-app -o jsonpath='{.status.loadBalancer.ingress[0].ip}'

curl -X POST "http://$EXTERNAL_IP/api/v1/todos/" `
  -H "Content-Type: application/json" `
  -d '{
    "title": "Test Task",
    "description": "Testing from OKE",
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

## 🛠️ Troubleshooting

### Issue: Pods not starting (ImagePullBackOff)

**Solution:** Check image names and registry credentials.

```powershell
# Check pod events
kubectl describe pod <pod-name> -n todo-app

# If using private registry, create image pull secret
kubectl create secret docker-registry regcred `
  --docker-server=registry.oraclecloud.io `
  --docker-username=<your-username> `
  --docker-password=<your-password> `
  -n todo-app

# Update deployment to use imagePullSecrets
```

### Issue: LoadBalancer stuck in Pending state

**Solution:** Oracle OKE requires service gateway for LoadBalancer.

```powershell
# Check service events
kubectl describe svc todo-frontend-lb -n todo-app

# Alternative: Use NodePort
kubectl expose deployment todo-frontend --type=NodePort --port=3000 -n todo-app

# Get NodePort
kubectl get svc todo-frontend -n todo-app

# Access via node public IP: http://NODE_PUBLIC_IP:NODEPORT
```

### Issue: Dapr sidecar not injected

**Solution:** Check annotations and Dapr installation.

```powershell
# Check pod annotations
kubectl get pod <pod-name> -n todo-app -o yaml | grep dapr

# Re-apply Dapr annotations
kubectl annotate pod <pod-name> dapr.io/enabled=true -n todo-app

# Restart deployment
kubectl rollout restart deployment/todo-backend -n todo-app
```

### Issue: Cannot connect to database

**Solution:** Verify connection string and network access.

```powershell
# Check secret
kubectl get secret db-secret -n todo-app -o jsonpath='{.data.connection-string}' | base64 -d

# Test database connection from local
psql "postgresql://user:password@host.neon.tech/dbname?sslmode=require"
```

---

## 📊 Cost Optimization (Always Free Tier)

### Oracle OKE Always Free Limits

- **Compute:** 2 VM instances (1 OCPU, 6GB RAM each)
- **Storage:** 200GB total
- **Network:** No charge for ingress

### Optimization Tips

1. **Use micro instances** for non-production
2. **Scale down replicas** to 1 during development
3. **Use autoscaling** to reduce costs
4. **Monitor usage** in Oracle Cloud Console

---

## 🎯 Post-Deployment Checklist

- [ ] All pods running (`kubectl get pods -n todo-app`)
- [ ] Dapr sidecars injected
- [ ] LoadBalancer has external IP
- [ ] Application accessible via browser
- [ ] Health endpoints responding
- [ ] Kafka events being published
- [ ] Database connection working
- [ ] Dapr components healthy

---

## 📝 References

- **Oracle OKE Documentation:** https://docs.oracle.com/en-us/iaas/Content/ContEng/
- **Dapr Documentation:** https://docs.dapr.io/
- **Strimzi (Kafka):** https://strimzi.io/
- **Neon PostgreSQL:** https://neon.tech/docs/

---

**Deployment complete! Your Todo App is now running on Oracle OKE!** 🚀
