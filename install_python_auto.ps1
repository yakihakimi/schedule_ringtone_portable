# Rules applied
# Enhanced Python installation script with automatic download and installation
# This script downloads and installs Python 3.12.4 if it's not already installed

Write-Host "========================================" -ForegroundColor Green
Write-Host "Automatic Python Installation" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if Python is already installed
Write-Host "[INFO] Checking for existing Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Python is already installed:" -ForegroundColor Green
        Write-Host $pythonVersion -ForegroundColor Cyan
        Write-Host ""
        Write-Host "[INFO] Checking pip..." -ForegroundColor Yellow
        $pipVersion = pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host $pipVersion -ForegroundColor Cyan
            Write-Host ""
            Write-Host "[SUCCESS] Python installation is complete and ready to use!" -ForegroundColor Green
            Read-Host "Press Enter to exit"
            exit 0
        } else {
            Write-Host "[WARNING] Python found but pip is not available. Reinstalling..." -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "[INFO] Python not found. Proceeding with automatic installation..." -ForegroundColor Yellow
}

Write-Host ""

# Check if we have internet connectivity
Write-Host "[INFO] Checking internet connectivity..." -ForegroundColor Yellow
try {
    $ping = Test-Connection -ComputerName "google.com" -Count 1 -Quiet
    if (-not $ping) {
        throw "No internet connection"
    }
    Write-Host "[SUCCESS] Internet connection verified." -ForegroundColor Green
} catch {
    Write-Host "[ERROR] No internet connection detected!" -ForegroundColor Red
    Write-Host "[INFO] Please check your internet connection and try again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "[INFO] Alternative: Please download Python manually from https://python.org" -ForegroundColor Yellow
    Write-Host "[INFO] Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

# Create temporary directory for download
$tempDir = Join-Path $env:TEMP "python_auto_install"
if (-not (Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
}

Write-Host "[INFO] Downloading Python installer..." -ForegroundColor Yellow
Write-Host ""

# Get Python 3.12.4 version
$pythonVersion = "3.12.4"
$pythonUrl = "https://www.python.org/ftp/python/$pythonVersion/python-$pythonVersion-amd64.exe"
$installerPath = Join-Path $tempDir "python-installer.exe"

Write-Host "[INFO] Downloading Python $pythonVersion from: $pythonUrl" -ForegroundColor Cyan
Write-Host "[INFO] Saving to: $installerPath" -ForegroundColor Cyan
Write-Host ""

try {
    # Set security protocol for HTTPS
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    
    Write-Host "[INFO] Attempting download with PowerShell..." -ForegroundColor Yellow
    
    # Try direct download first
    try {
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing -TimeoutSec 300
    } catch {
        Write-Host "[INFO] Direct download failed, trying with proxy..." -ForegroundColor Yellow
        # Try with proxy support
        [System.Net.WebRequest]::DefaultWebProxy = [System.Net.WebRequest]::GetSystemWebProxy()
        [System.Net.WebRequest]::DefaultWebProxy.Credentials = [System.Net.CredentialCache]::DefaultCredentials
        Invoke-WebRequest -Uri $pythonUrl -OutFile $installerPath -UseBasicParsing -TimeoutSec 300
    }
    
    if (-not (Test-Path $installerPath)) {
        throw "Download failed"
    }
    
    $fileSize = (Get-Item $installerPath).Length
    Write-Host "[SUCCESS] Download completed successfully!" -ForegroundColor Green
    Write-Host "[INFO] File size: $fileSize bytes" -ForegroundColor Cyan
    
} catch {
    Write-Host "[ERROR] Failed to download Python installer!" -ForegroundColor Red
    Write-Host "[INFO] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "[INFO] Please check your internet connection and try again." -ForegroundColor Yellow
    Write-Host "[INFO] Alternative: Please download Python manually from https://python.org" -ForegroundColor Yellow
    Write-Host "[INFO] Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""

Write-Host "[INFO] Installing Python..." -ForegroundColor Yellow
Write-Host "[INFO] This may take a few minutes. Please wait..." -ForegroundColor Yellow
Write-Host "[INFO] Installation will be silent (no user interaction required)" -ForegroundColor Yellow
Write-Host ""

try {
    # Install Python with all necessary options
    $arguments = @(
        "/quiet",
        "InstallAllUsers=1",
        "PrependPath=1", 
        "Include_pip=1",
        "Include_test=0",
        "Include_launcher=1",
        "Include_doc=0",
        "Include_tcltk=1"
    )
    
    $process = Start-Process -FilePath $installerPath -ArgumentList $arguments -Wait -PassThru
    
    if ($process.ExitCode -ne 0) {
        throw "Installation failed with exit code: $($process.ExitCode)"
    }
    
    Write-Host "[SUCCESS] Installation completed!" -ForegroundColor Green
    
} catch {
    Write-Host "[ERROR] Failed to install Python!" -ForegroundColor Red
    Write-Host "[INFO] Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Clean up installer
Write-Host "[INFO] Cleaning up temporary files..." -ForegroundColor Yellow
try {
    Remove-Item $installerPath -Force -ErrorAction SilentlyContinue
    Remove-Item $tempDir -Force -ErrorAction SilentlyContinue
} catch {
    # Ignore cleanup errors
}

# Refresh environment variables
Write-Host "[INFO] Refreshing environment variables..." -ForegroundColor Yellow
try {
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
} catch {
    # Ignore refresh errors
}

# Wait for the installation to be recognized
Start-Sleep -Seconds 15

# Check if installation was successful
Write-Host ""
Write-Host "[INFO] Verifying installation..." -ForegroundColor Yellow

try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "[SUCCESS] Python installation completed!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "[INFO] Python version:" -ForegroundColor Cyan
        Write-Host $pythonVersion -ForegroundColor White
        Write-Host ""
        Write-Host "[INFO] pip version:" -ForegroundColor Cyan
        $pipVersion = pip --version 2>&1
        Write-Host $pipVersion -ForegroundColor White
        Write-Host ""
        Write-Host "[INFO] Python installation path:" -ForegroundColor Cyan
        $pythonPath = where.exe python 2>&1
        Write-Host $pythonPath -ForegroundColor White
        Write-Host ""
        Write-Host "[SUCCESS] Python is now ready to use!" -ForegroundColor Green
        Write-Host "[INFO] You can now run the setup script: SETUP_WITH_FFMPEG.bat" -ForegroundColor Yellow
        Write-Host ""
    } else {
        throw "Python not found after installation"
    }
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "[WARNING] Python installation verification failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "[INFO] This might be due to:" -ForegroundColor Yellow
    Write-Host "[INFO] 1. Installation is still in progress" -ForegroundColor White
    Write-Host "[INFO] 2. PATH environment variable needs to be refreshed" -ForegroundColor White
    Write-Host "[INFO] 3. Terminal needs to be restarted" -ForegroundColor White
    Write-Host ""
    Write-Host "[INFO] Please try the following:" -ForegroundColor Yellow
    Write-Host "[INFO] 1. Restart your command prompt or PowerShell" -ForegroundColor White
    Write-Host "[INFO] 2. Check if Python was installed in: C:\Program Files\Python313" -ForegroundColor White
    Write-Host "[INFO] 3. Manually add Python to PATH if needed" -ForegroundColor White
    Write-Host "[INFO] 4. Run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "[INFO] If problems persist, download Python manually from:" -ForegroundColor Yellow
    Write-Host "[INFO] https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "[INFO] Make sure to check 'Add Python to PATH' during installation" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "[INFO] Installation process completed." -ForegroundColor Yellow
Read-Host "Press Enter to exit"
