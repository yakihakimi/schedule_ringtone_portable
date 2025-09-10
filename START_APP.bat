@echo off
REM Rules applied
setlocal enabledelayedexpansion

title Portable Ringtone Creator - Universal Launcher

echo ========================================
echo    Portable Ringtone Creator App
echo ========================================
echo Universal Launcher - One-Click Start
echo.

REM Set colors for better output
color 0A

REM Check if we're in the right directory
if not exist "backend\server.py" (
    echo [ERROR] This script must be run from the portable_app directory
    echo [INFO] Please navigate to the portable_app folder and run START_APP.bat
    echo.
    pause
    exit /b 1
)

echo [INFO] Performing comprehensive system check...
echo.

REM Check Python installation
echo [1/4] Checking Python installation...
python --version >nul 2>&1
echo [DEBUG] Python check error level: %errorlevel%
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo [INFO] Attempting automatic Python installation...
    echo [INFO] This will check for local installer or download Python 3.12.4 automatically.
    echo.
    
    REM Set flag to track installation success
    set PYTHON_INSTALLED=0
    
    REM First check if we have a local Python installer
    if exist "python-installer-local.exe" (
        echo [INFO] Found local Python installer: python-installer-local.exe
        echo [INFO] Running local Python installer...
        echo [INFO] Installing Python with silent mode and adding to PATH...
        
        REM Run the local installer with silent installation
        python-installer-local.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_tkinter=1 Include_launcher=1
        
        REM Wait for installation to complete
        echo [INFO] Waiting for installation to complete...
        timeout /t 10 /nobreak >nul
        
        REM Verify Python is now available
        python --version >nul 2>&1
        if %errorlevel% equ 0 (
            echo [SUCCESS] Python installation completed successfully using local installer!
            for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
            echo [SUCCESS] Python !PYTHON_VERSION! is now available
            set PYTHON_INSTALLED=1
        ) else (
            echo [WARNING] Local installer may not have completed yet, will try other methods...
        )
    )
    
    REM If local installer didn't work, try downloading
    if !PYTHON_INSTALLED! equ 0 (
        if exist "download_python_offline.bat" (
            echo [INFO] Running Python offline installer downloader...
            echo [INFO] This will download Python 3.12.4 installer for offline installation.
            echo.
            call download_python_offline.bat
            if %errorlevel% equ 0 (
                REM Check if download was successful and try to install
                if exist "python-installer-local.exe" (
                    echo [INFO] Download successful! Installing Python...
                    echo [INFO] Installing Python with silent mode and adding to PATH...
                    
                    REM Run the downloaded installer with silent installation
                    python-installer-local.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_tkinter=1 Include_launcher=1
                    
                    REM Wait for installation to complete
                    echo [INFO] Waiting for installation to complete...
                    timeout /t 10 /nobreak >nul
                    
                    REM Verify Python is now available
                    python --version >nul 2>&1
                    if %errorlevel% equ 0 (
                        echo [SUCCESS] Python installation completed successfully using downloaded installer!
                        for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
                        echo [SUCCESS] Python !PYTHON_VERSION! is now available
                        set PYTHON_INSTALLED=1
                    ) else (
                        echo [WARNING] Downloaded installer may not have completed yet, will try enhanced installer...
                    )
                ) else (
                    echo [WARNING] Download script completed but installer not found, will try enhanced installer...
                )
            ) else (
                echo [WARNING] Download failed, will try enhanced installer...
            )
        ) else (
            echo [WARNING] Download script not found, will try enhanced installer...
        )
    )
    
    REM If still not installed, try enhanced installer
    if !PYTHON_INSTALLED! equ 0 (
        if exist "install_python_enhanced.bat" (
            echo [INFO] Running enhanced Python installer...
            call install_python_enhanced.bat
            if %errorlevel% equ 0 (
                REM Verify Python is now available
                python --version >nul 2>&1
                if %errorlevel% equ 0 (
                    echo [SUCCESS] Python installation completed successfully using enhanced installer!
                    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
                    echo [SUCCESS] Python !PYTHON_VERSION! is now available
                    set PYTHON_INSTALLED=1
                )
            )
        )
    )
    
    REM Final check - if still not installed, show error
    if !PYTHON_INSTALLED! equ 0 (
        echo [ERROR] All automatic Python installation methods failed!
        echo [INFO] Please install Python 3.12.4 manually from: https://www.python.org/downloads/
        echo [INFO] Make sure to check "Add Python to PATH" during installation
        echo.
        echo [INFO] After installing Python, run this script again.
        echo.
        pause
        exit /b 1
    )
) else (
    echo [DEBUG] Python found, skipping installation block
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo [SUCCESS] Python !PYTHON_VERSION! found
    echo [DEBUG] Continuing to Node.js check...
)

REM Check Node.js installation
echo [2/4] Checking Node.js installation...
node --version >nul 2>&1
echo [DEBUG] Node.js check error level: %errorlevel%
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo.
    echo [INFO] Attempting automatic Node.js installation...
    echo [INFO] This will check for local installer or download Node.js LTS automatically.
    echo.
    
    REM Set flag to track installation success
    set NODEJS_INSTALLED=0
    
    REM First check if we have a local Node.js installer
    if exist "nodejs-installer-local.msi" (
        echo [INFO] Found local Node.js installer: nodejs-installer-local.msi
        echo [INFO] Running local Node.js installer...
        echo [INFO] Installing Node.js with interactive mode - please follow the wizard...
        
        REM Run the local installer with interactive installation
        echo [INFO] Starting Node.js installer - please follow the installation wizard...
        start /wait "Node.js Installer" "nodejs-installer-local.msi"
        
        REM Wait for installation to complete
        echo [INFO] Installation completed, refreshing PATH and verifying Node.js availability...
        timeout /t 3 /nobreak >nul
        
        REM Note: PATH will be refreshed automatically in new processes
        
        REM Try multiple verification methods
        node --version >nul 2>&1
        if %errorlevel% equ 0 (
            echo [SUCCESS] Node.js installation completed successfully using local installer!
            for /f %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
            echo [SUCCESS] Node.js !NODE_VERSION! is now available
            set NODEJS_INSTALLED=1
        ) else (
            REM Try checking common Node.js installation paths
            if exist "C:\Program Files\nodejs\node.exe" (
                echo [SUCCESS] Node.js found in Program Files, updating PATH...
                set "PATH=%PATH%;C:\Program Files\nodejs"
                node --version >nul 2>&1
                if %errorlevel% equ 0 (
                    echo [SUCCESS] Node.js installation completed successfully using local installer!
                    for /f %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
                    echo [SUCCESS] Node.js !NODE_VERSION! is now available
                    set NODEJS_INSTALLED=1
                ) else (
                    echo [WARNING] Node.js installed but not accessible, will try other methods...
                )
            ) else (
                echo [WARNING] Local installer may not have completed yet, will try other methods...
            )
        )
    )
    
    REM If local installer didn't work, try downloading
    if !NODEJS_INSTALLED! equ 0 (
        if exist "download_nodejs_offline.bat" (
            echo [INFO] Running Node.js offline installer downloader...
            echo [INFO] This will download Node.js LTS installer for offline installation.
            echo.
            call download_nodejs_offline.bat --from-start-app
            if %errorlevel% equ 0 (
                REM Check if download was successful and try to install
                if exist "nodejs-installer-local.msi" (
                    echo [INFO] Download successful! Installing Node.js...
                    echo [INFO] Installing Node.js with interactive mode - please follow the wizard...
                    
                    REM Run the downloaded installer with interactive installation
                    echo [INFO] Starting Node.js installer - please follow the installation wizard...
                    start /wait "Node.js Installer" "nodejs-installer-local.msi"
                    
                    REM Wait for installation to complete
                    echo [INFO] Installation completed, refreshing PATH and verifying Node.js availability...
                    timeout /t 3 /nobreak >nul
                    
                    REM Refresh PATH environment variable
                    call refreshenv >nul 2>&1
                    
                    REM Try multiple verification methods
                    node --version >nul 2>&1
                    if %errorlevel% equ 0 (
                        echo [SUCCESS] Node.js installation completed successfully using downloaded installer!
                        for /f %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
                        echo [SUCCESS] Node.js !NODE_VERSION! is now available
                        set NODEJS_INSTALLED=1
                    ) else (
                        REM Try checking common Node.js installation paths
                        if exist "C:\Program Files\nodejs\node.exe" (
                            echo [SUCCESS] Node.js found in Program Files, updating PATH...
                            set "PATH=%PATH%;C:\Program Files\nodejs"
                            node --version >nul 2>&1
                            if %errorlevel% equ 0 (
                                echo [SUCCESS] Node.js installation completed successfully using downloaded installer!
                                for /f %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
                                echo [SUCCESS] Node.js !NODE_VERSION! is now available
                                set NODEJS_INSTALLED=1
                            ) else (
                                echo [WARNING] Node.js installed but not accessible, will try manual installation...
                            )
                        ) else (
                            echo [WARNING] Downloaded installer may not have completed yet, will try manual installation...
                        )
                    )
                ) else (
                    echo [WARNING] Download script completed but installer not found, will try manual installation...
                )
            ) else (
                echo [WARNING] Download failed, will try manual installation...
            )
        ) else (
            echo [WARNING] Download script not found, will try manual installation...
        )
    )
    
    REM If still not installed, show manual installation instructions
    if !NODEJS_INSTALLED! equ 0 (
        echo [ERROR] All automatic Node.js installation methods failed!
        echo [INFO] Please install Node.js LTS manually from: https://nodejs.org/
        echo [INFO] Make sure to check "Add to PATH" during installation
        echo.
        echo [INFO] After installing Node.js, run this script again.
        echo.
        echo [INFO] You can also try running the setup script: SETUP_WITH_FFMPEG.bat
        echo.
        pause
        exit /b 1
    )
) else (
    echo [DEBUG] Node.js found, skipping installation block
    for /f %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    echo [SUCCESS] Node.js !NODE_VERSION! found
    echo [DEBUG] Continuing to Python dependencies check...
)

REM Check Python dependencies
echo [3/4] Checking Python dependencies...
python -c "import flask_cors" >nul 2>&1
if !errorlevel! neq 0 (
    echo [WARNING] Python dependencies not found, installing...
    cd backend
    
    REM First install essential build tools to fix distutils.msvccompiler error
    echo [INFO] Installing essential build tools first to fix distutils compatibility...
    
    REM Install setuptools
    pip install --upgrade setuptools --verbose
    if !errorlevel! equ 0 (
        echo [SUCCESS] setuptools installed successfully
    ) else (
        echo [WARNING] Failed to install setuptools, continuing anyway...
    )
    
    REM Install wheel
    pip install --upgrade wheel --verbose
    if !errorlevel! equ 0 (
        echo [SUCCESS] wheel installed successfully
    ) else (
        echo [WARNING] Failed to install wheel, continuing anyway...
    )
    
    REM Install pywin32 for Windows compatibility
    pip install pywin32 --verbose
    if !errorlevel! equ 0 (
        echo [SUCCESS] pywin32 installed successfully
    ) else (
        echo [WARNING] Failed to install pywin32, continuing anyway...
    )
    
    REM Install packages individually with error handling
    echo [INFO] Installing Python packages individually with error handling...
    
    REM Install Flask
    echo [INFO] Installing Flask...
    pip install --proxy http://proxy-enclave.altera.com:912 Flask==2.3.3 --verbose
    if !errorlevel! equ 0 (
        echo [SUCCESS] Flask installed successfully
    ) else (
        echo [WARNING] Failed to install Flask with proxy, trying without proxy...
        pip install Flask==2.3.3 --verbose
        if !errorlevel! equ 0 (
            echo [SUCCESS] Flask installed successfully without proxy
        ) else (
            echo [ERROR] Failed to install Flask - continuing without it
        )
    )
    
    REM Install Flask-CORS
    echo [INFO] Installing Flask-CORS...
    pip install --proxy http://proxy-enclave.altera.com:912 Flask-CORS==4.0.0 --verbose
    if !errorlevel! equ 0 (
        echo [SUCCESS] Flask-CORS installed successfully
    ) else (
        echo [WARNING] Failed to install Flask-CORS with proxy, trying without proxy...
        pip install Flask-CORS==4.0.0 --verbose
        if !errorlevel! equ 0 (
            echo [SUCCESS] Flask-CORS installed successfully without proxy
        ) else (
            echo [ERROR] Failed to install Flask-CORS - continuing without it
        )
    )
    
    REM Install Werkzeug
    echo [INFO] Installing Werkzeug...
    pip install --proxy http://proxy-enclave.altera.com:912 Werkzeug==2.3.7 --verbose
    if !errorlevel! equ 0 (
        echo [SUCCESS] Werkzeug installed successfully
    ) else (
        echo [WARNING] Failed to install Werkzeug with proxy, trying without proxy...
        pip install Werkzeug==2.3.7 --verbose
        if !errorlevel! equ 0 (
            echo [SUCCESS] Werkzeug installed successfully without proxy
        ) else (
            echo [ERROR] Failed to install Werkzeug - continuing without it
        )
    )
    
    REM Install pydub
    echo [INFO] Installing pydub...
    pip install --proxy http://proxy-enclave.altera.com:912 pydub==0.25.1 --verbose
    if !errorlevel! equ 0 (
        echo [SUCCESS] pydub installed successfully
    ) else (
        echo [WARNING] Failed to install pydub with proxy, trying without proxy...
        pip install pydub==0.25.1 --verbose
        if !errorlevel! equ 0 (
            echo [SUCCESS] pydub installed successfully without proxy
        ) else (
            echo [ERROR] Failed to install pydub - continuing without it
        )
    )
    
    REM Install pygame (this is the problematic one)
    echo [INFO] Installing pygame...
    pip install --proxy http://proxy-enclave.altera.com:912 pygame==2.6.0 --verbose
    if !errorlevel! equ 0 (
        echo [SUCCESS] pygame installed successfully
    ) else (
        echo [WARNING] Failed to install pygame with proxy, trying without proxy...
        pip install pygame==2.6.0 --verbose
        if !errorlevel! equ 0 (
            echo [SUCCESS] pygame installed successfully without proxy
        ) else (
            echo [ERROR] Failed to install pygame - trying alternative installation...
            echo [INFO] Trying to install pygame with pre-compiled wheel...
            pip install --only-binary=all pygame==2.6.0 --verbose
            if !errorlevel! equ 0 (
                echo [SUCCESS] pygame installed successfully with pre-compiled wheel
            ) else (
                echo [ERROR] Failed to install pygame - app will work without audio playback
                echo [INFO] You can install pygame manually later for audio features
            )
        )
    )
    
    REM Install requests
    echo [INFO] Installing requests...
    pip install --proxy http://proxy-enclave.altera.com:912 requests==2.31.0 --verbose
    if !errorlevel! equ 0 (
        echo [SUCCESS] requests installed successfully
    ) else (
        echo [WARNING] Failed to install requests with proxy, trying without proxy...
        pip install requests==2.31.0 --verbose
        if !errorlevel! equ 0 (
            echo [SUCCESS] requests installed successfully without proxy
        ) else (
            echo [ERROR] Failed to install requests - continuing without it
        )
    )
    
    REM Install python-dateutil
    echo [INFO] Installing python-dateutil...
    pip install --proxy http://proxy-enclave.altera.com:912 python-dateutil==2.8.2 --verbose
    if !errorlevel! equ 0 (
        echo [SUCCESS] python-dateutil installed successfully
    ) else (
        echo [WARNING] Failed to install python-dateutil with proxy, trying without proxy...
        pip install python-dateutil==2.8.2 --verbose
        if !errorlevel! equ 0 (
            echo [SUCCESS] python-dateutil installed successfully without proxy
        ) else (
            echo [ERROR] Failed to install python-dateutil - continuing without it
        )
    )
    
    cd ..
    echo [SUCCESS] Python dependencies installation completed (some packages may have failed)
    echo [INFO] The app will continue to run with available packages
) else (
    echo [SUCCESS] Python dependencies found
)

REM Check Node.js dependencies
echo [4/4] Checking Node.js dependencies...
if not exist "node_modules" (
    echo [WARNING] Node.js dependencies not found, installing...
    npm install
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install Node.js dependencies
        echo [INFO] Please check your internet connection and try again
        pause
        exit /b 1
    )
    echo [SUCCESS] Node.js dependencies installed successfully
) else (
    echo [SUCCESS] Node.js dependencies found
)

REM Check FFmpeg installation
echo [5/5] Checking FFmpeg...
if not exist "ffmpeg\bin\ffmpeg.exe" (
    echo [WARNING] FFmpeg not found, attempting automatic installation...
    echo [INFO] This will enable MP3 conversion features.
    echo.
    if exist "INSTALL_FFMPEG.bat" (
        call INSTALL_FFMPEG.bat
        if !errorlevel! neq 0 (
            echo [WARNING] FFmpeg installation failed, but the app will work with WAV files
            echo [INFO] You can install FFmpeg manually later for MP3 conversion
        ) else (
            echo [SUCCESS] FFmpeg installed successfully
        )
    ) else (
        echo [WARNING] FFmpeg installer not found, app will work with WAV files only
    )
) else (
    echo [SUCCESS] FFmpeg found
)

REM Check if ports are available
echo.
echo [INFO] Checking port availability...
netstat -an | findstr ":3000" >nul 2>&1
if !errorlevel! equ 0 (
    echo [WARNING] Port 3000 is already in use
    echo [INFO] Please close other applications using port 3000
    echo.
)

netstat -an | findstr ":5000" >nul 2>&1
if !errorlevel! equ 0 (
    echo [WARNING] Port 5000 is already in use
    echo [INFO] Please close other applications using port 5000
    echo.
)

echo.
echo ========================================
echo    Starting Portable Ringtone Creator
echo ========================================
echo.

REM Try different startup methods in order of preference
echo [INFO] Attempting to start the application...
echo.

REM Method 1: Direct startup (most reliable)
echo [Method 1] Starting application directly...
echo [INFO] Starting backend server...
start "Ringtone Backend" cmd /k "cd /d %~dp0backend && python server.py"

echo [INFO] Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo [INFO] Starting frontend server...
start "Ringtone Frontend" cmd /k "cd /d %~dp0 && npm start"

echo [INFO] Waiting for frontend to start...
timeout /t 8 /nobreak >nul

echo [SUCCESS] Application started successfully!
echo.
echo [INFO] Access the app at: http://localhost:3000
echo [INFO] Backend API at: http://localhost:5000
echo.
echo [INFO] Tips:
echo - The app works with WAV files even without FFmpeg
echo - FFmpeg enables MP3 conversion features
echo - Check the README.md for detailed usage instructions
echo.
echo [INFO] This window will close in 10 seconds...
timeout /t 10 /nobreak >nul
exit /b 0