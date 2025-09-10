# Rules applied
param(
    [switch]$UseProxy,
    [string]$ProxyUrl = "proxy-enclave.altera.com:912"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FFmpeg Automatic Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to setup proxy
function Setup-Proxy {
    param([string]$ProxyUrl)
    
    try {
        if ($UseProxy) {
            Write-Host "Setting up proxy: $ProxyUrl" -ForegroundColor Yellow
            $proxy = New-Object System.Net.WebProxy("http://$ProxyUrl")
            $proxy.Credentials = [System.Net.CredentialCache]::DefaultCredentials
            [System.Net.WebRequest]::DefaultWebProxy = $proxy
            Write-Host "Proxy configured successfully" -ForegroundColor Green
            return $true
        }
        return $false
    }
    catch {
        Write-Host "Proxy setup failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to download FFmpeg
function Download-FFmpeg {
    param([string]$DownloadUrl, [string]$OutputPath)
    
    try {
        Write-Host "Starting FFmpeg download..." -ForegroundColor Yellow
        Write-Host "URL: $DownloadUrl" -ForegroundColor Gray
        Write-Host "Output: $OutputPath" -ForegroundColor Gray
        
        # Use Invoke-WebRequest with progress
        $ProgressPreference = 'Continue'
        Invoke-WebRequest -Uri $DownloadUrl -OutFile $OutputPath -UseBasicParsing
        
        if (Test-Path $OutputPath) {
            $fileSize = (Get-Item $OutputPath).Length / 1MB
            Write-Host "Download completed: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Green
            return $true
        } else {
            Write-Host "Download failed - file not found" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Download failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to extract FFmpeg
function Extract-FFmpeg {
    param([string]$ZipPath, [string]$ExtractPath)
    
    try {
        Write-Host "Extracting FFmpeg..." -ForegroundColor Yellow
        
        # Create extraction directory
        if (!(Test-Path $ExtractPath)) {
            New-Item -ItemType Directory -Path $ExtractPath -Force | Out-Null
        }
        
        # Extract using .NET
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        [System.IO.Compression.ZipFile]::ExtractToDirectory($ZipPath, $ExtractPath)
        
        # Find the extracted FFmpeg bin directory
        $extractedDirs = Get-ChildItem -Path $ExtractPath -Directory | Where-Object { $_.Name -like "*ffmpeg*" }
        
        if ($extractedDirs.Count -eq 0) {
            Write-Host "No FFmpeg directory found in archive" -ForegroundColor Red
            return $false
        }
        
        $ffmpegDir = $extractedDirs[0]
        $sourceBinDir = Join-Path $ffmpegDir.FullName "bin"
        $targetBinDir = Join-Path (Split-Path $ExtractPath -Parent) "ffmpeg\bin"
        
        if (!(Test-Path $sourceBinDir)) {
            Write-Host "No bin directory found in FFmpeg archive" -ForegroundColor Red
            return $false
        }
        
        # Create target bin directory
        if (!(Test-Path $targetBinDir)) {
            New-Item -ItemType Directory -Path $targetBinDir -Force | Out-Null
        }
        
        # Copy FFmpeg executables
        $binFiles = Get-ChildItem -Path $sourceBinDir -File
        foreach ($file in $binFiles) {
            $targetPath = Join-Path $targetBinDir $file.Name
            Copy-Item -Path $file.FullName -Destination $targetPath -Force
            Write-Host "Extracted: $($file.Name)" -ForegroundColor Gray
        }
        
        # Clean up extraction directory
        Remove-Item -Path $ExtractPath -Recurse -Force
        
        Write-Host "Extraction completed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "Extraction failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to verify installation
function Test-FFmpegInstallation {
    param([string]$BinDir)
    
    try {
        $ffmpegExe = Join-Path $BinDir "ffmpeg.exe"
        
        if (!(Test-Path $ffmpegExe)) {
            Write-Host "ffmpeg.exe not found after installation" -ForegroundColor Red
            return $false
        }
        
        Write-Host "Testing FFmpeg installation..." -ForegroundColor Yellow
        
        # Test FFmpeg
        $result = & $ffmpegExe -version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $version = ($result | Select-String "ffmpeg version").ToString().Split()[2]
            Write-Host "FFmpeg installation verified successfully" -ForegroundColor Green
            Write-Host "Version: $version" -ForegroundColor Green
            return $true
        } else {
            Write-Host "FFmpeg test failed" -ForegroundColor Red
            return $false
        }
    }
    catch {
        Write-Host "Verification failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main installation function
function Install-FFmpeg {
    try {
        # Check if already installed
        $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
        $ffmpegExe = Join-Path $scriptDir "ffmpeg\bin\ffmpeg.exe"
        
        if (Test-Path $ffmpegExe) {
            Write-Host "FFmpeg already installed, verifying..." -ForegroundColor Yellow
            if (Test-FFmpegInstallation (Split-Path $ffmpegExe)) {
                Write-Host "FFmpeg is already working correctly!" -ForegroundColor Green
                return $true
            } else {
                Write-Host "FFmpeg found but not working, reinstalling..." -ForegroundColor Yellow
            }
        }
        
        # Setup proxy if requested
        if ($UseProxy) {
            Setup-Proxy -ProxyUrl $ProxyUrl
        }
        
        # Download FFmpeg
        $downloadUrl = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        $zipPath = Join-Path $scriptDir "ffmpeg.zip"
        $extractPath = Join-Path $scriptDir "ffmpeg_temp"
        
        if (!(Download-FFmpeg -DownloadUrl $downloadUrl -OutputPath $zipPath)) {
            return $false
        }
        
        # Extract FFmpeg
        if (!(Extract-FFmpeg -ZipPath $zipPath -ExtractPath $extractPath)) {
            return $false
        }
        
        # Verify installation
        $binDir = Join-Path $scriptDir "ffmpeg\bin"
        if (!(Test-FFmpegInstallation -BinDir $binDir)) {
            return $false
        }
        
        # Cleanup
        if (Test-Path $zipPath) {
            Remove-Item -Path $zipPath -Force
            Write-Host "Cleaned up temporary files" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "FFmpeg installation completed successfully!" -ForegroundColor Green
        Write-Host "MP3 conversion features are now available." -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        
        return $true
    }
    catch {
        Write-Host "Installation failed: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Run installation
$success = Install-FFmpeg

if ($success) {
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 0
} else {
    Write-Host ""
    Write-Host "FFmpeg installation failed!" -ForegroundColor Red
    Write-Host "Press any key to continue..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}
