@echo off
echo ================================================
echo Docker Desktop WSL Fix Script
echo ================================================
echo.
echo This will fix the Docker Desktop WSL error
echo.
echo IMPORTANT: Close Docker Desktop before running this!
echo.
pause

echo.
echo Step 1: Shutting down WSL...
wsl --shutdown

echo.
echo Step 2: Unregistering Docker WSL distributions...
wsl --unregister docker-desktop 2>nul
wsl --unregister docker-desktop-data 2>nul

echo.
echo Step 3: Updating WSL...
wsl --update

echo.
echo Step 4: Checking WSL status...
wsl --status

echo.
echo ================================================
echo Fix Applied!
echo ================================================
echo.
echo Next steps:
echo 1. Start Docker Desktop
echo 2. Wait 2-3 minutes for it to initialize
echo 3. Docker will recreate WSL distributions automatically
echo.
echo Then run: docker-compose up -d
echo.
pause
