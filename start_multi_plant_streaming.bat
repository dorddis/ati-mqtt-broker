@echo off
echo ========================================
echo Multi-Plant AMR Streaming
echo ========================================
echo.
echo Starting services...
echo - Publisher: 3 tuggers with mock movement data
echo - Bridge: Streaming to BOTH HiTech (Sector 1) and Old Plant (Sector 2)
echo.

REM Set environment variables for multi-plant streaming
set SECTOR_IDS=1,2
set LOG_EVERY_N=10
set NUM_ROBOTS=3
set ROBOT_PREFIX=tugger
set HZ=10

REM Start publisher in new window
echo Starting publisher...
start "AMR Publisher (3 Tuggers)" cmd /k "cd /d %~dp0 && python -X utf8 src/publisher/publisher.py"

REM Wait 3 seconds for publisher to start
timeout /t 3 /nobreak >nul

REM Start bridge in new window
echo Starting bridge...
start "Multi-Plant Bridge (HiTech + Old Plant)" cmd /k "cd /d %~dp0 && python -X utf8 src/bridge/bridge.py"

echo.
echo ========================================
echo Services Started!
echo ========================================
echo.
echo Two windows should open:
echo 1. AMR Publisher - Generating mock movement for 3 tuggers
echo 2. Multi-Plant Bridge - Streaming to both plants
echo.
echo You should see messages like:
echo   "POST ok 200 for tugger-01 to Sector 1 ..."
echo   "POST ok 200 for tugger-01 to Sector 2 ..."
echo.
echo Check the Twinzo UI at:
echo - HiTech Plant: https://platform.twinzo.com/branch/dcac4881-05ab-4f29-b0df-79c40df9c9c2
echo - Old Plant: https://platform.twinzo.com/branch/40557468-2d57-4a3d-9a5e-3eede177daf5
echo.
echo Close the command windows to stop streaming.
echo.
pause
