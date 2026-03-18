# Docker Image Build Script for Todo App Phase-V
# This script builds both backend and frontend Docker images

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Todo App Phase-V - Docker Image Build  " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Function to print messages
function Write-Info {
    param([string]$Message)
    Write-Host ">>> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host ">>> $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host ">>> ERROR: $Message" -ForegroundColor Red
}

# Check if Docker is running
Write-Info "Checking Docker status..."
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Custom "Docker is not running. Please start Docker Desktop and try again."
        exit 1
    }
    Write-Success "Docker is running"
} catch {
    Write-Error-Custom "Docker is not running. Please start Docker Desktop and try again."
    exit 1
}
Write-Host ""

# Build backend image
Write-Info "Building backend image (todo-backend:latest)..."
Set-Location "$ScriptDir\backend"
if (docker build -t todo-backend:latest .) {
    Write-Success "Backend image built successfully!"
} else {
    Write-Error-Custom "Failed to build backend image"
    exit 1
}
Write-Host ""

# Build frontend image
Write-Info "Building frontend image (todo-frontend:latest)..."
Set-Location "$ScriptDir\frontend"
if (docker build -t todo-frontend:latest .) {
    Write-Success "Frontend image built successfully!"
} else {
    Write-Error-Custom "Failed to build frontend image"
    exit 1
}
Write-Host ""

# Show image information
Write-Info "Build Summary:"
Write-Host ""
Write-Host "Backend Image:"
docker images todo-backend:latest --format "table {{.Repository}}`t{{.Tag}}`t{{.ID}}`t{{.Size}}"
Write-Host ""
Write-Host "Frontend Image:"
docker images todo-frontend:latest --format "table {{.Repository}}`t{{.Tag}}`t{{.ID}}`t{{.Size}}"
Write-Host ""

Write-Success "All images built successfully!"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test locally: docker-compose up -d"
Write-Host "  2. Load into Minikube: minikube image load todo-backend:latest todo-frontend:latest"
Write-Host "  3. Push to registry: docker push your-registry/todo-backend:latest"
Write-Host ""

Set-Location $ScriptDir
