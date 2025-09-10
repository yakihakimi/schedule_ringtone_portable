@echo off
REM Rules applied
echo ========================================
echo Testing FFmpeg Installation
echo ========================================
echo.

echo Testing Python installation script...
python install_ffmpeg_auto.py
if %errorlevel% equ 0 (
    echo Python installation successful!
    echo.
    echo Testing FFmpeg...
    if exist "ffmpeg\bin\ffmpeg.exe" (
        "ffmpeg\bin\ffmpeg.exe" -version
        echo.
        echo FFmpeg is working correctly!
    ) else (
        echo FFmpeg executable not found after installation
    )
) else (
    echo Python installation failed, trying PowerShell...
    echo.
    powershell -ExecutionPolicy Bypass -File install_ffmpeg_auto.ps1
    if %errorlevel% equ 0 (
        echo PowerShell installation successful!
        echo.
        echo Testing FFmpeg...
        if exist "ffmpeg\bin\ffmpeg.exe" (
            "ffmpeg\bin\ffmpeg.exe" -version
            echo.
            echo FFmpeg is working correctly!
        ) else (
            echo FFmpeg executable not found after installation
        )
    ) else (
        echo Both installation methods failed
    )
)

echo.
echo Press any key to continue...
pause >nul
