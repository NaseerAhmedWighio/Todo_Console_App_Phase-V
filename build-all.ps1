Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Full Stack Build & Start Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "`n=== Step 1: Infrastructure Services ===" -ForegroundColor Yellow
docker-compose pull zookeeper kafka redis
docker-compose up -d zookeeper kafka redis

Write-Host "`nWaiting for infrastructure to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 15

Write-Host "`n=== Step 2: Build Backend ===" -ForegroundColor Yellow
docker-compose build backend

Write-Host "`n=== Step 3: Build Frontend ===" -ForegroundColor Yellow
docker-compose build frontend

Write-Host "`n=== Step 4: Start All Services ===" -ForegroundColor Green
docker-compose up -d backend frontend

Write-Host "`nWaiting for all services to be healthy..." -ForegroundColor Gray
Start-Sleep -Seconds 20

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  All Services Status" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
docker-compose ps

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "  Service Endpoints" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Frontend:  http://localhost:3000"
Write-Host "  Backend:   http://localhost:7860"
Write-Host "  API Docs:  http://localhost:7860/docs"
Write-Host "  Kafka:     localhost:9092"
Write-Host "  Redis:     localhost:6379"
Write-Host "  Zookeeper: localhost:2181"
Write-Host "========================================="
Write-Host "`n✓ Full stack is ready!" -ForegroundColor Green
