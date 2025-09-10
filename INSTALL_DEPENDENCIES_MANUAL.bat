@echo off
REM Rules applied
setlocal enabledelayedexpansion

title Manual Dependencies Installation with Proxy Support

echo ========================================
echo   Manual Dependencies Installation
echo ========================================
echo This script installs Python and Node.js dependencies
echo with proxy support before creating the standalone executable
echo.

REM Check if we're in the right directory
if not exist "install_dependencies_manual.py" (
    echo [ERROR] This script must be run from the portable_app directory
    echo [INFO] Please navigate to the portable_app folder and run INSTALL_DEPENDENCIES_MANUAL.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Starting manual dependencies installation...
echo [INFO] This will install dependencies with proxy support
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

REM Check Node.js installation
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo [INFO] Please install Node.js LTS first
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Node.js found
echo.

REM Run the manual installation script
echo [INFO] Running manual dependencies installation script...
python install_dependencies_manual.py

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Manual dependencies installation completed!
    echo [INFO] You can now run CREATE_STANDALONE_EXECUTABLE.bat
    echo.
) else (
    echo.
    echo [ERROR] Manual dependencies installation failed!
    echo [INFO] Check the output above for error details
    echo.
)

echo [INFO] This window will close in 5 seconds...
timeout /t 5 /nobreak >nul
exit /b 0
