# Docker Desktop Complete Cleanup Script
# Run this in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker Desktop Complete Cleanup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop all Docker processes
Write-Host "Step 1: Stopping Docker Desktop processes..." -ForegroundColor Yellow
Get-Process "*docker*" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 3

# Step 2: Shutdown WSL
Write-Host "Step 2: Shutting down WSL..." -ForegroundColor Yellow
wsl --shutdown
Start-Sleep -Seconds 2

# Step 3: Unregister any remaining WSL distributions
Write-Host "Step 3: Unregistering Docker WSL distributions..." -ForegroundColor Yellow
wsl --unregister docker-desktop 2>$null
wsl --unregister docker-desktop-data 2>$null

# Step 4: Delete Docker files
Write-Host "Step 4: Deleting Docker files..." -ForegroundColor Yellow

$dockerPaths = @(
    "$env:LOCALAPPDATA\Docker",
    "$env:APPDATA\Docker",
    "$env:ProgramFiles\Docker"
)

foreach ($path in $dockerPaths) {
    if (Test-Path $path) {
        Write-Host "  Deleting: $path" -ForegroundColor Gray
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "  Not found: $path" -ForegroundColor Gray
    }
}

# Step 5: Verify cleanup
Write-Host ""
Write-Host "Step 5: Verifying cleanup..." -ForegroundColor Yellow
$cleanupSuccess = $true
foreach ($path in $dockerPaths) {
    if (Test-Path $path) {
        Write-Host "  WARNING: Still exists: $path" -ForegroundColor Red
        $cleanupSuccess = $false
    }
}

if ($cleanupSuccess) {
    Write-Host "  ✓ All Docker files deleted successfully!" -ForegroundColor Green
} else {
    Write-Host "  Some files could not be deleted. Try restarting and running this script again." -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cleanup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart your computer (important!)" -ForegroundColor White
Write-Host "2. Download Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor White
Write-Host "3. Install Docker Desktop with default settings" -ForegroundColor White
Write-Host "4. Wait 5-10 minutes for first initialization" -ForegroundColor White
Write-Host ""

pause
