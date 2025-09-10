@echo off
REM Rules applied
setlocal enabledelayedexpansion

title Install Python Dependencies with Proxy

echo ========================================
echo   Install Python Dependencies with Proxy
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend\requirements.txt" (
    echo [ERROR] This script must be run from the portable_app directory
    echo [INFO] Please navigate to the portable_app folder and run install_python_deps.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Installing Python dependencies with proxy support...
echo [INFO] Proxy: http://proxy-enclave.altera.com:912
echo.

REM Create python_packages directory
if not exist "python_packages" mkdir python_packages

echo [INFO] Method 1: Installing with proxy and timeout...
pip install --proxy http://proxy-enclave.altera.com:912 --target python_packages -r backend\requirements.txt --timeout 120

if %errorlevel% equ 0 (
    echo [SUCCESS] Python dependencies installed successfully!
    echo [INFO] Dependencies are now in the python_packages directory
    echo.
    goto :success
)

echo [WARNING] Method 1 failed, trying Method 2...
echo [INFO] Method 2: Installing with proxy, timeout, and retries...
pip install --proxy http://proxy-enclave.altera.com:912 --target python_packages -r backend\requirements.txt --timeout 120 --retries 3

if %errorlevel% equ 0 (
    echo [SUCCESS] Python dependencies installed successfully!
    echo [INFO] Dependencies are now in the python_packages directory
    echo.
    goto :success
)

echo [WARNING] Method 2 failed, trying Method 3...
echo [INFO] Method 3: Installing without proxy...
pip install --target python_packages -r backend\requirements.txt --timeout 120

if %errorlevel% equ 0 (
    echo [SUCCESS] Python dependencies installed successfully!
    echo [INFO] Dependencies are now in the python_packages directory
    echo.
    goto :success
)

echo [ERROR] All installation methods failed!
echo [INFO] Please check your network connection and proxy settings
echo [INFO] You can try running the command manually:
echo [INFO] pip install --proxy http://proxy-enclave.altera.com:912 --target python_packages -r backend\requirements.txt
echo.
pause
exit /b 1

:success
echo [INFO] You can now run CREATE_STANDALONE_EXECUTABLE.bat
echo.
pause
exit /b 0
