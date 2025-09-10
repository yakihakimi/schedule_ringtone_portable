@echo off
REM Rules applied
REM Enhanced Python installation script with automatic download and installation
REM This script downloads and installs Python 3.12.4 if it's not already installed

echo ========================================
echo Automatic Python Installation
echo ========================================
echo.

REM Check if Python is already installed
echo [INFO] Checking for existing Python installation...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Python is already installed:
    python --version
    echo.
    echo [INFO] Checking pip...
    pip --version >nul 2>&1
    if %errorlevel% equ 0 (
        pip --version
        echo.
        echo [SUCCESS] Python installation is complete and ready to use!
        goto :end
    ) else (
        echo [WARNING] Python found but pip is not available. Reinstalling...
    )
) else (
    echo [INFO] Python not found. Proceeding with automatic installation...
)

echo.

REM Check if we have internet connectivity
echo [INFO] Checking internet connectivity...
ping -n 1 google.com >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] No internet connection detected!
    echo [INFO] Please check your internet connection and try again.
    echo.
    echo [INFO] Alternative: Please download Python manually from https://python.org
    echo [INFO] Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Internet connection verified.
echo.

REM Create temporary directory for download
set TEMP_DIR=%TEMP%\python_auto_install
if not exist "%TEMP_DIR%" mkdir "%TEMP_DIR%"

echo [INFO] Downloading Python installer...
echo.

REM Get Python 3.12.4 version
REM Using Python 3.12.4 as the required version
set PYTHON_VERSION=3.12.4
set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe
set INSTALLER_PATH=%TEMP_DIR%\python-installer.exe

echo [INFO] Downloading Python %PYTHON_VERSION% from: %PYTHON_URL%
echo [INFO] Saving to: %INSTALLER_PATH%
echo.

REM Try to download using PowerShell with proxy support
echo [INFO] Attempting download with PowerShell...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%INSTALLER_PATH%' -UseBasicParsing -TimeoutSec 300 } catch { Write-Host 'Download failed, trying with proxy...'; [System.Net.WebRequest]::DefaultWebProxy = [System.Net.WebRequest]::GetSystemWebProxy(); [System.Net.WebRequest]::DefaultWebProxy.Credentials = [System.Net.CredentialCache]::DefaultCredentials; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%INSTALLER_PATH%' -UseBasicParsing -TimeoutSec 300 } }"

if not exist "%INSTALLER_PATH%" (
    echo [ERROR] Failed to download Python installer!
    echo [INFO] Trying alternative download method...
    
    REM Try with curl as fallback
    curl -L -o "%INSTALLER_PATH%" "%PYTHON_URL%" --connect-timeout 30 --max-time 300
    
    if not exist "%INSTALLER_PATH%" (
        echo [ERROR] All download methods failed!
        echo [INFO] Please check your internet connection and try again.
        echo.
        echo [INFO] Alternative: Please download Python manually from https://python.org
        echo [INFO] Make sure to check "Add Python to PATH" during installation
        echo.
        pause
        exit /b 1
    )
)

echo [SUCCESS] Download completed successfully!
echo [INFO] File size: 
for %%A in ("%INSTALLER_PATH%") do echo %%~zA bytes
echo.

echo [INFO] Installing Python...
echo [INFO] This may take a few minutes. Please wait...
echo [INFO] Installation will be silent (no user interaction required)
echo.

REM Install Python with all necessary options
REM InstallAllUsers=1: Install for all users
REM PrependPath=1: Add Python to PATH
REM Include_pip=1: Include pip package manager
REM Include_test=0: Skip test suite to save space
REM Include_launcher=1: Include Python launcher
REM Include_doc=0: Skip documentation to save space
REM Include_tcltk=1: Include Tkinter for GUI support
"%INSTALLER_PATH%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_test=0 Include_launcher=1 Include_doc=0 Include_tcltk=1

REM Wait for installation to complete
echo [INFO] Waiting for installation to complete...
timeout /t 120 /nobreak >nul

REM Clean up installer
echo [INFO] Cleaning up temporary files...
del "%INSTALLER_PATH%" >nul 2>&1
rmdir "%TEMP_DIR%" >nul 2>&1

REM Refresh environment variables
echo [INFO] Refreshing environment variables...
call refreshenv >nul 2>&1

REM Wait a bit more for the system to recognize the new installation
timeout /t 10 /nobreak >nul

REM Check if installation was successful
echo.
echo [INFO] Verifying installation...
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
    echo [INFO] pip version:
    pip --version
    echo.
    echo [INFO] Python installation path:
    where python
    echo.
    echo [SUCCESS] Python is now ready to use!
    echo [INFO] You can now run the setup script: SETUP_WITH_FFMPEG.bat
    echo.
) else (
    echo.
    echo ========================================
    echo [WARNING] Python installation verification failed!
    echo ========================================
    echo.
    echo [INFO] This might be due to:
    echo [INFO] 1. Installation is still in progress
    echo [INFO] 2. PATH environment variable needs to be refreshed
    echo [INFO] 3. Terminal needs to be restarted
    echo.
    echo [INFO] Please try the following:
    echo [INFO] 1. Restart your command prompt or PowerShell
    echo [INFO] 2. Check if Python was installed in: C:\Program Files\Python313
    echo [INFO] 3. Manually add Python to PATH if needed
    echo [INFO] 4. Run this script again
    echo.
    echo [INFO] If problems persist, download Python manually from:
    echo [INFO] https://www.python.org/downloads/
    echo [INFO] Make sure to check "Add Python to PATH" during installation
    echo.
)

:end
echo.
echo [INFO] Installation process completed.
echo [INFO] Press any key to continue...
pause >nul
