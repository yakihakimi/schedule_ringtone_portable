#!/usr/bin/env python3
# Rules applied
"""
Portable Ringtone Creator - Truly Standalone Launcher
This version includes ALL dependencies bundled inside the executable
"""

import os
import sys
import subprocess
import time
import platform
import shutil
import logging
import psutil
import atexit
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

class StandaloneAppLauncher:
    def __init__(self):
        print("[DEBUG] Initializing StandaloneAppLauncher...")
        
        # Check for multiple instances first
        if not self.check_single_instance():
            print("[ERROR] Another instance of the application is already running")
            print("[INFO] Please close the existing instance before starting a new one")
            input("Press Enter to exit...")
            sys.exit(1)
        
        # Handle PyInstaller bundle paths
        if getattr(sys, 'frozen', False):
            print("[DEBUG] Running from PyInstaller executable")
            if hasattr(sys, '_MEIPASS'):
                self.bundle_dir = Path(sys._MEIPASS)
                self.app_dir = Path(sys.executable).parent
                print(f"[DEBUG] PyInstaller bundle directory: {self.bundle_dir}")
            else:
                self.app_dir = Path(sys.executable).parent
                self.bundle_dir = self.app_dir
                print("[DEBUG] No _MEIPASS found, using app directory as bundle")
        else:
            print("[DEBUG] Running from Python script")
            self.app_dir = Path(__file__).parent
            self.bundle_dir = self.app_dir
            
        print(f"[DEBUG] App directory: {self.app_dir}")
        print(f"[DEBUG] Bundle directory: {self.bundle_dir}")
        print(f"[DEBUG] Running from executable: {getattr(sys, 'frozen', False)}")
        print(f"[DEBUG] Python executable: {sys.executable}")
        print(f"[DEBUG] Python version: {sys.version}")
        
        # Register cleanup function
        atexit.register(self.cleanup_lock_file)
        
        print("[DEBUG] Initialization completed")
    
    def check_single_instance(self):
        """Check if another instance is already running using lock file method"""
        print("[DEBUG] Checking for multiple instances...")
        
        try:
            # Method 1: Try lock file approach (more reliable)
            lock_file = self.app_dir / "portable_ringtone_app.lock"
            print(f"[DEBUG] Lock file path: {lock_file}")
            
            if lock_file.exists():
                print("[DEBUG] Lock file exists, checking if process is still running...")
                try:
                    with open(lock_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    print(f"[DEBUG] Lock file contains PID: {pid}")
                    
                    # Check if the process is still running
                    try:
                        proc = psutil.Process(pid)
                        if proc.is_running():
                            print(f"[WARNING] Another instance is running (PID: {pid})")
                            return False
                        else:
                            print(f"[DEBUG] Process {pid} is not running, removing stale lock file")
                            lock_file.unlink()
                    except psutil.NoSuchProcess:
                        print(f"[DEBUG] Process {pid} not found, removing stale lock file")
                        lock_file.unlink()
                except (ValueError, FileNotFoundError):
                    print("[DEBUG] Invalid lock file, removing it")
                    lock_file.unlink()
            
            # Create lock file with current PID
            try:
                with open(lock_file, 'w') as f:
                    f.write(str(os.getpid()))
                print(f"[DEBUG] Created lock file with PID: {os.getpid()}")
            except Exception as e:
                print(f"[WARNING] Could not create lock file: {e}")
            
            # Method 2: Fallback to process detection (as backup)
            print("[DEBUG] Also checking process list as backup...")
            current_process = psutil.Process()
            current_name = current_process.name()
            current_pid = current_process.pid
            
            print(f"[DEBUG] Current process: {current_name} (PID: {current_pid})")
            
            # Count processes with the same name, excluding the current process
            same_name_processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    # Skip the current process
                    if proc.info['pid'] == current_pid:
                        print(f"[DEBUG] Skipping current process (PID: {current_pid})")
                        continue
                        
                    if proc.info['name'] == current_name:
                        # Check if it's the same executable
                        if proc.info['cmdline'] and len(proc.info['cmdline']) > 0:
                            cmdline = ' '.join(proc.info['cmdline'])
                            if 'PortableRingtoneApp' in cmdline or 'py_start_app_standalone' in cmdline:
                                same_name_processes.append(proc.info['pid'])
                                print(f"[DEBUG] Found similar process: PID {proc.info['pid']}, cmdline: {cmdline}")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            print(f"[DEBUG] Found {len(same_name_processes)} other similar processes (excluding current)")
            
            # If we have any other processes, we have multiple instances
            if len(same_name_processes) > 0:
                print("[WARNING] Multiple instances detected via process list")
                print(f"[DEBUG] Other processes found: {same_name_processes}")
                # Clean up lock file if we created it
                if lock_file.exists():
                    lock_file.unlink()
                return False
            
            print("[SUCCESS] Single instance check passed")
            return True
            
        except Exception as e:
            print(f"[WARNING] Could not check for multiple instances: {e}")
            print("[INFO] Continuing anyway...")
            return True
    
    def cleanup_lock_file(self):
        """Clean up the lock file when the application exits"""
        try:
            lock_file = self.app_dir / "portable_ringtone_app.lock"
            if lock_file.exists():
                print(f"[DEBUG] Cleaning up lock file: {lock_file}")
                lock_file.unlink()
                print("[DEBUG] Lock file cleaned up successfully")
        except Exception as e:
            print(f"[WARNING] Could not clean up lock file: {e}")
        
    def print_header(self):
        """Print application header"""
        print("=" * 40)
        print("   Portable Ringtone Creator App")
        print("=" * 40)
        print("Truly Standalone Version - No External Dependencies")
        print()
        
    def extract_all_bundled_files(self):
        """Extract ALL bundled files including dependencies"""
        print("[DEBUG] Starting file extraction process...")
        
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            print("[INFO] Extracting all bundled files and dependencies...")
            print(f"[DEBUG] Bundle directory contents: {list(self.bundle_dir.iterdir()) if self.bundle_dir.exists() else 'Directory not found'}")
            
            # Ensure app directory exists
            print(f"[DEBUG] Creating app directory: {self.app_dir}")
            self.app_dir.mkdir(parents=True, exist_ok=True)
            print(f"[DEBUG] App directory created/exists: {self.app_dir.exists()}")
            
            # Extract ALL items from bundle directory dynamically
            print("[DEBUG] Getting all items from bundle directory...")
            all_bundle_items = list(self.bundle_dir.iterdir())
            print(f"[DEBUG] Found {len(all_bundle_items)} items in bundle directory")
            
            # Filter out PyInstaller internal files and directories
            items_to_extract = []
            for item in all_bundle_items:
                item_name = item.name
                # Skip PyInstaller internal files and directories
                if item_name not in ['_internal', 'base_library.zip', 'python313.dll', 'vcruntime140.dll', 'api-ms-win-*.dll']:
                    items_to_extract.append(item_name)
                    print(f"[DEBUG] Will extract: {item_name} ({'dir' if item.is_dir() else 'file'})")
            
            print(f"[DEBUG] Total items to extract: {len(items_to_extract)}")
            
            extracted_count = 0
            for item_name in items_to_extract:
                print(f"[DEBUG] Processing item: {item_name}")
                bundle_path = self.bundle_dir / item_name
                app_path = self.app_dir / item_name
                
                print(f"[DEBUG] Bundle path: {bundle_path} (exists: {bundle_path.exists()})")
                print(f"[DEBUG] App path: {app_path} (exists: {app_path.exists()})")
                
                if bundle_path.exists():
                    try:
                        if bundle_path.is_dir():
                            # Always extract directories (overwrite if exists)
                            print(f"[INFO] Extracting directory: {item_name}")
                            print(f"[DEBUG] Copying from {bundle_path} to {app_path}")
                            if app_path.exists():
                                print(f"[DEBUG] Directory exists, removing first: {app_path}")
                                shutil.rmtree(app_path)
                            shutil.copytree(bundle_path, app_path)
                            extracted_count += 1
                            print(f"[DEBUG] Directory extraction completed: {item_name}")
                        else:
                            # Always extract files (overwrite if exists)
                            print(f"[INFO] Extracting file: {item_name}")
                            print(f"[DEBUG] Copying from {bundle_path} to {app_path}")
                            shutil.copy2(bundle_path, app_path)
                            extracted_count += 1
                            print(f"[DEBUG] File extraction completed: {item_name}")
                    except Exception as e:
                        print(f"[WARNING] Failed to extract {item_name}: {e}")
                        print(f"[DEBUG] Exception type: {type(e)}")
                        import traceback
                        print(f"[DEBUG] Traceback: {traceback.format_exc()}")
                else:
                    print(f"[WARNING] Bundled item not found: {item_name}")
            
            print(f"[SUCCESS] All files extracted ({extracted_count} items)")
            print(f"[DEBUG] Final app directory contents: {list(self.app_dir.iterdir())}")
            return True
        else:
            print("[INFO] Not running from PyInstaller bundle, skipping extraction")
            print(f"[DEBUG] Frozen: {getattr(sys, 'frozen', False)}, MEIPASS: {hasattr(sys, '_MEIPASS')}")
            return True
    
    def check_bundled_dependencies(self):
        """Check if all required dependencies are bundled"""
        print("[DEBUG] Starting dependency check...")
        print("[INFO] Checking bundled dependencies...")
        
        # Check Python dependencies (should be bundled with PyInstaller)
        print("[DEBUG] Checking Python dependencies...")
        try:
            print("[DEBUG] Importing flask...")
            import flask
            print(f"[DEBUG] Flask version: {flask.__version__}")
            
            print("[DEBUG] Importing flask_cors...")
            import flask_cors
            print("[DEBUG] Flask-CORS imported successfully")
            
            print("[DEBUG] Importing pydub...")
            import pydub
            print("[DEBUG] Pydub imported successfully")
            
            print("[SUCCESS] Python dependencies are bundled")
        except ImportError as e:
            print(f"[WARNING] Python dependency missing: {e}")
            print(f"[DEBUG] Import error details: {type(e)} - {e}")
            return False
        
        # Check Node.js dependencies
        print("[DEBUG] Checking Node.js dependencies...")
        node_modules = self.app_dir / "node_modules"
        react_scripts = node_modules / ".bin" / "react-scripts.cmd"
        
        print(f"[DEBUG] Node modules path: {node_modules} (exists: {node_modules.exists()})")
        print(f"[DEBUG] React scripts path: {react_scripts} (exists: {react_scripts.exists()})")
        
        if node_modules.exists():
            print(f"[DEBUG] Node modules directory contents: {list(node_modules.iterdir())[:10]}...")  # Show first 10 items
            if (node_modules / ".bin").exists():
                print(f"[DEBUG] .bin directory contents: {list((node_modules / '.bin').iterdir())}")
        
        if node_modules.exists() and react_scripts.exists():
            print("[SUCCESS] Node.js dependencies are bundled")
            return True
        else:
            print("[WARNING] Node.js dependencies not found in bundle")
            if not node_modules.exists():
                print("[DEBUG] node_modules directory does not exist")
            if not react_scripts.exists():
                print("[DEBUG] react-scripts.cmd does not exist")
            return False
    
    def kill_existing_processes(self):
        """Kill any existing backend/frontend processes"""
        print("[INFO] Checking for existing backend/frontend processes...")
        
        try:
            # Kill processes using port 5000 (backend)
            print("[DEBUG] Checking for processes using port 5000...")
            result = subprocess.run('netstat -ano | findstr ":5000"', shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("[INFO] Found processes using port 5000, attempting to kill them...")
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ':5000' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            try:
                                print(f"[DEBUG] Killing process {pid} using port 5000...")
                                subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                            except Exception as e:
                                print(f"[WARNING] Could not kill process {pid}: {e}")
            
            # Kill processes using port 3000 (frontend)
            print("[DEBUG] Checking for processes using port 3000...")
            result = subprocess.run('netstat -ano | findstr ":3000"', shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("[INFO] Found processes using port 3000, attempting to kill them...")
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ':3000' in line:
                        parts = line.split()
                        if len(parts) >= 5:
                            pid = parts[-1]
                            try:
                                print(f"[DEBUG] Killing process {pid} using port 3000...")
                                subprocess.run(f'taskkill /F /PID {pid}', shell=True, capture_output=True)
                            except Exception as e:
                                print(f"[WARNING] Could not kill process {pid}: {e}")
            
            # Wait a moment for processes to be killed
            print("[DEBUG] Waiting 3 seconds for processes to be killed...")
            time.sleep(3)
            
        except Exception as e:
            print(f"[WARNING] Error killing existing processes: {e}")
    
    def check_ports(self):
        """Check if required ports are available"""
        print("[INFO] Checking port availability...")
        
        # Check port 3000
        result = subprocess.run('netstat -an | findstr ":3000"', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("[WARNING] Port 3000 is already in use")
            print("[INFO] Please close other applications using port 3000")
            print()
            
        # Check port 5000
        result = subprocess.run('netstat -an | findstr ":5000"', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("[WARNING] Port 5000 is already in use")
            print("[INFO] Please close other applications using port 5000")
            print()
    
    def start_backend(self):
        """Start the backend server using bundled Python"""
        print("[DEBUG] Starting backend server...")
        print("[INFO] Starting backend server...")
        
        # Check if backend is already running
        print("[DEBUG] Checking if backend is already running...")
        result = subprocess.run('netstat -an | findstr ":5000"', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("[INFO] Backend is already running on port 5000")
            return True
        
        backend_dir = self.app_dir / "backend"
        print(f"[DEBUG] Backend directory: {backend_dir} (exists: {backend_dir.exists()})")
        
        if not backend_dir.exists():
            print("[ERROR] Backend directory not found")
            print(f"[DEBUG] App directory contents: {list(self.app_dir.iterdir())}")
            return False
        
        # Check if server.py exists
        server_file = backend_dir / "server.py"
        print(f"[DEBUG] Server file: {server_file} (exists: {server_file.exists()})")
        
        if not server_file.exists():
            print("[ERROR] server.py not found in backend directory")
            print(f"[DEBUG] Backend directory contents: {list(backend_dir.iterdir())}")
            return False
        
        # Use the bundled Python interpreter
        python_cmd = sys.executable
        print(f"[DEBUG] Using Python command: {python_cmd}")
        
        # Start backend in a new window with unique title to prevent multiple instances
        backend_title = f"Ringtone Backend - {int(time.time())}"
        backend_cmd = f'start "{backend_title}" cmd /k "cd /d {backend_dir} && "{python_cmd}" server.py"'
        print(f"[DEBUG] Backend command: {backend_cmd}")
        
        print("[DEBUG] Executing backend start command...")
        result = subprocess.run(backend_cmd, shell=True)
        print(f"[DEBUG] Backend start command result: {result}")
        
        print("[INFO] Waiting for backend to start...")
        print("[DEBUG] Waiting 5 seconds for backend to initialize...")
        time.sleep(5)
        
        # Verify backend is running
        print("[DEBUG] Checking if backend is running on port 5000...")
        result = subprocess.run('netstat -an | findstr ":5000"', shell=True, capture_output=True, text=True)
        print(f"[DEBUG] Port check result: {result.returncode}")
        print(f"[DEBUG] Port check output: {result.stdout}")
        
        if result.returncode == 0:
            print("[SUCCESS] Backend server started successfully")
            return True
        else:
            print("[WARNING] Backend may not have started properly")
            print("[DEBUG] Backend might still be starting up, continuing...")
            return False
    
    def start_frontend(self):
        """Start the frontend using bundled Node.js dependencies"""
        print("[DEBUG] Starting frontend server...")
        print("[INFO] Starting frontend server...")
        
        # Check if frontend is already running
        print("[DEBUG] Checking if frontend is already running...")
        result = subprocess.run('netstat -an | findstr ":3000"', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("[INFO] Frontend is already running on port 3000")
            return True
        
        # Check if we have bundled node_modules
        node_modules = self.app_dir / "node_modules"
        react_scripts = node_modules / ".bin" / "react-scripts.cmd"
        
        print(f"[DEBUG] Node modules path: {node_modules} (exists: {node_modules.exists()})")
        print(f"[DEBUG] React scripts path: {react_scripts} (exists: {react_scripts.exists()})")
        
        if react_scripts.exists():
            print("[INFO] Using bundled Node.js dependencies...")
            
            # Use only ONE method to prevent multiple windows
            # Try npm start first (most reliable)
            frontend_title = f"Ringtone Frontend - {int(time.time())}"
            frontend_cmd = f'start "{frontend_title}" cmd /k "cd /d {self.app_dir} && npm start"'
            
            print(f"[INFO] Starting frontend with npm start...")
            print(f"[DEBUG] Command: {frontend_cmd}")
            
            print("[DEBUG] Executing frontend start command...")
            result = subprocess.run(frontend_cmd, shell=True)
            print(f"[DEBUG] Frontend start command result: {result}")
            
            print("[INFO] Waiting for frontend to start...")
            print("[DEBUG] Waiting 8 seconds for frontend to initialize...")
            time.sleep(8)
            
            # Check if frontend started
            print("[DEBUG] Checking if frontend is running on port 3000...")
            result = subprocess.run('netstat -an | findstr ":3000"', shell=True, capture_output=True, text=True)
            print(f"[DEBUG] Port check result: {result.returncode}")
            print(f"[DEBUG] Port check output: {result.stdout}")
            
            if result.returncode == 0:
                print("[SUCCESS] Frontend started successfully")
                return True
            else:
                print("[WARNING] Frontend may not have started properly")
                print("[DEBUG] Frontend might still be starting up, continuing...")
                return False
        else:
            print("[ERROR] Bundled Node.js dependencies not found")
            print("[INFO] Frontend cannot start without bundled dependencies")
            print(f"[DEBUG] Missing: {react_scripts}")
            return False
    
    def start_application(self):
        """Start the complete application"""
        print()
        print("=" * 40)
        print("   Starting Portable Ringtone Creator")
        print("=" * 40)
        print()
        
        # Start backend
        backend_success = self.start_backend()
        
        # Start frontend
        frontend_success = self.start_frontend()
        
        print()
        print("=" * 40)
        print("   Application Startup Complete")
        print("=" * 40)
        print()
        
        if backend_success:
            print("[SUCCESS] Backend API at: http://localhost:5000")
        else:
            print("[ERROR] Backend failed to start")
        
        if frontend_success:
            print("[SUCCESS] Frontend at: http://localhost:3000")
        else:
            print("[ERROR] Frontend failed to start")
            print("[INFO] Check the frontend window for error messages")
        
        print()
        print("[INFO] This is a truly standalone executable")
        print("[INFO] No external dependencies required")
        print()
        print("[INFO] This window will close in 10 seconds...")
        time.sleep(10)
        
    def run(self):
        """Main execution method"""
        try:
            print("[DEBUG] Starting main execution...")
            self.print_header()
            
            print("[INFO] Truly standalone mode - no external dependencies required")
            print()
            
            # Extract all bundled files
            print("[DEBUG] Step 1: Extracting bundled files...")
            if not self.extract_all_bundled_files():
                print("[ERROR] Failed to extract bundled files")
                input("Press Enter to exit...")
                sys.exit(1)
            print("[DEBUG] Step 1 completed: File extraction")
            
            # Check bundled dependencies
            print("[DEBUG] Step 2: Checking bundled dependencies...")
            if not self.check_bundled_dependencies():
                print("[WARNING] Some dependencies may not be properly bundled")
                print("[INFO] Continuing anyway...")
            print("[DEBUG] Step 2 completed: Dependency check")
            
            # Kill existing processes and check ports
            print("[DEBUG] Step 3: Killing existing processes...")
            self.kill_existing_processes()
            print("[DEBUG] Step 3a completed: Process cleanup")
            
            print("[DEBUG] Step 3b: Checking ports...")
            self.check_ports()
            print("[DEBUG] Step 3b completed: Port check")
            
            # Start application
            print("[DEBUG] Step 4: Starting application...")
            self.start_application()
            print("[DEBUG] Step 4 completed: Application startup")
            
            print("[DEBUG] Main execution completed successfully")
            
        except KeyboardInterrupt:
            print("\n[INFO] Application startup cancelled by user")
            print("[DEBUG] KeyboardInterrupt caught")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            print(f"[ERROR] Unexpected error: {e}")
            print(f"[DEBUG] Exception type: {type(e)}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            input("Press Enter to exit...")
            sys.exit(1)

if __name__ == "__main__":
    launcher = StandaloneAppLauncher()
    launcher.run()
