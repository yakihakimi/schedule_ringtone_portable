@echo off
REM Rules applied
setlocal enabledelayedexpansion

title Portable App Setup Verification

echo ========================================
echo    Portable App Setup Verification
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend\server.py" (
    echo [ERROR] This script must be run from the portable_app directory
    echo [INFO] Please navigate to the portable_app folder and run verify_setup.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Verifying portable app setup...
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo [INFO] Please install Python 3.12.4 from: https://www.python.org/downloads/
    goto :end_error
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [SUCCESS] Python !PYTHON_VERSION! found
)

REM Check Node.js
echo [2/5] Checking Node.js installation...
node --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo [INFO] Please install Node.js LTS from: https://nodejs.org/
    goto :end_error
) else (
    for /f %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo [SUCCESS] Node.js !NODE_VERSION! found
)

REM Check Python dependencies
echo [3/5] Checking Python dependencies...
python -c "import flask, flask_cors, pydub; print('All Python dependencies OK')" 2>nul
if !errorlevel! neq 0 (
    echo [WARNING] Python dependencies are missing or incomplete
    echo [INFO] Run: install_dependencies.bat
    set DEPS_MISSING=1
) else (
    echo [SUCCESS] All Python dependencies are installed
)

REM Check Node.js dependencies
echo [4/5] Checking Node.js dependencies...
if not exist "node_modules" (
    echo [WARNING] Node.js dependencies are missing
    echo [INFO] Run: npm install
    set NODE_DEPS_MISSING=1
) else (
    echo [SUCCESS] Node.js dependencies are installed
)

REM Check FFmpeg
echo [5/5] Checking FFmpeg installation...
if exist "ffmpeg\bin\ffmpeg.exe" (
    echo [SUCCESS] FFmpeg is available
) else (
    echo [WARNING] FFmpeg not found - MP3 conversion will be limited
    echo [INFO] Run: INSTALL_FFMPEG.bat (optional)
)

echo.
echo ========================================
echo    Setup Verification Results
echo ========================================

if defined DEPS_MISSING (
    echo [ACTION REQUIRED] Python dependencies need to be installed
    echo [SOLUTION] Run: install_dependencies.bat
    echo.
)

if defined NODE_DEPS_MISSING (
    echo [ACTION REQUIRED] Node.js dependencies need to be installed
    echo [SOLUTION] Run: npm install
    echo.
)

if not defined DEPS_MISSING if not defined NODE_DEPS_MISSING (
    echo [SUCCESS] Setup verification completed successfully!
    echo [INFO] You can now run: START_APP.bat
    echo.
    echo [NEXT STEPS]
    echo 1. Run: START_APP.bat
    echo 2. Open: http://localhost:3000
    echo 3. If you get CORS errors, run: test_backend.bat
    echo.
) else (
    echo [SETUP INCOMPLETE] Please install missing dependencies first
    echo.
)

pause
exit /b 0

:end_error
echo.
echo [SETUP FAILED] Please install missing prerequisites first
echo.
pause
exit /b 1
