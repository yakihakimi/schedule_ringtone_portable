@echo off
REM Rules applied
REM Script to download Node.js installer for offline installation
REM Run this on a computer with internet access, then copy the file to the target computer

REM Check if this script was called from START_APP.bat
if "%1"=="--from-start-app" (
    echo [INFO] Downloading Node.js LTS installer...
    goto :download_start
)

echo ========================================
echo Node.js Offline Installer Downloader
echo ========================================
echo.

echo [INFO] This script will download Node.js LTS installer for offline installation.
echo [INFO] Run this on a computer with internet access, then copy the file to your target computer.
echo.

:download_start

REM Check if we have internet connectivity with multiple methods
echo [INFO] Checking internet connectivity...
echo [INFO] Trying multiple connectivity tests...

REM Method 1: Try ping to Google
ping -n 1 google.com >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Internet connection verified via ping.
    goto :internet_ok
)

REM Method 2: Try ping to Cloudflare DNS
ping -n 1 1.1.1.1 >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Internet connection verified via IP ping.
    goto :internet_ok
)

REM Method 3: Try PowerShell web request test
echo [INFO] Testing with PowerShell web request...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://www.google.com' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Internet connection verified via web request.
    goto :internet_ok
)

REM Method 4: Try with proxy configuration
echo [INFO] Testing with proxy configuration...
set HTTP_PROXY=http://proxy-enclave.altera.com:912
set HTTPS_PROXY=http://proxy-enclave.altera.com:912
powershell -Command "try { $response = Invoke-WebRequest -Uri 'https://www.google.com' -UseBasicParsing -TimeoutSec 10; if ($response.StatusCode -eq 200) { exit 0 } else { exit 1 } } catch { exit 1 }" >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Internet connection verified via proxy.
    goto :internet_ok
)

REM If all methods fail
echo [ERROR] No internet connection detected with any method!
echo [INFO] Please check your internet connection and try again.
echo [INFO] If you're behind a corporate firewall, ensure proxy settings are correct.
echo.
pause
exit /b 1

:internet_ok

echo [SUCCESS] Internet connection verified.
echo.

REM Set download parameters - using Node.js LTS (Long Term Support)
set NODEJS_VERSION=20.11.0
set NODEJS_URL=https://nodejs.org/dist/v%NODEJS_VERSION%/node-v%NODEJS_VERSION%-x64.msi
set LOCAL_INSTALLER_PATH=nodejs-installer-local.msi

echo [INFO] Downloading Node.js LTS %NODEJS_VERSION% installer...
echo [INFO] Source: %NODEJS_URL%
echo [INFO] Destination: %LOCAL_INSTALLER_PATH%
echo.

REM Try to download using PowerShell with enhanced proxy support
echo [INFO] Attempting download with PowerShell...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; try { Write-Host 'Attempting direct download...'; Invoke-WebRequest -Uri '%NODEJS_URL%' -OutFile '%LOCAL_INSTALLER_PATH%' -UseBasicParsing -TimeoutSec 300 -Verbose } catch { Write-Host 'Direct download failed, trying with system proxy...'; try { [System.Net.WebRequest]::DefaultWebProxy = [System.Net.WebRequest]::GetSystemWebProxy(); [System.Net.WebRequest]::DefaultWebProxy.Credentials = [System.Net.CredentialCache]::DefaultCredentials; Invoke-WebRequest -Uri '%NODEJS_URL%' -OutFile '%LOCAL_INSTALLER_PATH%' -UseBasicParsing -TimeoutSec 300 -Verbose } catch { Write-Host 'System proxy failed, trying with corporate proxy...'; $proxy = New-Object System.Net.WebProxy('http://proxy-enclave.altera.com:912'); $proxy.Credentials = [System.Net.CredentialCache]::DefaultCredentials; [System.Net.WebRequest]::DefaultWebProxy = $proxy; Invoke-WebRequest -Uri '%NODEJS_URL%' -OutFile '%LOCAL_INSTALLER_PATH%' -UseBasicParsing -TimeoutSec 300 -Verbose } } }"

if not exist "%LOCAL_INSTALLER_PATH%" (
    echo [ERROR] PowerShell download failed. Trying with curl...
    echo [INFO] Attempting curl download with proxy support...
    curl -L -o "%LOCAL_INSTALLER_PATH%" "%NODEJS_URL%" --connect-timeout 30 --max-time 300 --retry 3 --proxy "http://proxy-enclave.altera.com:912" --verbose
    if not exist "%LOCAL_INSTALLER_PATH%" (
        echo [INFO] Curl with proxy failed, trying without proxy...
        curl -L -o "%LOCAL_INSTALLER_PATH%" "%NODEJS_URL%" --connect-timeout 30 --max-time 300 --retry 3 --verbose
    )
)

if not exist "%LOCAL_INSTALLER_PATH%" (
    echo [ERROR] All download methods failed!
    echo [INFO] Please check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Download completed successfully!
echo [INFO] File size: 
for %%A in ("%LOCAL_INSTALLER_PATH%") do echo %%~zA bytes
echo.

REM Check if this script was called from START_APP.bat
if "%1"=="--from-start-app" (
    echo [SUCCESS] Download completed successfully for automatic installation.
    exit /b 0
)

echo ========================================
echo [SUCCESS] Node.js installer ready for offline installation!
echo ========================================
echo.
echo [INFO] File created: %LOCAL_INSTALLER_PATH%
echo [INFO] File size: 
for %%A in ("%LOCAL_INSTALLER_PATH%") do echo %%~zA bytes
echo.
echo [INFO] Next steps:
echo [INFO] 1. Copy this file to your target computer
echo [INFO] 2. Place it in the same folder as START_APP.bat
echo [INFO] 3. Run START_APP.bat on the target computer
echo [INFO] 4. The script will automatically detect and use the local installer
echo.
echo [INFO] The installer will install Node.js LTS %NODEJS_VERSION% with:
echo [INFO] - npm package manager
echo [INFO] - Node.js runtime
echo [INFO] - Added to system PATH
echo [INFO] - Installation for all users
echo.

pause
