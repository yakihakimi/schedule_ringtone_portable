@echo off
REM Rules applied
REM Setup script for portable ringtone app

echo ========================================
echo    Ringtone Creator App Setup
echo ========================================
echo.

REM Get the directory where this script is located
set "APP_DIR=%~dp0"
echo App directory: %APP_DIR%

echo This script will help you set up the Ringtone Creator App
echo.

REM Check if Python is available
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.7+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    echo After installing Python, run this setup script again.
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo SUCCESS: Python %PYTHON_VERSION% is installed
)

REM Check if Node.js is available
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo.
    echo Please install Node.js LTS from: https://nodejs.org/
    echo Make sure to check "Add to PATH" during installation
    echo.
    echo After installing Node.js, run this setup script again.
    pause
    exit /b 1
) else (
    for /f %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo SUCCESS: Node.js %NODE_VERSION% is installed
)

echo.
echo SUCCESS: All requirements are installed!
echo.

REM Install Python dependencies
echo Installing Python dependencies...
cd /d "%APP_DIR%backend"
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo SUCCESS: Python dependencies installed

REM Install Node.js dependencies
echo Installing Node.js dependencies...
cd /d "%APP_DIR%"
npm install
if errorlevel 1 (
    echo ERROR: Failed to install Node.js dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo SUCCESS: Node.js dependencies installed

echo.
echo ========================================
echo SUCCESS: Setup Complete!
echo ========================================
echo.
echo You can now run the app using:
echo   - START_APP.bat (Windows batch file)
echo   - START_APP.ps1 (PowerShell script)
echo.
echo The app will be available at: http://localhost:3000
echo.
pause
