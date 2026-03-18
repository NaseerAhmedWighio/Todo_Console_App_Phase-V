Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Backend Service Build Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "`nBuilding backend image..." -ForegroundColor Yellow
docker-compose build backend

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nStarting backend service..." -ForegroundColor Green
    docker-compose up -d backend
    
    Write-Host "`nWaiting for backend to be healthy..." -ForegroundColor Gray
    Start-Sleep -Seconds 15
    
    Write-Host "`nBackend service status:" -ForegroundColor Cyan
    docker-compose ps backend
    
    Write-Host "`n✓ Backend is ready!" -ForegroundColor Green
    Write-Host "  - API: http://localhost:7860"
    Write-Host "  - API Docs: http://localhost:7860/docs"
} else {
    Write-Host "`n✗ Backend build failed!" -ForegroundColor Red
    exit 1
}
