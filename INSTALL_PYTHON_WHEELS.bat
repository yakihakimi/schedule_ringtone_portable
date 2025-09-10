@echo off
REM Rules applied
setlocal enabledelayedexpansion

title Install Python Dependencies with Precompiled Wheels

echo ========================================
echo   Install Python Dependencies with Wheels
echo ========================================
echo This script installs Python dependencies using precompiled wheels
echo to avoid build errors and compilation issues.
echo.

REM Check if we're in the right directory
if not exist "install_python_wheels.py" (
    echo [ERROR] This script must be run from the portable_app directory
    echo [INFO] Please navigate to the portable_app folder and run INSTALL_PYTHON_WHEELS.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Starting Python wheel installation...
echo [INFO] This will use precompiled wheels to avoid build errors
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo [INFO] Please install Python 3.12.4 first
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Python found
echo.

REM Run the wheel installation script
echo [INFO] Running Python wheel installation script...
python install_python_wheels.py

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Python wheel installation completed!
    echo [INFO] You can now run CREATE_STANDALONE_EXECUTABLE.bat
    echo.
) else (
    echo.
    echo [ERROR] Python wheel installation failed!
    echo [INFO] Check the output above for error details
    echo [INFO] You may need to install packages manually
    echo.
)

echo [INFO] This window will close in 5 seconds...
timeout /t 5 /nobreak >nul
exit /b 0
