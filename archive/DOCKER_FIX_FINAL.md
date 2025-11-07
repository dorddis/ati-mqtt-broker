# Docker Desktop WSL Fix - Final Solution

## Problem
Docker's WSL VHD files are corrupted or missing at:
`C:\Users\sidro\AppData\Local\Docker\wsl\main\ext4.vhdx`

## Solution: Clean Reset Docker's WSL Data

### Step 1: Close Docker Desktop Completely
1. Right-click Docker Desktop in system tray
2. Click "Quit Docker Desktop"
3. Wait 30 seconds

### Step 2: Delete Docker's WSL Data Files

Open PowerShell as Administrator and run:

```powershell
# Navigate to Docker's WSL data directory
cd $env:LOCALAPPDATA\Docker\wsl

# List what's there (to see what we're deleting)
dir

# Delete all WSL data (this will be recreated)
Remove-Item -Path data -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path main -Recurse -Force -ErrorAction SilentlyContinue
```

### Step 3: Clear Docker Desktop Settings (Optional but Recommended)

```powershell
# This resets Docker to fresh state
Remove-Item -Path "$env:APPDATA\Docker\settings.json" -Force -ErrorAction SilentlyContinue
```

### Step 4: Restart Docker Desktop
1. Open Docker Desktop
2. **IMPORTANT: Wait 3-5 minutes** for full initialization
3. It will recreate all WSL distributions from scratch
4. You should see "Docker Desktop is running" in system tray

### Step 5: Verify
```powershell
wsl --list --verbose
```

Should show:
```
  NAME                   STATE           VERSION
* docker-desktop         Running         2
  docker-desktop-data    Running         2
```

---

## If That Doesn't Work: Nuclear Option

1. **Uninstall Docker Desktop completely**
   - Settings → Apps → Docker Desktop → Uninstall

2. **Delete all Docker folders**
   ```powershell
   Remove-Item -Path "$env:LOCALAPPDATA\Docker" -Recurse -Force
   Remove-Item -Path "$env:APPDATA\Docker" -Recurse -Force
   Remove-Item -Path "$env:ProgramFiles\Docker" -Recurse -Force
   ```

3. **Restart computer**

4. **Install Docker Desktop fresh**
   - Download from https://www.docker.com/products/docker-desktop
   - Install with default settings
   - Wait 5 minutes after installation for initialization

---

## Commands Summary

Run these in PowerShell as Administrator (after closing Docker):

```powershell
# Stop Docker
wsl --shutdown

# Delete corrupted WSL data
cd $env:LOCALAPPDATA\Docker\wsl
Remove-Item -Path data -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path main -Recurse -Force -ErrorAction SilentlyContinue

# Start Docker Desktop and wait 3-5 minutes
```
