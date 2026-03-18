# Complete clean reinstall script
Write-Host "Stopping any running Node processes..."
Stop-Process -Name node -Force -ErrorAction SilentlyContinue

Write-Host "Removing node_modules..."
Remove-Item -Recurse -Force node_modules -ErrorAction SilentlyContinue

Write-Host "Removing package-lock.json..."
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue

Write-Host "Cleaning npm cache..."
npm cache clean --force

Write-Host "Installing dependencies..."
npm install --legacy-peer-deps

Write-Host "Done!"
