# Minikube Setup Script for Todo App Phase V (PowerShell)
# This script sets up Minikube with all required components on Windows

$ErrorActionPreference = "Stop"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Todo App - Minikube Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Configuration
$MINIKUBE_PROFILE = "todo-app"
$MINIKUBE_DRIVER = "docker"  # Change to 'hyperv' if needed
$MINIKUBE_CPUS = 4
$MINIKUBE_MEMORY = "8192MB"
$MINIKUBE_DISK = "20gb"
$KUBERNETES_VERSION = "v1.28.0"

Write-Host ""
Write-Host "1. Checking prerequisites..." -ForegroundColor Yellow

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Check if Minikube is installed
if (Get-Command minikube -ErrorAction SilentlyContinue) {
    $minikubeVersion = minikube version --short
    Write-Host "✓ Minikube is installed (version: $minikubeVersion)" -ForegroundColor Green
} else {
    Write-Host "❌ Minikube is not installed." -ForegroundColor Red
    Write-Host "Install from: https://minikube.sigs.k8s.io/docs/start/" -ForegroundColor Yellow
    exit 1
}

# Check if kubectl is installed
if (Get-Command kubectl -ErrorAction SilentlyContinue) {
    $kubectlVersion = kubectl version --client -o json 2>$null | ConvertFrom-Json | Select-Object -ExpandProperty clientVersion | Select-Object -ExpandProperty gitVersion
    Write-Host "✓ kubectl is installed (version: $kubectlVersion)" -ForegroundColor Green
} else {
    Write-Host "❌ kubectl is not installed." -ForegroundColor Red
    Write-Host "Install from: https://kubernetes.io/docs/tasks/tools/" -ForegroundColor Yellow
    exit 1
}

# Check if Helm is installed
if (Get-Command helm -ErrorAction SilentlyContinue) {
    $helmVersion = helm version --short
    Write-Host "✓ Helm is installed (version: $helmVersion)" -ForegroundColor Green
} else {
    Write-Host "❌ Helm is not installed." -ForegroundColor Red
    Write-Host "Install from: https://helm.sh/docs/intro/install/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "2. Starting Minikube..." -ForegroundColor Yellow

# Stop and delete existing cluster if it exists
if (minikube status -p $MINIKUBE_PROFILE -o json 2>$null) {
    Write-Host "Stopping existing cluster..." -ForegroundColor Gray
    minikube stop -p $MINIKUBE_PROFILE
}

$profiles = minikube profile list 2>$null | ConvertFrom-Json
if ($profiles.profiles.name -contains $MINIKUBE_PROFILE) {
    Write-Host "Deleting existing cluster..." -ForegroundColor Gray
    minikube delete -p $MINIKUBE_PROFILE
}

# Start Minikube with optimized settings
Write-Host "Starting Minikube cluster..." -ForegroundColor Gray
minikube start `
    --profile $MINIKUBE_PROFILE `
    --driver $MINIKUBE_DRIVER `
    --cpus $MINIKUBE_CPUS `
    --memory $MINIKUBE_MEMORY `
    --disk-size $MINIKUBE_DISK `
    --kubernetes-version $KUBERNETES_VERSION `
    --enable-default-cni `
    --addons=storage-provisioner `
    --wait=all `
    --timeout=10m

Write-Host "✓ Minikube cluster started" -ForegroundColor Green

Write-Host ""
Write-Host "3. Configuring kubectl..." -ForegroundColor Yellow

# Set kubectl context
kubectl config use-context minikube-$MINIKUBE_PROFILE
Write-Host "✓ kubectl context set" -ForegroundColor Green

Write-Host ""
Write-Host "4. Enabling Minikube addons..." -ForegroundColor Yellow

minikube addons enable ingress -p $MINIKUBE_PROFILE
minikube addons enable metrics-server -p $MINIKUBE_PROFILE
Write-Host "✓ Minikube addons enabled" -ForegroundColor Green

Write-Host ""
Write-Host "5. Installing Dapr..." -ForegroundColor Yellow

# Check if Dapr CLI is installed
if (Get-Command dapr -ErrorAction SilentlyContinue) {
    Write-Host "✓ Dapr CLI is installed" -ForegroundColor Green
} else {
    Write-Host "Installing Dapr CLI..." -ForegroundColor Gray
    powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
    $env:Path += ";$env:USERPROFILE\.dapr\bin"
}

# Initialize Dapr on Kubernetes
Write-Host "Installing Dapr on Kubernetes..." -ForegroundColor Gray
dapr init -k --wait
Write-Host "✓ Dapr installed" -ForegroundColor Green

Write-Host ""
Write-Host "6. Verifying installation..." -ForegroundColor Yellow

# Wait for pods to be ready
Write-Host "Waiting for system pods to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Minikube Setup Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Cluster Info:" -ForegroundColor Yellow
minikube status -p $MINIKUBE_PROFILE

Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  - Access Dashboard: minikube dashboard -p $MINIKUBE_PROFILE"
Write-Host "  - View all pods: kubectl get pods -A"
Write-Host "  - View Dapr components: kubectl get components -n default"

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Build Docker images: docker-compose build"
Write-Host "  2. Load images: minikube image load todo-app-phase-v-backend:latest"
Write-Host "  3. Deploy: helm install todo-app ./k8s/helm/backend"
Write-Host ""
