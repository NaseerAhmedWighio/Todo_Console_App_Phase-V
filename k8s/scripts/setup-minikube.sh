#!/bin/bash
# Minikube Setup Script for Todo App Phase V
# This script sets up Minikube with all required components

set -e

echo "========================================="
echo "Todo App - Minikube Setup"
echo "========================================="

# Configuration
MINIKUBE_PROFILE="todo-app"
MINIKUBE_DRIVER="docker"  # Change to 'hyperv', 'virtualbox', or 'kvm2' based on your system
MINIKUBE_CPUS=4
MINIKUBE_MEMORY=8192
MINIKUBE_DISK="20gb"
KUBERNETES_VERSION="v1.28.0"

echo ""
echo "1. Checking prerequisites..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi
echo "✓ Docker is running"

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    echo "❌ Minikube is not installed. Please install it from: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi
echo "✓ Minikube is installed (version: $(minikube version --short))"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install it from: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi
echo "✓ kubectl is installed (version: $(kubectl version --client --short 2>/dev/null || kubectl version --client))"

# Check if Helm is installed
if ! command -v helm &> /dev/null; then
    echo "❌ Helm is not installed. Please install it from: https://helm.sh/docs/intro/install/"
    exit 1
fi
echo "✓ Helm is installed (version: $(helm version --short))"

echo ""
echo "2. Starting Minikube..."

# Stop and delete existing cluster if it exists
if minikube status -p $MINIKUBE_PROFILE &> /dev/null; then
    echo "Stopping existing cluster..."
    minikube stop -p $MINIKUBE_PROFILE
fi

if minikube profile list | grep -q $MINIKUBE_PROFILE; then
    echo "Deleting existing cluster..."
    minikube delete -p $MINIKUBE_PROFILE
fi

# Start Minikube with optimized settings for local development
minikube start \
    --profile $MINIKUBE_PROFILE \
    --driver $MINIKUBE_DRIVER \
    --cpus $MINIKUBE_CPUS \
    --memory $MINIKUBE_MEMORY \
    --disk-size $MINIKUBE_DISK \
    --kubernetes-version $KUBERNETES_VERSION \
    --enable-default-cni \
    --addons=storage-provisioner \
    --wait=all \
    --timeout=10m

echo "✓ Minikube cluster started"

echo ""
echo "3. Configuring kubectl..."

# Set kubectl context to minikube
kubectl config use-context minikube-$MINIKUBE_PROFILE
echo "✓ kubectl context set to minikube-$MINIKUBE_PROFILE"

echo ""
echo "4. Enabling Minikube addons..."

# Enable useful addons
minikube addons enable ingress -p $MINIKUBE_PROFILE || true
minikube addons enable metrics-server -p $MINIKUBE_PROFILE || true
echo "✓ Minikube addons enabled"

echo ""
echo "5. Installing Dapr..."

# Install Dapr CLI if not installed
if ! command -v dapr &> /dev/null; then
    echo "Installing Dapr CLI..."
    curl -fsSL https://raw.githubusercontent.com/dapr/cli/master/install/install.sh | bash
    export PATH=$PATH:$HOME/.dapr/bin
fi

# Initialize Dapr on Kubernetes
echo "Installing Dapr on Kubernetes..."
dapr init -k --wait
echo "✓ Dapr installed"

echo ""
echo "6. Verifying installation..."

# Wait for all pods to be ready
echo "Waiting for all system pods to be ready..."
kubectl wait --for=condition=ready pod -l app=dapr-system --timeout=180s -n dapr-system || true
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=ingress-nginx --timeout=180s -n ingress-nginx || true

echo ""
echo "========================================="
echo "✅ Minikube Setup Complete!"
echo "========================================="
echo ""
echo "Cluster Info:"
minikube status -p $MINIKUBE_PROFILE
echo ""
echo "Useful commands:"
echo "  - Access Kubernetes Dashboard: minikube dashboard -p $MINIKUBE_PROFILE"
echo "  - Access Dapr Dashboard: dapr dashboard -p $MINIKUBE_PROFILE"
echo "  - View all pods: kubectl get pods -A"
echo "  - View Dapr components: kubectl get components -n default"
echo ""
echo "Next steps:"
echo "  1. Build your Docker images: docker-compose build"
echo "  2. Load images into Minikube: minikube image load todo-app-phase-v-backend:latest"
echo "  3. Deploy with Helm: helm install todo-app ./k8s/helm/backend"
echo ""
