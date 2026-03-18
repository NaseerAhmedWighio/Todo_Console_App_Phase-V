Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Frontend Service Build Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "`nBuilding frontend image..." -ForegroundColor Yellow
docker-compose build frontend

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nStarting frontend service..." -ForegroundColor Green
    docker-compose up -d frontend
    
    Write-Host "`nWaiting for frontend to be healthy..." -ForegroundColor Gray
    Start-Sleep -Seconds 15
    
    Write-Host "`nFrontend service status:" -ForegroundColor Cyan
    docker-compose ps frontend
    
    Write-Host "`n✓ Frontend is ready!" -ForegroundColor Green
    Write-Host "  - Web UI: http://localhost:3000"
} else {
    Write-Host "`n✗ Frontend build failed!" -ForegroundColor Red
    exit 1
}
