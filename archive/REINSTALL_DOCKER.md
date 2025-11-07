# Docker Desktop Complete Reinstall Guide

## Problem
Docker's base WSL distribution files are corrupted. Need clean reinstall.

## Solution: Complete Reinstall (10 minutes)

### Step 1: Uninstall Docker Desktop

**Option A: Using Windows Settings**
1. Press `Win + I` to open Settings
2. Go to Apps → Installed apps
3. Find "Docker Desktop"
4. Click three dots → Uninstall
5. Follow prompts

**Option B: Using PowerShell (as Administrator)**
```powershell
Get-Package -Name "Docker Desktop" | Uninstall-Package
```

### Step 2: Clean Up All Docker Files

**Run in PowerShell as Administrator:**
```powershell
# Shutdown WSL
wsl --shutdown

# Delete all Docker folders
Remove-Item -Path "$env:LOCALAPPDATA\Docker" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:APPDATA\Docker" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:ProgramFiles\Docker" -Recurse -Force -ErrorAction SilentlyContinue

# Verify deletion
Test-Path "$env:LOCALAPPDATA\Docker"  # Should return False
```

### Step 3: Restart Computer
This ensures all Docker processes are fully terminated and file locks are released.

### Step 4: Download Docker Desktop
1. Go to: https://www.docker.com/products/docker-desktop
2. Click "Download for Windows"
3. Wait for download to complete (500MB file)

### Step 5: Install Docker Desktop
1. Run the installer: `Docker Desktop Installer.exe`
2. **IMPORTANT**: Check these options:
   - ✅ "Use WSL 2 instead of Hyper-V" (if asked)
   - ✅ "Add shortcut to desktop"
3. Click Install
4. Wait for installation (3-5 minutes)
5. Click "Close and restart" when prompted

### Step 6: First Launch
1. Open Docker Desktop
2. Accept license agreement
3. **Wait 5-10 minutes** for first-time initialization
4. You should see "Docker Desktop is running"

### Step 7: Verify Installation
```powershell
# Check WSL distributions
wsl --list --verbose

# Should show:
#   NAME                   STATE           VERSION
# * docker-desktop         Running         2
#   docker-desktop-data    Running         2

# Check Docker
docker --version
docker ps
```

---

## Quick Automated Cleanup Script

Save this as `cleanup_docker.ps1` and run as Administrator:

```powershell
Write-Host "Stopping Docker Desktop..." -ForegroundColor Yellow
Get-Process "*docker*" | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Shutting down WSL..." -ForegroundColor Yellow
wsl --shutdown

Write-Host "Deleting Docker files..." -ForegroundColor Yellow
Remove-Item -Path "$env:LOCALAPPDATA\Docker" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:APPDATA\Docker" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "$env:ProgramFiles\Docker" -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Cleanup complete!" -ForegroundColor Green
Write-Host "Please restart your computer, then install Docker Desktop." -ForegroundColor Cyan
```

---

## After Reinstall: Start Your Project

Once Docker is working:

```bash
cd C:\Users\sidro\all-code\archived\twinzo-mock
docker-compose up -d
docker-compose ps
```

You should see:
```
NAME                 COMMAND                  SERVICE     STATUS
mock-mqtt-broker     "/docker-entrypoint.…"   broker      running
mock-publisher       "python publisher.py"    publisher   running
mock-rest-bridge     "python bridge.py"       bridge      running
```

---

## Estimated Time
- Uninstall: 2 minutes
- Cleanup: 1 minute
- Restart: 2 minutes
- Download: 3 minutes (depends on internet)
- Install: 5 minutes
- First launch: 5 minutes

**Total: ~18 minutes**

Worth it to have a clean, working Docker installation!
