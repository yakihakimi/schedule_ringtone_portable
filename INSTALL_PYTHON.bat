@echo off
REM Rules applied
REM Simple Python installation launcher
REM This script will automatically download and install Python if it's not already installed

echo ========================================
echo Python Auto-Installer
echo ========================================
echo.

REM Check if Python is already installed
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Python is already installed:
    python --version
    echo.
    echo [INFO] Python is ready to use!
    echo [INFO] You can now run: SETUP_WITH_FFMPEG.bat
    echo.
    pause
    exit /b 0
)

echo [INFO] Python not found. Starting automatic installation...
echo.

REM Check if we're in the right directory
if not exist "install_python_auto.bat" (
    echo [ERROR] Python installer script not found!
    echo [INFO] Please make sure you're running this from the portable_app directory.
    echo.
    pause
    exit /b 1
)

REM Run the automatic Python installation
echo [INFO] Running Python auto-installer...
call install_python_auto.bat

REM Check if installation was successful
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo [SUCCESS] Python installation completed!
    echo ========================================
    echo.
    echo [INFO] Python version:
    python --version
    echo.
    echo [INFO] You can now run: SETUP_WITH_FFMPEG.bat
    echo.
) else (
    echo.
    echo ========================================
    echo [ERROR] Python installation failed!
    echo ========================================
    echo.
    echo [INFO] Please try the following:
    echo [INFO] 1. Restart your terminal
    echo [INFO] 2. Run this script again
    echo [INFO] 3. Download Python manually from: https://www.python.org/downloads/
    echo.
)

pause
