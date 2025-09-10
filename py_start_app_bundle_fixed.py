#!/usr/bin/env python3
# Rules applied
"""
Portable Ringtone Creator - Universal Launcher (Bundle Fixed Version)
This script handles PyInstaller bundle issues and network timeouts properly
"""

import os
import sys
import subprocess
import time
import platform
import shutil
import urllib.request
import zipfile
import tempfile
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai-actions.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PortableAppLauncher:
    def __init__(self):
        # Handle PyInstaller bundle paths properly
        if getattr(sys, 'frozen', False):
            # Running from PyInstaller executable
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller bundle directory (temporary extraction)
                self.bundle_dir = Path(sys._MEIPASS)
                # App directory is where the executable is located
                self.app_dir = Path(sys.executable).parent
            else:
                self.app_dir = Path(sys.executable).parent
                self.bundle_dir = self.app_dir
        else:
            # Running from Python script
            self.app_dir = Path(__file__).parent
            self.bundle_dir = self.app_dir
            
        self.python_path = r"C:\Program Files\Python313\python.exe"
        self.proxy_config = "http://proxy-enclave.altera.com:912"
        
        print(f"[DEBUG] App directory: {self.app_dir}")
        print(f"[DEBUG] Bundle directory: {self.bundle_dir}")
        print(f"[DEBUG] Running from executable: {getattr(sys, 'frozen', False)}")
        
    def print_header(self):
        """Print application header"""
        print("=" * 40)
        print("   Portable Ringtone Creator App")
        print("=" * 40)
        print("Universal Launcher - Bundle Fixed Version")
        print()
        
    def extract_bundled_files(self):
        """Extract bundled files from PyInstaller bundle to app directory"""
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            print("[INFO] Extracting bundled files from PyInstaller bundle...")
            
            # Ensure app directory exists
            self.app_dir.mkdir(parents=True, exist_ok=True)
            
            # List of items to extract
            items_to_extract = [
                "backend",
                "public", 
                "src",
                "package.json",
                "package-lock.json",
                "tsconfig.json"
            ]
            
            extracted_count = 0
            for item in items_to_extract:
                bundle_path = self.bundle_dir / item
                app_path = self.app_dir / item
                
                if bundle_path.exists():
                    try:
                        if bundle_path.is_dir():
                            if not app_path.exists():
                                print(f"[INFO] Extracting directory: {item}")
                                shutil.copytree(bundle_path, app_path)
                                extracted_count += 1
                            else:
                                print(f"[INFO] Directory already exists: {item}")
                        else:
                            if not app_path.exists():
                                print(f"[INFO] Extracting file: {item}")
                                shutil.copy2(bundle_path, app_path)
                                extracted_count += 1
                            else:
                                print(f"[INFO] File already exists: {item}")
                    except Exception as e:
                        print(f"[WARNING] Failed to extract {item}: {e}")
                else:
                    print(f"[WARNING] Bundled item not found: {item}")
            
            print(f"[SUCCESS] File extraction completed ({extracted_count} items extracted)")
            return True
        else:
            print("[INFO] Not running from PyInstaller bundle, skipping extraction")
            return True
    
    def check_directory(self):
        """Check if we're in the correct directory and files are available"""
        # First extract bundled files if needed
        if not self.extract_bundled_files():
            print("[ERROR] Failed to extract bundled files")
            input("Press Enter to exit...")
            sys.exit(1)
        
        # Check for backend server
        backend_server = self.app_dir / "backend" / "server.py"
        if not backend_server.exists():
            print("[ERROR] Backend server not found")
            print(f"[DEBUG] Looking for: {backend_server}")
            print(f"[DEBUG] App directory contents: {list(self.app_dir.iterdir())}")
            print()
            input("Press Enter to exit...")
            sys.exit(1)
            
        # Check for package.json
        package_json = self.app_dir / "package.json"
        if not package_json.exists():
            print("[WARNING] package.json not found - Node.js dependencies may not install properly")
            
    def run_command(self, command, shell=True, capture_output=False, timeout=300):
        """Run a command and return the result"""
        try:
            if capture_output:
                result = subprocess.run(
                    command, 
                    shell=shell, 
                    capture_output=True, 
                    text=True, 
                    timeout=timeout
                )
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(command, shell=shell, timeout=timeout)
                return result.returncode, "", ""
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {command}")
            return -1, "", "Command timed out"
        except Exception as e:
            logger.error(f"Error running command {command}: {e}")
            return -1, "", str(e)
            
    def check_python_installation(self):
        """Check and install Python if needed"""
        print("[1/4] Checking Python installation...")
        
        # Try different Python commands
        python_commands = ["python", "python3", self.python_path]
        
        for cmd in python_commands:
            if cmd == self.python_path and not os.path.exists(cmd):
                continue
                
            returncode, stdout, stderr = self.run_command(f"{cmd} --version", capture_output=True)
            if returncode == 0:
                version = stdout.strip()
                print(f"[SUCCESS] Python {version} found")
                return cmd
                
        print("[ERROR] Python is not installed or not in PATH")
        print("[INFO] Please install Python 3.13+ manually from: https://www.python.org/downloads/")
        print()
        input("Press Enter to exit...")
        sys.exit(1)
        
    def check_nodejs_installation(self):
        """Check and install Node.js if needed"""
        print("[2/4] Checking Node.js installation...")
        
        returncode, stdout, stderr = self.run_command("node --version", capture_output=True)
        if returncode == 0:
            version = stdout.strip()
            print(f"[SUCCESS] Node.js {version} found")
            return True
            
        print("[ERROR] Node.js is not installed or not in PATH")
        print("[INFO] Please install Node.js LTS manually from: https://nodejs.org/")
        print()
        input("Press Enter to exit...")
        sys.exit(1)
        
    def check_python_dependencies(self, python_cmd):
        """Check and install Python dependencies"""
        print("[3/4] Checking Python dependencies...")
        
        # Check if flask_cors is installed
        returncode, _, _ = self.run_command(f"{python_cmd} -c \"import flask_cors\"", capture_output=True)
        if returncode != 0:
            print("[WARNING] Python dependencies not found, installing...")
            
            backend_dir = self.app_dir / "backend"
            requirements_file = backend_dir / "requirements.txt"
            
            if requirements_file.exists():
                original_dir = os.getcwd()
                os.chdir(backend_dir)
                
                try:
                    print("[INFO] Installing with proxy configuration...")
                    cmd = f"{python_cmd} -m pip install --proxy {self.proxy_config} -r requirements.txt"
                    returncode, _, _ = self.run_command(cmd, timeout=300)
                    
                    if returncode != 0:
                        print("[ERROR] Failed to install Python dependencies with proxy")
                        print("[INFO] Trying without proxy...")
                        cmd = f"{python_cmd} -m pip install -r requirements.txt"
                        returncode, _, _ = self.run_command(cmd, timeout=300)
                        
                        if returncode != 0:
                            print("[ERROR] Failed to install Python dependencies")
                            print("[INFO] Please check your internet connection and try again")
                            os.chdir(original_dir)
                            input("Press Enter to exit...")
                            sys.exit(1)
                    
                    print("[SUCCESS] Python dependencies installed successfully")
                    
                finally:
                    os.chdir(original_dir)
            else:
                print("[WARNING] requirements.txt not found")
        else:
            print("[SUCCESS] Python dependencies found")
            
    def check_nodejs_dependencies(self):
        """Check and install Node.js dependencies with network timeout handling"""
        print("[4/4] Checking Node.js dependencies...")
        
        node_modules = self.app_dir / "node_modules"
        react_scripts_path = node_modules / ".bin" / "react-scripts.cmd"
        
        if not node_modules.exists() or not react_scripts_path.exists():
            print("[WARNING] Node.js dependencies not found or incomplete, installing...")
            
            original_dir = os.getcwd()
            os.chdir(self.app_dir)
            
            try:
                # Clear npm cache first
                print("[INFO] Clearing npm cache...")
                self.run_command("npm cache clean --force", timeout=60)
                
                # Try multiple installation methods
                install_methods = [
                    f"npm install --proxy {self.proxy_config}",
                    "npm install --no-audit",
                    "npm install --offline",
                    "npm install"
                ]
                
                success = False
                for method in install_methods:
                    print(f"[INFO] Trying: {method}")
                    returncode, stdout, stderr = self.run_command(method, timeout=600, capture_output=True)
                    
                    if returncode == 0:
                        print(f"[SUCCESS] Installation successful with: {method}")
                        success = True
                        break
                    else:
                        print(f"[WARNING] Failed with {method}: {stderr[:200]}...")
                
                if not success:
                    print("[ERROR] All npm install methods failed")
                    print("[INFO] This might be due to network issues")
                    print("[INFO] You can try running 'npm install' manually later")
                    print("[INFO] Continuing without Node.js dependencies...")
                    return False
                
                # Verify react-scripts is installed
                if not react_scripts_path.exists():
                    print("[WARNING] react-scripts not found after installation")
                    print("[INFO] Trying to install react-scripts specifically...")
                    returncode, _, _ = self.run_command("npm install react-scripts --no-audit", timeout=300, capture_output=True)
                    if returncode != 0:
                        print("[WARNING] Failed to install react-scripts specifically")
                        return False
                
                print("[SUCCESS] Node.js dependencies installed successfully")
                return True
                
            finally:
                os.chdir(original_dir)
        else:
            print("[SUCCESS] Node.js dependencies found")
            return True
            
    def check_ffmpeg(self):
        """Check FFmpeg installation"""
        print("[5/5] Checking FFmpeg...")
        
        ffmpeg_path = self.app_dir / "ffmpeg" / "bin" / "ffmpeg.exe"
        if not ffmpeg_path.exists():
            print("[WARNING] FFmpeg not found")
            print("[INFO] App will work with WAV files only")
            print("[INFO] Install FFmpeg manually for MP3 conversion")
        else:
            print("[SUCCESS] FFmpeg found")
            
    def check_ports(self):
        """Check if required ports are available"""
        print()
        print("[INFO] Checking port availability...")
        
        # Check port 3000
        returncode, _, _ = self.run_command('netstat -an | findstr ":3000"', capture_output=True)
        if returncode == 0:
            print("[WARNING] Port 3000 is already in use")
            print("[INFO] Please close other applications using port 3000")
            print()
            
        # Check port 5000
        returncode, _, _ = self.run_command('netstat -an | findstr ":5000"', capture_output=True)
        if returncode == 0:
            print("[WARNING] Port 5000 is already in use")
            print("[INFO] Please close other applications using port 5000")
            print()
            
    def start_application(self, python_cmd):
        """Start the application with improved error handling"""
        print()
        print("=" * 40)
        print("   Starting Portable Ringtone Creator")
        print("=" * 40)
        print()
        
        print("[INFO] Attempting to start the application...")
        print()
        
        # Start backend
        print("[INFO] Starting backend server...")
        backend_dir = self.app_dir / "backend"
        backend_cmd = f'start "Ringtone Backend" cmd /k "cd /d {backend_dir} && {python_cmd} server.py"'
        self.run_command(backend_cmd)
        
        print("[INFO] Waiting for backend to start...")
        time.sleep(5)
        
        # Start frontend with multiple fallback methods
        print("[INFO] Starting frontend server...")
        
        # Check if we have Node.js dependencies
        node_modules = self.app_dir / "node_modules"
        react_scripts_path = node_modules / ".bin" / "react-scripts.cmd"
        
        if node_modules.exists() and react_scripts_path.exists():
            print("[INFO] Node.js dependencies found, starting frontend...")
            
            # Try different startup methods
            frontend_methods = [
                f'start "Ringtone Frontend" cmd /k "cd /d {self.app_dir} && npm start"',
                f'start "Ringtone Frontend (npx)" cmd /k "cd /d {self.app_dir} && npx react-scripts start"',
                f'start "Ringtone Frontend (direct)" cmd /k "cd /d {self.app_dir} && "{react_scripts_path}" start"'
            ]
            
            for i, method in enumerate(frontend_methods, 1):
                print(f"[INFO] Trying frontend method {i}...")
                self.run_command(method)
                time.sleep(3)
                
                # Check if frontend started
                returncode, _, _ = self.run_command('netstat -an | findstr ":3000"', capture_output=True)
                if returncode == 0:
                    print(f"[SUCCESS] Frontend started with method {i}")
                    break
                else:
                    print(f"[WARNING] Method {i} did not start frontend")
        else:
            print("[WARNING] Node.js dependencies not available")
            print("[INFO] Frontend will not start automatically")
            print("[INFO] Please install Node.js dependencies manually and run 'npm start'")
        
        print()
        print("[SUCCESS] Application startup completed!")
        print()
        print("[INFO] Backend API at: http://localhost:5000")
        print("[INFO] Frontend at: http://localhost:3000 (if started)")
        print()
        print("[INFO] Tips:")
        print("- The app works with WAV files even without FFmpeg")
        print("- FFmpeg enables MP3 conversion features")
        print("- If frontend doesn't start, run 'npm start' manually in the app directory")
        print()
        print("[INFO] This window will close in 10 seconds...")
        time.sleep(10)
        
    def run(self):
        """Main execution method"""
        try:
            self.print_header()
            self.check_directory()
            
            print("[INFO] Performing comprehensive system check...")
            print()
            
            # Check and install Python
            python_cmd = self.check_python_installation()
            
            # Check and install Node.js
            self.check_nodejs_installation()
            
            # Check Python dependencies
            self.check_python_dependencies(python_cmd)
            
            # Check Node.js dependencies (may fail due to network issues)
            nodejs_success = self.check_nodejs_dependencies()
            
            # Check FFmpeg
            self.check_ffmpeg()
            
            # Check ports
            self.check_ports()
            
            # Start application
            self.start_application(python_cmd)
            
        except KeyboardInterrupt:
            print("\n[INFO] Application startup cancelled by user")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"[ERROR] Unexpected error: {e}")
            input("Press Enter to exit...")
            sys.exit(1)

if __name__ == "__main__":
    launcher = PortableAppLauncher()
    launcher.run()
