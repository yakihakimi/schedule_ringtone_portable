@echo off
REM Rules applied
echo ========================================
echo Portable App Setup with FFmpeg
echo ========================================
echo.

echo This script will set up the portable app with all dependencies including FFmpeg.
echo.

REM Check if Python is available
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo.
    echo [INFO] Attempting automatic Python installation...
    echo [INFO] This will download and install Python 3.12.4 automatically.
    echo.
    
    REM Try to run the enhanced Python installation script
    if exist "install_python_enhanced.bat" (
        echo [INFO] Running enhanced Python installer...
        call install_python_enhanced.bat
        if %errorlevel% neq 0 (
            echo [ERROR] Enhanced Python installation failed!
            echo [INFO] Trying fallback installer...
            if exist "install_python_auto.bat" (
                call install_python_auto.bat
                if %errorlevel% neq 0 (
                    echo [ERROR] Automatic Python installation failed!
                    echo [INFO] Please install Python 3.12.4 manually from: https://www.python.org/downloads/
                    echo [INFO] Make sure to check "Add Python to PATH" during installation
                    echo.
                    pause
                    exit /b 1
                )
            ) else (
                echo [ERROR] No Python installer found!
                echo [INFO] Please install Python 3.12.4 manually from: https://www.python.org/downloads/
                echo [INFO] Make sure to check "Add Python to PATH" during installation
                echo.
                pause
                exit /b 1
            )
        )
    ) else (
        echo [ERROR] Enhanced Python installer not found!
        echo [INFO] Please install Python 3.12.4 manually from: https://www.python.org/downloads/
        echo [INFO] Make sure to check "Add Python to PATH" during installation
        echo.
        pause
        exit /b 1
    )
    
    REM Verify Python is now available
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python installation verification failed!
        echo [INFO] Please restart your terminal and try again.
        echo [INFO] If problems persist, install Python manually from: https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )
)

echo Python is available.
echo.

REM Check if Node.js is available
echo Checking Node.js installation...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js is not installed or not in PATH.
    echo Please install Node.js from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo Node.js is available.
echo.

REM Install Python dependencies
echo Installing Python dependencies...
cd backend
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install Python dependencies.
    echo.
    pause
    exit /b 1
)
cd ..
echo Python dependencies installed successfully.
echo.

REM Install Node.js dependencies
echo Installing Node.js dependencies...
npm install
if %errorlevel% neq 0 (
    echo Failed to install Node.js dependencies.
    echo.
    pause
    exit /b 1
)
echo Node.js dependencies installed successfully.
echo.

REM Install FFmpeg
echo Installing FFmpeg...
call INSTALL_FFMPEG.bat
if %errorlevel% neq 0 (
    echo FFmpeg installation failed, but the app will still work with WAV files.
    echo.
)

echo.
echo ========================================
echo Setup completed!
echo ========================================
echo.
echo The portable app is now ready to use.
echo.
echo To start the app:
echo 1. Run START_APP.bat
echo 2. Or run START_APP.ps1 in PowerShell
echo.
echo Features available:
echo - WAV ringtone creation (always available)
echo - MP3 conversion (if FFmpeg installed successfully)
echo - Audio file upload and editing
echo - Windows Task Scheduler integration
echo.
pause
