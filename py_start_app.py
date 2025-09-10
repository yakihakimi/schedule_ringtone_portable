#!/usr/bin/env python3
# Rules applied
"""
Portable Ringtone Creator - Universal Launcher (Python Version)
This script replicates the functionality of START_APP.bat in Python
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
        self.app_dir = Path(__file__).parent
        self.python_path = r"C:\Program Files\Python313\python.exe"
        self.proxy_config = "http://proxy-enclave.altera.com:912"
        
    def print_header(self):
        """Print application header"""
        print("=" * 40)
        print("   Portable Ringtone Creator App")
        print("=" * 40)
        print("Universal Launcher - One-Click Start")
        print()
        
    def check_directory(self):
        """Check if we're in the correct directory"""
        backend_server = self.app_dir / "backend" / "server.py"
        if not backend_server.exists():
            print("[ERROR] This script must be run from the portable_app directory")
            print("[INFO] Please navigate to the portable_app folder and run py_start_app.py")
            print()
            input("Press Enter to exit...")
            sys.exit(1)
            
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
        print()
        print("[INFO] Attempting automatic Python installation...")
        
        # Try local installer first
        local_installer = self.app_dir / "python-installer-local.exe"
        if local_installer.exists():
            print("[INFO] Found local Python installer: python-installer-local.exe")
            print("[INFO] Running local Python installer...")
            
            cmd = f'"{local_installer}" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_tkinter=1 Include_launcher=1'
            returncode, _, _ = self.run_command(cmd, timeout=600)
            
            if returncode == 0:
                print("[INFO] Waiting for installation to complete...")
                time.sleep(10)
                
                # Verify installation
                for cmd in python_commands:
                    returncode, stdout, stderr = self.run_command(f"{cmd} --version", capture_output=True)
                    if returncode == 0:
                        version = stdout.strip()
                        print(f"[SUCCESS] Python {version} is now available")
                        return cmd
                        
        # Try download script
        download_script = self.app_dir / "download_python_offline.bat"
        if download_script.exists():
            print("[INFO] Running Python offline installer downloader...")
            returncode, _, _ = self.run_command(f'"{download_script}"')
            
            if returncode == 0 and local_installer.exists():
                print("[INFO] Download successful! Installing Python...")
                cmd = f'"{local_installer}" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1 Include_tkinter=1 Include_launcher=1'
                returncode, _, _ = self.run_command(cmd, timeout=600)
                
                if returncode == 0:
                    time.sleep(10)
                    for cmd in python_commands:
                        returncode, stdout, stderr = self.run_command(f"{cmd} --version", capture_output=True)
                        if returncode == 0:
                            version = stdout.strip()
                            print(f"[SUCCESS] Python {version} is now available")
                            return cmd
                            
        # Try enhanced installer
        enhanced_installer = self.app_dir / "install_python_enhanced.bat"
        if enhanced_installer.exists():
            print("[INFO] Running enhanced Python installer...")
            returncode, _, _ = self.run_command(f'"{enhanced_installer}"')
            
            if returncode == 0:
                for cmd in python_commands:
                    returncode, stdout, stderr = self.run_command(f"{cmd} --version", capture_output=True)
                    if returncode == 0:
                        version = stdout.strip()
                        print(f"[SUCCESS] Python {version} is now available")
                        return cmd
                        
        print("[ERROR] All automatic Python installation methods failed!")
        print("[INFO] Please install Python 3.13+ manually from: https://www.python.org/downloads/")
        print("[INFO] Make sure to check 'Add Python to PATH' during installation")
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
        print()
        print("[INFO] Attempting automatic Node.js installation...")
        
        # Try local installer first
        local_installer = self.app_dir / "nodejs-installer-local.msi"
        if local_installer.exists():
            print("[INFO] Found local Node.js installer: nodejs-installer-local.msi")
            print("[INFO] Running local Node.js installer...")
            
            cmd = f'start /wait "Node.js Installer" "{local_installer}"'
            returncode, _, _ = self.run_command(cmd, timeout=600)
            
            if returncode == 0:
                print("[INFO] Installation completed, refreshing PATH...")
                time.sleep(3)
                
                # Verify installation
                returncode, stdout, stderr = self.run_command("node --version", capture_output=True)
                if returncode == 0:
                    version = stdout.strip()
                    print(f"[SUCCESS] Node.js {version} is now available")
                    return True
                    
                # Try checking common installation paths
                nodejs_path = r"C:\Program Files\nodejs\node.exe"
                if os.path.exists(nodejs_path):
                    print("[SUCCESS] Node.js found in Program Files, updating PATH...")
                    os.environ["PATH"] += f";{os.path.dirname(nodejs_path)}"
                    returncode, stdout, stderr = self.run_command("node --version", capture_output=True)
                    if returncode == 0:
                        version = stdout.strip()
                        print(f"[SUCCESS] Node.js {version} is now available")
                        return True
                        
        # Try download script
        download_script = self.app_dir / "download_nodejs_offline.bat"
        if download_script.exists():
            print("[INFO] Running Node.js offline installer downloader...")
            returncode, _, _ = self.run_command(f'"{download_script}" --from-start-app')
            
            if returncode == 0 and local_installer.exists():
                print("[INFO] Download successful! Installing Node.js...")
                cmd = f'start /wait "Node.js Installer" "{local_installer}"'
                returncode, _, _ = self.run_command(cmd, timeout=600)
                
                if returncode == 0:
                    time.sleep(3)
                    returncode, stdout, stderr = self.run_command("node --version", capture_output=True)
                    if returncode == 0:
                        version = stdout.strip()
                        print(f"[SUCCESS] Node.js {version} is now available")
                        return True
                        
        print("[ERROR] All automatic Node.js installation methods failed!")
        print("[INFO] Please install Node.js LTS manually from: https://nodejs.org/")
        print("[INFO] Make sure to check 'Add to PATH' during installation")
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
                os.chdir(backend_dir)
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
                        os.chdir(self.app_dir)
                        input("Press Enter to exit...")
                        sys.exit(1)
                        
                os.chdir(self.app_dir)
                print("[SUCCESS] Python dependencies installed successfully")
            else:
                print("[WARNING] requirements.txt not found")
        else:
            print("[SUCCESS] Python dependencies found")
            
    def check_nodejs_dependencies(self):
        """Check and install Node.js dependencies"""
        print("[4/4] Checking Node.js dependencies...")
        
        node_modules = self.app_dir / "node_modules"
        react_scripts_path = node_modules / ".bin" / "react-scripts.cmd"
        
        if not node_modules.exists() or not react_scripts_path.exists():
            print("[WARNING] Node.js dependencies not found or incomplete, installing...")
            
            # Ensure we're in the correct directory
            original_dir = os.getcwd()
            os.chdir(self.app_dir)
            
            try:
                # Clear npm cache first
                print("[INFO] Clearing npm cache...")
                self.run_command("npm cache clean --force", timeout=60)
                
                # Install dependencies
                print("[INFO] Installing Node.js dependencies...")
                returncode, stdout, stderr = self.run_command("npm install", timeout=600, capture_output=True)
                
                if returncode != 0:
                    print(f"[ERROR] Failed to install Node.js dependencies: {stderr}")
                    print("[INFO] Trying with verbose output...")
                    
                    # Try with verbose output for debugging
                    returncode, stdout, stderr = self.run_command("npm install --verbose", timeout=600, capture_output=True)
                    if returncode != 0:
                        print(f"[ERROR] npm install failed: {stderr}")
                        print("[INFO] Please check your internet connection and try again")
                        os.chdir(original_dir)
                        input("Press Enter to exit...")
                        sys.exit(1)
                
                # Verify react-scripts is installed
                if not react_scripts_path.exists():
                    print("[WARNING] react-scripts not found after installation, trying to install it specifically...")
                    returncode, _, _ = self.run_command("npm install react-scripts", timeout=300, capture_output=True)
                    if returncode != 0:
                        print("[ERROR] Failed to install react-scripts specifically")
                        os.chdir(original_dir)
                        input("Press Enter to exit...")
                        sys.exit(1)
                
                print("[SUCCESS] Node.js dependencies installed successfully")
                
            finally:
                os.chdir(original_dir)
        else:
            print("[SUCCESS] Node.js dependencies found")
            
        # Additional check for react-scripts
        if not react_scripts_path.exists():
            print("[ERROR] react-scripts is missing from node_modules/.bin/")
            print("[INFO] This is required for the React app to start")
            input("Press Enter to exit...")
            sys.exit(1)
            
    def check_ffmpeg(self):
        """Check FFmpeg installation"""
        print("[5/5] Checking FFmpeg...")
        
        ffmpeg_path = self.app_dir / "ffmpeg" / "bin" / "ffmpeg.exe"
        if not ffmpeg_path.exists():
            print("[WARNING] FFmpeg not found, attempting automatic installation...")
            print("[INFO] This will enable MP3 conversion features.")
            print()
            
            install_script = self.app_dir / "INSTALL_FFMPEG.bat"
            if install_script.exists():
                returncode, _, _ = self.run_command(f'"{install_script}"', timeout=600)
                if returncode != 0:
                    print("[WARNING] FFmpeg installation failed, but the app will work with WAV files")
                    print("[INFO] You can install FFmpeg manually later for MP3 conversion")
                else:
                    print("[SUCCESS] FFmpeg installed successfully")
            else:
                print("[WARNING] FFmpeg installer not found, app will work with WAV files only")
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
        """Start the application"""
        print()
        print("=" * 40)
        print("   Starting Portable Ringtone Creator")
        print("=" * 40)
        print()
        
        print("[INFO] Attempting to start the application...")
        print()
        
        # Start backend
        print("[Method 1] Starting application directly...")
        print("[INFO] Starting backend server...")
        
        backend_dir = self.app_dir / "backend"
        backend_cmd = f'start "Ringtone Backend" cmd /k "cd /d {backend_dir} && {python_cmd} server.py"'
        self.run_command(backend_cmd)
        
        print("[INFO] Waiting for backend to start...")
        time.sleep(5)
        
        # Start frontend with better error handling
        print("[INFO] Starting frontend server...")
        
        # Check if we're running from an executable (PyInstaller)
        if getattr(sys, 'frozen', False):
            # Running from executable
            print("[INFO] Running from executable - using alternative startup method...")
            
            # Try to use npx to run react-scripts
            frontend_cmd = f'start "Ringtone Frontend" cmd /k "cd /d {self.app_dir} && npx react-scripts start"'
            self.run_command(frontend_cmd)
        else:
            # Running from Python script
            frontend_cmd = f'start "Ringtone Frontend" cmd /k "cd /d {self.app_dir} && npm start"'
            self.run_command(frontend_cmd)
        
        print("[INFO] Waiting for frontend to start...")
        time.sleep(8)
        
        # Verify frontend started successfully
        print("[INFO] Verifying frontend startup...")
        returncode, _, _ = self.run_command('netstat -an | findstr ":3000"', capture_output=True)
        if returncode == 0:
            print("[SUCCESS] Frontend appears to be running on port 3000")
        else:
            print("[WARNING] Frontend may not have started properly")
            print("[INFO] Check the frontend window for error messages")
        
        print("[SUCCESS] Application started successfully!")
        print()
        print("[INFO] Access the app at: http://localhost:3000")
        print("[INFO] Backend API at: http://localhost:5000")
        print()
        print("[INFO] Tips:")
        print("- The app works with WAV files even without FFmpeg")
        print("- FFmpeg enables MP3 conversion features")
        print("- Check the README.md for detailed usage instructions")
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
            
            # Check Node.js dependencies
            self.check_nodejs_dependencies()
            
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
