# Fix Docker Desktop WSL Error

**Error:** `ERROR_PATH_NOT_FOUND` when starting Docker Desktop
**Cause:** WSL has no installed distributions

## Quick Fix Steps

### Option 1: Reinstall Docker Desktop's WSL Distributions (Fastest)

1. **Close Docker Desktop completely**
   - Right-click Docker Desktop in system tray → Quit Docker Desktop
   - Wait 30 seconds

2. **Reset WSL**
   ```powershell
   # Run in PowerShell as Administrator
   wsl --shutdown
   wsl --unregister docker-desktop
   wsl --unregister docker-desktop-data
   ```

3. **Start Docker Desktop again**
   - Docker will automatically recreate the WSL distributions
   - Wait 2-3 minutes for initialization

### Option 2: Install a Linux Distribution (Recommended for Long-term)

If Option 1 doesn't work, install Ubuntu:

```powershell
# Run in PowerShell as Administrator
wsl --install Ubuntu
```

Then restart Docker Desktop.

### Option 3: Update WSL

```powershell
# Run in PowerShell as Administrator
wsl --update
wsl --shutdown
```

Then restart Docker Desktop.

## Verification

After trying a fix:

```bash
wsl --list --verbose
```

Should show:
```
  NAME                   STATE           VERSION
* docker-desktop         Running         2
  docker-desktop-data    Running         2
```

## If Nothing Works

1. **Uninstall Docker Desktop completely**
   - Settings → Apps → Docker Desktop → Uninstall
   - Delete `C:\Users\sidro\AppData\Local\Docker` folder

2. **Update WSL**
   ```powershell
   wsl --update
   ```

3. **Reinstall Docker Desktop**
   - Download from https://www.docker.com/products/docker-desktop
   - Install with default settings
   - Enable "Use WSL 2" during installation

## Alternative: Run Without Docker

For this Twinzo test, we can actually run without Docker:

1. **Run MQTT broker locally** (if you have Mosquitto installed)
2. **Run Python scripts directly**:
   ```bash
   python -X utf8 test_twinzo_live.py
   ```

This script doesn't need MQTT broker - it directly sends to Twinzo API!

---

**Current Status:** WSL has no distributions installed
**Recommended:** Try Option 1 first (quickest)
