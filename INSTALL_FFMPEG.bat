@echo off
REM Rules applied
echo ========================================
echo FFmpeg Installation for Portable App
echo ========================================
echo.

REM Check if ffmpeg is already installed
if exist "ffmpeg\bin\ffmpeg.exe" (
    echo FFmpeg is already installed in portable_app\ffmpeg\bin\
    echo Testing installation...
    "ffmpeg\bin\ffmpeg.exe" -version >nul 2>&1
    if %errorlevel% equ 0 (
        echo FFmpeg is working correctly!
        echo You can now use MP3 conversion features.
        echo.
        pause
        exit /b 0
    ) else (
        echo FFmpeg found but may not be working properly.
        echo Reinstalling FFmpeg automatically...
        echo.
    )
)

echo FFmpeg not found. Starting automatic installation...
echo.

REM Try Python installation first
echo Attempting Python-based installation...
python install_ffmpeg_auto.py
if %errorlevel% equ 0 (
    echo.
    echo FFmpeg installed successfully using Python!
    echo MP3 conversion features are now available.
    echo.
    pause
    exit /b 0
)

echo Python installation failed, trying PowerShell...
echo.

REM Try PowerShell installation
powershell -ExecutionPolicy Bypass -File install_ffmpeg_auto.ps1
if %errorlevel% equ 0 (
    echo.
    echo FFmpeg installed successfully using PowerShell!
    echo MP3 conversion features are now available.
    echo.
    pause
    exit /b 0
)

echo.
echo Automatic installation failed. Please install FFmpeg manually.
echo.
echo INSTRUCTIONS:
echo 1. Download FFmpeg from: https://ffmpeg.org/download.html
echo 2. Extract the ZIP file
echo 3. Copy the 'bin' folder contents to: portable_app\ffmpeg\bin\
echo 4. Ensure ffmpeg.exe is in: portable_app\ffmpeg\bin\ffmpeg.exe
echo 5. Run this script again to verify installation
echo.
echo ALTERNATIVE: Use WAV format only (no FFmpeg required)
echo The app works perfectly with WAV files without FFmpeg.
echo.
echo For detailed instructions, see: FFMPEG_INSTALLATION_GUIDE.md
echo.
pause
