Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Infrastructure Services Build Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "`n[1/3] Pulling Zookeeper..." -ForegroundColor Yellow
docker-compose pull zookeeper

Write-Host "`n[2/3] Pulling Kafka..." -ForegroundColor Yellow
docker-compose pull kafka

Write-Host "`n[3/3] Pulling Redis..." -ForegroundColor Yellow
docker-compose pull redis

Write-Host "`nStarting infrastructure services..." -ForegroundColor Green
docker-compose up -d zookeeper kafka redis

Write-Host "`nWaiting for services to be healthy..." -ForegroundColor Gray
Start-Sleep -Seconds 10

Write-Host "`nInfrastructure services status:" -ForegroundColor Cyan
docker-compose ps zookeeper kafka redis

Write-Host "`n✓ Infrastructure services are ready!" -ForegroundColor Green
Write-Host "  - Zookeeper: localhost:2181"
Write-Host "  - Kafka: localhost:9092"
Write-Host "  - Redis: localhost:6379"
