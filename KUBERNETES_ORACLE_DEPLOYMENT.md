# Oracle Cloud Infrastructure (OCI) Deployment Guide
# OKE (Oracle Kubernetes Engine) + Dapr + Kafka

This guide covers deploying the Todo App to Oracle Cloud Infrastructure using OKE.

## 📋 Prerequisites

### OCI Requirements
1. **Oracle Cloud Account** - [Sign up](https://www.oracle.com/cloud/free/)
2. **OCI CLI** installed and configured
3. **kubectl** configured for OKE
4. **Helm** v3.x
5. **Dapr CLI**
6. **Docker**

### Install OCI CLI

**Windows:**
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.ps1'))"
```

**Linux/macOS:**
```bash
curl -o install.sh https://raw.githubusercontent.com/oracle/oci-cli/master/scripts/install/install.sh
bash install.sh
```

**Configure OCI CLI:**
```bash
oci setup config
```

---

## 🚀 Deployment Steps

### Step 1: Create OKE Cluster

#### Option A: Using OCI Console

1. Go to **Kubernetes Clusters (OKE)** in OCI Console
2. Click **Create Cluster**
3. Choose **Quick Create** for simplicity
4. Configure:
   - **Cluster Name**: todo-app-cluster
   - **Kubernetes Version**: 1.28.x or latest
   - **Node Pool**: 
     - Shape: VM.Standard.E4.Flex (4 OCPU, 16GB RAM minimum)
     - Node Count: 3 (for HA)
   - **Networking**: Create new VCN
5. Click **Create Cluster**

#### Option B: Using OCI CLI

```bash
# Create VCN
oci network vcn create \
  --compartment-id <YOUR_COMPARTMENT_ID> \
  --display-name todo-app-vcn \
  --cidr-blocks 10.0.0.0/16

# Create OKE Cluster
oci ce cluster create \
  --compartment-id <YOUR_COMPARTMENT_ID> \
  --name todo-app-cluster \
  --kubernetes-version v1.28.5 \
  --options '{"serviceLbSubnetIds":[],"skipServiceLbSet":true}' \
  --vcn-id <YOUR_VCN_ID>
```

### Step 2: Configure kubectl

```bash
# Get kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id <CLUSTER_OCID> \
  --file $HOME/.kube/config \
  --region <YOUR_REGION> \
  --token-version 2.0.0

# Or use OCI Console: Click "Access Cluster" and copy the command
```

**Verify connection:**
```bash
kubectl cluster-info
kubectl get nodes
```

---

### Step 3: Create Container Registry

#### Create OCI Registry

```bash
# Create compartment for registry (optional)
oci iam compartment create \
  --compartment-id <YOUR_COMPARTMENT_ID> \
  --name todo-app-registry \
  --description "Todo App Container Registry"

# Create auth token for Docker
oci iam auth-token create \
  --user-id <YOUR_USER_OCID> \
  --description "Docker Registry Token"
```

#### Login to OCI Registry

```bash
# Get your tenancy OCID
oci iam tenancy get

# Login to registry
docker login -u '<YOUR_TENANCY_NAMESPACE>/<YOUR_USERNAME>' <REGION>.ocir.io
# Use auth token as password
```

---

### Step 4: Build and Push Docker Images

```bash
# Tag backend image
docker tag todo-app-phase-v-backend:latest <REGION>.ocir.io/<TENANCY_NAMESPACE>/todo-app/backend:latest

# Tag frontend image
docker tag todo-app-phase-v-frontend:latest <REGION>.ocir.io/<TENANCY_NAMESPACE>/todo-app/frontend:latest

# Push images
docker push <REGION>.ocir.io/<TENANCY_NAMESPACE>/todo-app/backend:latest
docker push <REGION>.ocir.io/<TENANCY_NAMESPACE>/todo-app/frontend:latest
```

**Verify:**
```bash
# List images in registry
oci artifacts container image list \
  --compartment-id <YOUR_COMPARTMENT_ID> \
  --display-name todo-app/backend
```

---

### Step 5: Create Kubernetes Secrets

#### Create Registry Secret

```bash
kubectl create secret docker-registry ocir-secret \
  --docker-server=<REGION>.ocir.io \
  --docker-username='<TENANCY_NAMESPACE>/<USERNAME>' \
  --docker-password='<AUTH_TOKEN>' \
  --docker-email='your-email@example.com' \
  -n todo-app
```

#### Create Application Secrets

```bash
kubectl create secret generic todo-app-secrets \
  --from-literal=DATABASE_URL='your-database-url' \
  --from-literal=JWT_SECRET='your-jwt-secret' \
  --from-literal=OPENROUTER_API_KEY='your-api-key' \
  --from-literal=SMTP_USERNAME='your-smtp-username' \
  --from-literal=SMTP_PASSWORD='your-smtp-password' \
  --from-literal=FROM_EMAIL='your-from-email' \
  -n todo-app
```

---

### Step 6: Install Dapr on OKE

```bash
# Install Dapr with Helm
helm repo add dapr https://dapr.github.io/helm-charts/
helm repo update

helm install dapr dapr/dapr \
  --version=1.12.0 \
  --namespace dapr-system \
  --create-namespace \
  --wait
```

**Verify:**
```bash
kubectl get pods -n dapr-system
```

---

### Step 7: Deploy Infrastructure

```bash
# Create namespace
kubectl create namespace todo-app

# Deploy Kafka, Zookeeper, Redis
helm upgrade --install infrastructure ./k8s/helm/infrastructure \
  --namespace todo-app \
  --create-namespace \
  --set kafka.persistence.size=10Gi \
  --set zookeeper.persistence.size=5Gi \
  --set redis.persistence.size=5Gi \
  --wait
```

---

### Step 8: Apply Dapr Components

```bash
# Apply Dapr components
kubectl apply -f k8s/manifests/dapr/ -n todo-app

# Verify
kubectl get components -n todo-app
```

---

### Step 9: Deploy Applications

#### Deploy Backend

```bash
helm upgrade --install todo-backend ./k8s/helm/backend \
  --namespace todo-app \
  --set image.repository=<REGION>.ocir.io/<TENANCY_NAMESPACE>/todo-app/backend \
  --set image.tag=latest \
  --set imagePullSecrets[0].name=ocir-secret \
  --set replicaCount=2 \
  --set resources.requests.memory="512Mi" \
  --set resources.requests.cpu="250m" \
  --set resources.limits.memory="1Gi" \
  --set resources.limits.cpu="500m" \
  --set env.DATABASE_URL='your-database-url' \
  --set env.JWT_SECRET='your-jwt-secret' \
  --set env.OPENROUTER_API_KEY='your-api-key' \
  --wait
```

#### Deploy Frontend

```bash
helm upgrade --install todo-frontend ./k8s/helm/frontend \
  --namespace todo-app \
  --set image.repository=<REGION>.ocir.io/<TENANCY_NAMESPACE>/todo-app/frontend \
  --set image.tag=latest \
  --set imagePullSecrets[0].name=ocir-secret \
  --set replicaCount=2 \
  --set ingress.enabled=true \
  --set ingress.className=nginx \
  --set ingress.hosts[0].host=todo-app.<YOUR_DOMAIN> \
  --wait
```

---

### Step 10: Install NGINX Ingress Controller

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.type=LoadBalancer \
  --set controller.autoscaling.enabled=true \
  --set controller.autoscaling.minReplicas=2 \
  --wait
```

**Get Load Balancer IP:**
```bash
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

---

### Step 11: Configure DNS

1. Get the Load Balancer IP from Step 10
2. Create DNS A record:
   - **Host**: todo-app
   - **Value**: <LOAD_BALANCER_IP>
   - **TTL**: 3600

---

### Step 12: Enable SSL/TLS (Optional but Recommended)

#### Install cert-manager

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.2/cert-manager.yaml
```

#### Create ClusterIssuer

```yaml
# k8s/manifests/letsencrypt-clusterissuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

```bash
kubectl apply -f k8s/manifests/letsencrypt-clusterissuer.yaml
```

#### Update Frontend Ingress with TLS

```bash
helm upgrade --install todo-frontend ./k8s/helm/frontend \
  --namespace todo-app \
  --set ingress.enabled=true \
  --set ingress.className=nginx \
  --set ingress.hosts[0].host=todo-app.<YOUR_DOMAIN> \
  --set ingress.tls[0].secretName=todo-app-tls \
  --set ingress.tls[0].hosts[0]=todo-app.<YOUR_DOMAIN> \
  --wait
```

---

## 🔍 Verify Deployment

### Check All Resources

```bash
# Pods
kubectl get pods -n todo-app

# Services
kubectl get services -n todo-app

# Ingress
kubectl get ingress -n todo-app

# Dapr Components
kubectl get components -n todo-app
```

### Test Application

```bash
# Test backend
curl https://todo-app.<YOUR_DOMAIN>/api/health

# Test frontend
curl https://todo-app.<YOUR_DOMAIN>/health
```

---

## 📊 Monitoring and Logging

### Install Metrics Server

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### View Resource Usage

```bash
kubectl top nodes
kubectl top pods -n todo-app
```

### Install Prometheus and Grafana (Optional)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

---

## 🗑️ Cleanup

### Delete Application

```bash
# Remove Helm releases
helm uninstall todo-backend -n todo-app
helm uninstall todo-frontend -n todo-app
helm uninstall infrastructure -n todo-app

# Delete namespace
kubectl delete namespace todo-app

# Delete Dapr
helm uninstall dapr -n dapr-system
```

### Delete OKE Cluster

**Warning:** This will delete all resources!

```bash
oci ce cluster delete --cluster-id <CLUSTER_OCID>
```

### Delete Container Registry Images

```bash
oci artifacts container image delete --image-id <IMAGE_OCID>
```

---

## 💰 Cost Optimization

### Recommended Resource Limits

| Component | CPU Request | CPU Limit | Memory Request | Memory Limit |
|-----------|-------------|-----------|----------------|--------------|
| Backend   | 250m        | 500m      | 512Mi          | 1Gi          |
| Frontend  | 100m        | 200m      | 256Mi          | 512Mi        |
| Kafka     | 500m        | 1000m     | 1Gi            | 2Gi          |
| Redis     | 100m        | 200m      | 256Mi          | 512Mi        |

### Use Spot Instances

```bash
# Create node pool with spot instances
oci ce node-pool create \
  --cluster-id <CLUSTER_OCID> \
  --name spot-pool \
  --node-shape VM.Standard.E4.Flex \
  --node-config-details '{"placementConfigs":[{"subnetId":"<SUBNET_OCID>"}]}' \
  --node-source-details '{"sourceType":"IMAGE","imageId":"<IMAGE_OCID>}' \
  --size 3
```

---

## 🔧 Troubleshooting

### Image Pull Errors

```bash
# Check secret
kubectl get secret ocir-secret -n todo-app -o yaml

# Verify registry access
docker pull <REGION>.ocir.io/<TENANCY_NAMESPACE>/todo-app/backend:latest
```

### Load Balancer Issues

```bash
# Check service events
kubectl describe svc -n todo-app todo-backend

# Check ingress controller
kubectl get pods -n ingress-nginx
```

### Dapr Sidecar Issues

```bash
# Check sidecar injection
kubectl get pod -n todo-app -o jsonpath='{.items[*].metadata.annotations}'

# Check Dapr logs
kubectl logs -n todo-app <pod-name> -c daprd
```

---

## 📝 Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│                    Oracle Cloud (OCI)                       │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Oracle Kubernetes Engine (OKE)              │  │
│  │                                                        │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │              Load Balancer                      │  │  │
│  │  │           (Public IP: 443, 80)                  │  │  │
│  │  └───────────────────┬───────────────────────────┘  │  │
│  │                      │                               │  │
│  │  ┌───────────────────▼───────────────────────────┐  │  │
│  │  │           NGINX Ingress Controller              │  │  │
│  │  └───────────────────┬───────────────────────────┘  │  │
│  │                      │                               │  │
│  │  ┌───────────────────▼───────────────────────────┐  │  │
│  │  │           todo-app Namespace                    │  │  │
│  │  │                                                │  │  │
│  │  │  ┌──────────────┐      ┌──────────────┐       │  │  │
│  │  │  │   Frontend   │─────▶│    Backend   │       │  │  │
│  │  │  │  (Next.js)   │      │   (FastAPI)  │       │  │  │
│  │  │  │   x2 pods    │      │    x2 pods   │       │  │  │
│  │  │  └──────────────┘      └──────┬───────┘       │  │  │
│  │  │                                │                │  │  │
│  │  │                          ┌─────┴─────┐         │  │  │
│  │  │                          │   Dapr    │         │  │  │
│  │  │                          │ Sidecars  │         │  │  │
│  │  │                          └─────┬─────┘         │  │  │
│  │  │                                │                │  │  │
│  │  │         ┌──────────────────────┼────────────┐  │  │  │
│  │  │         │                      │            │  │  │  │
│  │  │  ┌──────▼──────┐      ┌───────▼──────┐    │  │  │  │
│  │  │  │    Kafka    │      │    Redis     │    │  │  │  │
│  │  │  │  (Stateful) │      │  (Stateful)  │    │  │  │  │
│  │  │  └─────────────┘      └──────────────┘    │  │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌────────────────────────────────────────────────────┐│
│  │              External Services                      ││
│  │  • Neon PostgreSQL (Cloud)                         ││
│  │  • OpenRouter API                                   ││
│  │  • SMTP Email Service                               ││
│  └────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

---

## 📚 Additional Resources

- [OCI Documentation](https://docs.oracle.com/en-us/iaas/)
- [OKE Best Practices](https://docs.oracle.com/en-us/iaas/Content/ContEng/Concepts/contengoverview.htm)
- [OCI Container Registry](https://docs.oracle.com/en-us/iaas/Content/Registry/Concepts/registryoverview.htm)
- [Dapr on Kubernetes](https://docs.dapr.io/operations/hosting/kubernetes/)

---

**Last Updated:** 2026-03-18  
**Author:** Naseer Ahmed
