@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python 3 was not found. Install Python 3.9+ and enable Add Python to PATH.
  pause
  exit /b 1
)
echo Starting Olive and Oak Online Shopping Management System...
start "ShopSphere browser" http://localhost:8000
python server.py
pause
