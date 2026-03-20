# ============================================
# Todo App Phase V - Dapr Notification System
# Quick Start Script for Windows PowerShell
# ============================================

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Todo App Phase V - Dapr Deployment   " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Color functions
function Write-Info {
    param([string]$Message)
    Write-Host ">>> $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host ">>> $Message" -ForegroundColor Green
}

function Write-Warning-Custom {
    param([string]$Message)
    Write-Host ">>> WARNING: $Message" -ForegroundColor Yellow
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host ">>> ERROR: $Message" -ForegroundColor Red
}

# ============================================
# Step 1: Check Prerequisites
# ============================================
Write-Info "Step 1: Checking prerequisites..."

# Check Docker
try {
    $dockerVersion = docker --version 2>&1
    Write-Success "Docker installed: $dockerVersion"
} catch {
    Write-Error-Custom "Docker is not installed or not running!"
    Write-Info "Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Check Docker Compose
try {
    $composeVersion = docker-compose --version 2>&1
    Write-Success "Docker Compose installed: $composeVersion"
} catch {
    Write-Error-Custom "Docker Compose is not installed!"
    exit 1
}

# Check if .env file exists
if (Test-Path ".env") {
    Write-Success ".env file found"
} else {
    Write-Warning-Custom ".env file not found! Copy .env.example to .env and fill in your credentials"
    Write-Info "Run: cp .env.example .env"
}

Write-Host ""

# ============================================
# Step 2: Build Application Images
# ============================================
Write-Info "Step 2: Building application images..."

$buildImages = Read-Host "Build backend and frontend images? (y/n)"

if ($buildImages -eq "y" -or $buildImages -eq "Y") {
    # Build backend
    Write-Info "Building backend image..."
    Set-Location "$ScriptDir\backend"
    if (docker build -t naseerahmedwighio/todo-console-app-v-backend:latest .) {
        Write-Success "Backend image built successfully!"
    } else {
        Write-Error-Custom "Failed to build backend image"
        exit 1
    }
    
    # Build frontend
    Write-Info "Building frontend image..."
    Set-Location "$ScriptDir\frontend"
    if (docker build -t naseerahmedwighio/todo-console-app-v-frontend:latest .) {
        Write-Success "Frontend image built successfully!"
    } else {
        Write-Error-Custom "Failed to build frontend image"
        exit 1
    }
    
    Set-Location $ScriptDir
    
    # Tag images
    Write-Info "Tagging images..."
    docker tag naseerahmedwighio/todo-console-app-v-backend:latest naseerahmedwighio/todo-console-app-v-backend:latest
    docker tag naseerahmedwighio/todo-console-app-v-frontend:latest naseerahmedwighio/todo-console-app-v-frontend:latest
    
    Write-Success "Images built and tagged successfully!"
} else {
    Write-Info "Skipping image build (using existing images)"
}

Write-Host ""

# ============================================
# Step 3: Pull Infrastructure Images
# ============================================
Write-Info "Step 3: Pulling infrastructure images..."

docker pull confluentinc/cp-zookeeper:7.4.0
docker pull confluentinc/cp-kafka:7.4.0
docker pull redis:7-alpine
docker pull daprio/daprd:1.12.0

Write-Success "Infrastructure images pulled!"
Write-Host ""

# ============================================
# Step 4: Start All Services
# ============================================
Write-Info "Step 4: Starting all services with Dapr..."

$startTime = Get-Date
docker-compose -f docker-compose-dapr.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Success "All services started!"
} else {
    Write-Error-Custom "Failed to start services"
    exit 1
}

Write-Host ""

# ============================================
# Step 5: Wait for Services to be Ready
# ============================================
Write-Info "Step 5: Waiting for services to be ready..."

$maxAttempts = 30
$attempt = 0

Write-Info "Waiting for backend to be healthy..."
while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:7860/health" -TimeoutSec 5 -UseBasicParsing 2>$null
        if ($response.StatusCode -eq 200) {
            Write-Success "Backend is healthy!"
            break
        }
    } catch {
        $attempt++
        Start-Sleep -Seconds 2
        if ($attempt % 5 -eq 0) {
            Write-Info "Still waiting for backend... (attempt $attempt/$maxAttempts)"
        }
    }
}

if ($attempt -eq $maxAttempts) {
    Write-Warning-Custom "Backend health check timed out. Check logs with: docker logs todo-backend"
}

Write-Host ""
Write-Info "Waiting for Dapr sidecar to be ready..."
Start-Sleep -Seconds 10

try {
    $daprResponse = Invoke-WebRequest -Uri "http://localhost:3500/v1.0/healthz" -TimeoutSec 5 -UseBasicParsing 2>$null
    if ($daprResponse.StatusCode -eq 200) {
        Write-Success "Dapr sidecar is healthy!"
    }
} catch {
    Write-Warning-Custom "Dapr sidecar health check failed. Check logs with: docker logs todo-dapr-sidecar"
}

Write-Host ""

# ============================================
# Step 6: Show Service Status
# ============================================
Write-Info "Step 6: Service Status"
Write-Host ""
Write-Host "Running Containers:" -ForegroundColor Yellow
docker ps --filter "name=todo-" --filter "name=kafka" --filter "name=zookeeper" --filter "name=redis" --format "table {{.Names}}`t{{.Status}}`t{{.Ports}}"
Write-Host ""

# ============================================
# Step 7: Show Access Information
# ============================================
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Deployment Complete!                  " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your services are running:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  Frontend:        http://localhost:3000" -ForegroundColor White
Write-Host "  Backend API:     http://localhost:7860" -ForegroundColor White
Write-Host "  Dapr API:        http://localhost:3500" -ForegroundColor White
Write-Host "  Kafka:           localhost:9092" -ForegroundColor White
Write-Host "  Redis:           localhost:6379" -ForegroundColor White
Write-Host "  Zookeeper:       localhost:2181" -ForegroundColor White
Write-Host ""
Write-Host "Quick Tests:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  # Test backend health" -ForegroundColor Gray
Write-Host "  curl http://localhost:7860/health" -ForegroundColor White
Write-Host ""
Write-Host "  # Test Dapr health" -ForegroundColor Gray
Write-Host "  curl http://localhost:3500/v1.0/healthz" -ForegroundColor White
Write-Host ""
Write-Host "  # Send test notification email" -ForegroundColor Gray
Write-Host "  curl -X POST http://localhost:7860/api/v1/notifications/send-test-email -H 'Authorization: Bearer YOUR_TOKEN'" -ForegroundColor White
Write-Host ""
Write-Host "  # Create recurring task (Pay Bills)" -ForegroundColor Gray
Write-Host "  curl -X POST 'http://localhost:7860/api/v1/recurring/create-with-notifications?task_title=Pay%20Bills&recurrence_pattern=pay_bills&by_monthday=1' -H 'Authorization: Bearer YOUR_TOKEN'" -ForegroundColor White
Write-Host ""
Write-Host "Logs:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  # View all logs" -ForegroundColor Gray
Write-Host "  docker-compose -f docker-compose-dapr.yml logs -f" -ForegroundColor White
Write-Host ""
Write-Host "  # View backend logs" -ForegroundColor Gray
Write-Host "  docker logs -f todo-backend" -ForegroundColor White
Write-Host ""
Write-Host "  # View Dapr logs" -ForegroundColor Gray
Write-Host "  docker logs -f todo-dapr-sidecar" -ForegroundColor White
Write-Host ""
Write-Host "Stop Services:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  docker-compose -f docker-compose-dapr.yml down" -ForegroundColor White
Write-Host ""

$endTime = Get-Date
$duration = New-TimeSpan -Start $startTime -End $endTime
Write-Info "Total deployment time: $($duration.Minutes)m $($duration.Seconds)s"
Write-Host ""
