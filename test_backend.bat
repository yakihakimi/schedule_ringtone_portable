@echo off
REM Rules applied
setlocal enabledelayedexpansion

title Backend Server Test

echo ========================================
echo    Backend Server Test
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend\server.py" (
    echo [ERROR] This script must be run from the portable_app directory
    echo [INFO] Please navigate to the portable_app folder and run test_backend.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Testing backend server startup...
echo.

cd backend

echo [1/3] Checking Python dependencies...
python -c "import flask, flask_cors, pydub; print('Dependencies OK')"
if !errorlevel! neq 0 (
    echo [ERROR] Python dependencies are missing
    echo [INFO] Please run install_dependencies.bat first
    cd ..
    pause
    exit /b 1
)

echo [2/3] Starting backend server...
echo [INFO] Server will start in a new window. Check for any error messages.
echo [INFO] If successful, you should see: "Running on http://127.0.0.1:5000"
echo.

start "Backend Server Test" cmd /k "python server.py"

echo [3/3] Waiting for server to start...
timeout /t 5 /nobreak >nul

echo [INFO] Testing server connection...
curl -s http://localhost:5000/health >nul 2>&1
if !errorlevel! equ 0 (
    echo [SUCCESS] Backend server is running and responding!
    echo [INFO] You can access the API at: http://localhost:5000
) else (
    echo [WARNING] Could not connect to backend server
    echo [INFO] Check the server window for error messages
    echo [INFO] Make sure port 5000 is not blocked by firewall
)

echo.
echo [INFO] Test completed. Check the server window for details.
echo [INFO] Close the server window when done testing.
echo.
pause
exit /b 0
