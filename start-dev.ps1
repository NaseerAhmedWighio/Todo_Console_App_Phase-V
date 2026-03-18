# Docker Development Startup Script
# Starts infrastructure (Kafka, Redis) in Docker, runs backend locally

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Todo App Phase V - Development Mode" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "[WARNING] .env file not found!" -ForegroundColor Yellow
    Write-Host "Copy .env.example to .env and configure your environment variables." -ForegroundColor Yellow
    Write-Host ""
}

# Check if backend/.env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "[WARNING] backend\.env file not found!" -ForegroundColor Yellow
    Write-Host "Copy backend\.env.example to backend\.env and configure your environment variables." -ForegroundColor Yellow
    Write-Host ""
}

# Start Docker infrastructure
Write-Host "[1/3] Starting Docker infrastructure (Kafka, Redis)..." -ForegroundColor Green
docker-compose -f docker-compose.dev.yml up -d kafka zookeeper redis

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to start Docker services!" -ForegroundColor Red
    exit 1
}

Write-Host "[2/3] Waiting for services to be ready..." -ForegroundColor Green
Start-Sleep -Seconds 10

# Check if services are healthy
$redisReady = $false
$kafkaReady = $false

for ($i = 0; $i -lt 30; $i++) {
    $result = docker-compose -f docker-compose.dev.yml ps
    if ($result -match "redis-dev.*healthy") {
        $redisReady = $true
        break
    }
    Start-Sleep -Seconds 2
}

if (-not $redisReady) {
    Write-Host "[WARNING] Redis may not be fully ready yet" -ForegroundColor Yellow
}

Write-Host "[3/3] Starting backend locally..." -ForegroundColor Green
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Services Status:" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  Frontend:  Will be available at http://localhost:3000 (after you start it)" -ForegroundColor Green
Write-Host "  Backend:   Starting at http://localhost:7860" -ForegroundColor Green
Write-Host "  Kafka:     localhost:9092" -ForegroundColor Green
Write-Host "  Redis:     localhost:6379" -ForegroundColor Green
Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  1. Backend is starting now..." -ForegroundColor White
Write-Host "  2. In another terminal, run: docker-compose -f docker-compose.dev-frontend.yml up" -ForegroundColor White
Write-Host "     OR run: cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "To stop Docker services: docker-compose -f docker-compose.dev.yml down" -ForegroundColor Yellow
Write-Host ""

# Start backend locally
cd backend
python -m uvicorn main:app --reload --port 7860
