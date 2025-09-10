@echo off
REM Rules applied
setlocal enabledelayedexpansion

title Install Python Dependencies with Wheels (Simple)

echo ========================================
echo   Install Python Dependencies with Wheels
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend\requirements.txt" (
    echo [ERROR] This script must be run from the portable_app directory
    echo [INFO] Please navigate to the portable_app folder and run install_wheels_simple.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Installing Python dependencies with precompiled wheels...
echo [INFO] This avoids build errors and compilation issues
echo [INFO] Proxy: http://proxy-enclave.altera.com:912
echo.

REM Create python_packages directory
if not exist "python_packages" mkdir python_packages

echo [INFO] Method 1: Installing with precompiled wheels only...
pip install --proxy http://proxy-enclave.altera.com:912 --target python_packages -r backend\requirements.txt --only-binary=all --timeout 120

if %errorlevel% equ 0 (
    echo [SUCCESS] Python dependencies installed successfully with wheels!
    echo [INFO] Dependencies are now in the python_packages directory
    echo.
    goto :success
)

echo [WARNING] Method 1 failed, trying Method 2...
echo [INFO] Method 2: Installing with precompiled wheels and retries...
pip install --proxy http://proxy-enclave.altera.com:912 --target python_packages -r backend\requirements.txt --only-binary=all --timeout 120 --retries 3

if %errorlevel% equ 0 (
    echo [SUCCESS] Python dependencies installed successfully with wheels!
    echo [INFO] Dependencies are now in the python_packages directory
    echo.
    goto :success
)

echo [WARNING] Method 2 failed, trying Method 3...
echo [INFO] Method 3: Installing without proxy with wheels...
pip install --target python_packages -r backend\requirements.txt --only-binary=all --timeout 120

if %errorlevel% equ 0 (
    echo [SUCCESS] Python dependencies installed successfully with wheels!
    echo [INFO] Dependencies are now in the python_packages directory
    echo.
    goto :success
)

echo [WARNING] Method 3 failed, trying Method 4...
echo [INFO] Method 4: Installing with prefer-binary (allows source if needed)...
pip install --proxy http://proxy-enclave.altera.com:912 --target python_packages -r backend\requirements.txt --prefer-binary --timeout 120

if %errorlevel% equ 0 (
    echo [SUCCESS] Python dependencies installed successfully!
    echo [INFO] Dependencies are now in the python_packages directory
    echo.
    goto :success
)

echo [ERROR] All wheel installation methods failed!
echo [INFO] This might be due to:
echo   - Network connectivity issues
echo   - Proxy configuration problems
echo   - Package compatibility issues
echo   - Missing precompiled wheels for your Python version
echo.
echo [INFO] You can try installing packages individually:
echo   pip install --proxy http://proxy-enclave.altera.com:912 --target python_packages flask --only-binary=all
echo   pip install --proxy http://proxy-enclave.altera.com:912 --target python_packages flask-cors --only-binary=all
echo   pip install --proxy http://proxy-enclave.altera.com:912 --target python_packages pydub --only-binary=all
echo.
pause
exit /b 1

:success
echo [INFO] You can now run CREATE_STANDALONE_EXECUTABLE.bat
echo.
pause
exit /b 0
