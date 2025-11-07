# Fix WSL Virtualization - Complete Guide

## Problem
WSL cannot create virtual machines: `ERROR_PATH_NOT_FOUND` at HCS level
This affects both Docker Desktop AND regular WSL installations.

## Solution: Enable Windows Virtualization Features

### Step 1: Enable Required Windows Features

**Open PowerShell as Administrator** and run:

```powershell
# Enable WSL feature
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart

# Enable Virtual Machine Platform
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# (Optional but recommended) Enable Hyper-V
dism.exe /online /enable-feature /featurename:Microsoft-Hyper-V-All /all /norestart
```

### Step 2: Restart Computer

**CRITICAL**: You MUST restart for these changes to take effect.

```powershell
shutdown /r /t 30
```

### Step 3: After Restart - Configure WSL

**Open PowerShell as Administrator:**

```powershell
# Update WSL to latest version
wsl --update

# Set WSL 2 as default version
wsl --set-default-version 2

# Verify WSL status
wsl --status
```

Should show:
```
Default Version: 2
```

### Step 4: Install Ubuntu

```powershell
wsl --install Ubuntu
```

This will:
- Download Ubuntu (~500MB)
- Install it as a WSL distribution
- Prompt you to create a username/password (just use simple ones for Docker)

### Step 5: Verify WSL Works

```powershell
wsl --list --verbose
```

Should show:
```
  NAME      STATE           VERSION
* Ubuntu    Stopped         2
```

### Step 6: Start Docker Desktop

Now Docker Desktop can work because WSL is properly configured!

1. Open Docker Desktop
2. Wait 3-5 minutes for initialization
3. Docker will create its distributions automatically

Verify with:
```powershell
wsl --list --verbose
```

Should show:
```
  NAME                   STATE           VERSION
* Ubuntu                 Stopped         2
  docker-desktop         Running         2
  docker-desktop-data    Running         2
```

---

## Alternative: Using Windows Features GUI

If PowerShell doesn't work:

1. Press `Win + R`, type `optionalfeatures`, press Enter
2. Check these boxes:
   - ☑ Virtual Machine Platform
   - ☑ Windows Subsystem for Linux
   - ☑ Hyper-V (if available)
3. Click OK
4. Restart when prompted
5. Continue with Step 3 above

---

## Verification Commands

After restart and setup:

```powershell
# Check Windows features
dism.exe /online /get-features | findstr -i "virtual machine subsystem"

# Check WSL
wsl --status
wsl --list --verbose

# Check Docker
docker --version
docker ps
```

---

## Total Time Required
- Enable features: 2 minutes
- Restart: 2 minutes
- Configure WSL: 2 minutes
- Install Ubuntu: 5 minutes
- Start Docker: 3 minutes

**Total: ~15 minutes**

---

## What This Fixes
✅ WSL ERROR_PATH_NOT_FOUND errors
✅ Docker Desktop WSL integration issues
✅ Ability to run any Linux distribution in WSL
✅ Proper virtualization for WSL 2

---

## After Everything Works

Test your setup:

```bash
# Navigate to your project
cd C:\Users\sidro\all-code\archived\twinzo-mock

# Start Docker containers
docker-compose up -d

# Verify containers running
docker-compose ps

# Check logs
docker-compose logs -f bridge
```

You should see:
- 3 containers running (broker, publisher, bridge)
- Bridge connecting to Twinzo API
- OAuth authentication succeeding
- Position data being sent to Twinzo
