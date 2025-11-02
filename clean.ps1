# Django Project Clean Script
# Usage: .\clean.ps1

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host " CLEANING DJANGO PROJECT CACHE..." -ForegroundColor Yellow
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Clean Python Cache
Write-Host "Cleaning Python cache files..." -ForegroundColor Green
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Include "*.pyc","*.pyo" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "Done!" -ForegroundColor Gray
Write-Host ""

# Clean Test Coverage
Write-Host "Cleaning test and coverage files..." -ForegroundColor Green
Get-ChildItem -Path . -Recurse -Include ".coverage","coverage.xml","htmlcov",".pytest_cache" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Done!" -ForegroundColor Gray
Write-Host ""

# Clean Build Artifacts
Write-Host "Cleaning build artifacts..." -ForegroundColor Green
Get-ChildItem -Path . -Recurse -Include "*.egg-info","build","dist" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Done!" -ForegroundColor Gray
Write-Host ""

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host " CLEANING COMPLETED!" -ForegroundColor Green
Write-Host "================================================================================" -ForegroundColor Cyan
