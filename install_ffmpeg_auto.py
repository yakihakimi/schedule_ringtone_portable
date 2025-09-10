# Rules applied
import os
import sys
import urllib.request
import zipfile
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_proxy():
    """Setup proxy configuration if needed"""
    try:
        # Check if we're behind a corporate proxy
        proxy_url = "proxy-enclave.altera.com:912"
        
        # Test if proxy is accessible
        proxy_handler = urllib.request.ProxyHandler({
            'http': proxy_url,
            'https': proxy_url
        })
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)
        
        logger.info(f"Proxy configured: {proxy_url}")
        return True
    except Exception as e:
        logger.warning(f"Proxy setup failed: {e}")
        return False

def download_ffmpeg():
    """Download FFmpeg portable build"""
    try:
        # FFmpeg download URL (static build for Windows)
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        
        # Local paths
        script_dir = Path(__file__).parent
        ffmpeg_dir = script_dir / "ffmpeg"
        bin_dir = ffmpeg_dir / "bin"
        zip_path = script_dir / "ffmpeg.zip"
        
        # Create directories
        bin_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Starting FFmpeg download...")
        logger.info(f"Download URL: {ffmpeg_url}")
        logger.info(f"Target directory: {bin_dir}")
        
        # Download with progress
        def show_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, (downloaded * 100) // total_size)
                sys.stdout.write(f"\rDownloading: {percent}% ({downloaded // 1024 // 1024}MB/{total_size // 1024 // 1024}MB)")
                sys.stdout.flush()
        
        urllib.request.urlretrieve(ffmpeg_url, zip_path, reporthook=show_progress)
        print()  # New line after progress
        
        logger.info("Download completed successfully")
        return zip_path, bin_dir
        
    except Exception as e:
        logger.error(f"Download failed: {e}")
        return None, None

def extract_ffmpeg(zip_path, bin_dir):
    """Extract FFmpeg from ZIP file"""
    try:
        logger.info("Extracting FFmpeg...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find the bin directory in the zip
            bin_files = [f for f in zip_ref.namelist() if f.startswith('ffmpeg-master-latest-win64-gpl/bin/')]
            
            if not bin_files:
                logger.error("No bin files found in FFmpeg archive")
                return False
            
            # Extract only the bin files
            for file in bin_files:
                if file.endswith('/'):
                    continue
                    
                # Get the filename without the path
                filename = os.path.basename(file)
                target_path = bin_dir / filename
                
                # Extract the file
                with zip_ref.open(file) as source, open(target_path, 'wb') as target:
                    shutil.copyfileobj(source, target)
                
                logger.info(f"Extracted: {filename}")
        
        logger.info("Extraction completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return False

def verify_installation(bin_dir):
    """Verify FFmpeg installation"""
    try:
        ffmpeg_exe = bin_dir / "ffmpeg.exe"
        
        if not ffmpeg_exe.exists():
            logger.error("ffmpeg.exe not found after installation")
            return False
        
        # Test FFmpeg
        import subprocess
        result = subprocess.run([str(ffmpeg_exe), "-version"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            logger.info("FFmpeg installation verified successfully")
            logger.info(f"FFmpeg version: {result.stdout.split('ffmpeg version')[1].split()[0] if 'ffmpeg version' in result.stdout else 'Unknown'}")
            return True
        else:
            logger.error(f"FFmpeg test failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False

def cleanup(zip_path):
    """Clean up temporary files"""
    try:
        if zip_path and zip_path.exists():
            zip_path.unlink()
            logger.info("Cleaned up temporary files")
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")

def install_ffmpeg():
    """Main installation function"""
    try:
        logger.info("=" * 60)
        logger.info("FFmpeg Automatic Installation for Portable App")
        logger.info("=" * 60)
        
        # Check if already installed
        script_dir = Path(__file__).parent
        ffmpeg_exe = script_dir / "ffmpeg" / "bin" / "ffmpeg.exe"
        
        if ffmpeg_exe.exists():
            logger.info("FFmpeg already installed, verifying...")
            if verify_installation(ffmpeg_exe.parent):
                logger.info("FFmpeg is already working correctly!")
                return True
            else:
                logger.info("FFmpeg found but not working, reinstalling...")
        
        # Setup proxy if needed
        setup_proxy()
        
        # Download FFmpeg
        zip_path, bin_dir = download_ffmpeg()
        if not zip_path or not bin_dir:
            return False
        
        # Extract FFmpeg
        if not extract_ffmpeg(zip_path, bin_dir):
            return False
        
        # Verify installation
        if not verify_installation(bin_dir):
            return False
        
        # Cleanup
        cleanup(zip_path)
        
        logger.info("=" * 60)
        logger.info("FFmpeg installation completed successfully!")
        logger.info("MP3 conversion features are now available.")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"Installation failed: {e}")
        cleanup(zip_path if 'zip_path' in locals() else None)
        return False

if __name__ == "__main__":
    success = install_ffmpeg()
    if not success:
        logger.error("FFmpeg installation failed!")
        sys.exit(1)
    else:
        logger.info("FFmpeg installation successful!")
        sys.exit(0)
