@echo off
REM Rules applied
setlocal enabledelayedexpansion

title Portable Ringtone Creator - Dependency Installer

echo ========================================
echo    Dependency Installation Script
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend\server.py" (
    echo [ERROR] This script must be run from the portable_app directory
    echo [INFO] Please navigate to the portable_app folder and run install_dependencies.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Installing Python dependencies with proxy support...
echo.

cd backend

REM Try with proxy first
echo [1/2] Attempting installation with proxy...
pip install --proxy http://proxy-enclave.altera.com:912 -r requirements.txt
if !errorlevel! equ 0 (
    echo [SUCCESS] Dependencies installed successfully with proxy
    cd ..
    goto :check_installation
)

echo [WARNING] Proxy installation failed, trying without proxy...
echo [2/2] Attempting installation without proxy...
pip install -r requirements.txt
if !errorlevel! equ 0 (
    echo [SUCCESS] Dependencies installed successfully without proxy
    cd ..
    goto :check_installation
)

echo [ERROR] Failed to install Python dependencies
echo [INFO] Please check your internet connection and try again
cd ..
pause
exit /b 1

:check_installation
echo.
echo [INFO] Verifying installation...
python -c "import flask, flask_cors, pydub; print('All dependencies installed successfully')"
if !errorlevel! equ 0 (
    echo [SUCCESS] All Python dependencies are working correctly
) else (
    echo [ERROR] Some dependencies are missing or not working
    echo [INFO] Please run this script again or install manually
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Dependency installation completed successfully!
echo [INFO] You can now run START_APP.bat to start the application
echo.
pause
exit /b 0