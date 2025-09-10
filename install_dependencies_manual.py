#!/usr/bin/env python3
# Rules applied
"""
Manual dependency installation script with proxy support
Run this script to install dependencies before creating the standalone executable
"""

import os
import sys
import subprocess
from pathlib import Path

def install_python_dependencies_manual():
    """Manually install Python dependencies with proxy support"""
    print("=" * 50)
    print("   Manual Python Dependencies Installation")
    print("=" * 50)
    print()
    
    app_dir = Path(__file__).parent
    backend_dir = app_dir / "backend"
    requirements_file = backend_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print("[ERROR] requirements.txt not found")
        return False
    
    # Create a local packages directory
    packages_dir = app_dir / "python_packages"
    packages_dir.mkdir(exist_ok=True)
    
    proxy_config = "http://proxy-enclave.altera.com:912"
    
    print("[INFO] Installing Python dependencies with proxy support...")
    print(f"[INFO] Proxy: {proxy_config}")
    print(f"[INFO] Target directory: {packages_dir}")
    print()
    
    # Try different installation methods
    methods = [
        {
            "name": "Method 1: Proxy with timeout",
            "cmd": f"pip install --proxy {proxy_config} --target {packages_dir} -r {requirements_file} --timeout 120"
        },
        {
            "name": "Method 2: Proxy with retries",
            "cmd": f"pip install --proxy {proxy_config} --target {packages_dir} -r {requirements_file} --timeout 120 --retries 3"
        },
        {
            "name": "Method 3: Proxy with verbose output",
            "cmd": f"pip install --proxy {proxy_config} --target {packages_dir} -r {requirements_file} --timeout 120 --retries 3 --verbose"
        },
        {
            "name": "Method 4: No proxy with timeout",
            "cmd": f"pip install --target {packages_dir} -r {requirements_file} --timeout 120"
        }
    ]
    
    for method in methods:
        print(f"[INFO] Trying {method['name']}...")
        print(f"[DEBUG] Command: {method['cmd']}")
        print()
        
        result = subprocess.run(method['cmd'], shell=True, capture_output=True, text=True, timeout=600)
        
        if result.returncode == 0:
            print(f"[SUCCESS] {method['name']} succeeded!")
            print("[SUCCESS] Python dependencies installed successfully")
            return True
        else:
            print(f"[WARNING] {method['name']} failed:")
            print(f"[ERROR] {result.stderr}")
            print()
    
    print("[ERROR] All Python dependency installation methods failed")
    print("[INFO] You may need to check your network connection and proxy settings")
    return False

def install_nodejs_dependencies_manual():
    """Manually install Node.js dependencies with proxy support"""
    print("=" * 50)
    print("   Manual Node.js Dependencies Installation")
    print("=" * 50)
    print()
    
    app_dir = Path(__file__).parent
    proxy_config = "http://proxy-enclave.altera.com:912"
    
    # Change to app directory
    original_dir = os.getcwd()
    os.chdir(app_dir)
    
    try:
        print("[INFO] Installing Node.js dependencies with proxy support...")
        print(f"[INFO] Proxy: {proxy_config}")
        print()
        
        # Clear npm cache first
        print("[INFO] Clearing npm cache...")
        subprocess.run("npm cache clean --force", shell=True, timeout=60)
        
        # Try different installation methods
        methods = [
            {
                "name": "Method 1: Proxy with no audit",
                "cmd": f"npm install --proxy {proxy_config} --no-audit"
            },
            {
                "name": "Method 2: Proxy with timeout",
                "cmd": f"npm install --proxy {proxy_config} --no-audit --timeout 120000"
            },
            {
                "name": "Method 3: No proxy with no audit",
                "cmd": "npm install --no-audit"
            },
            {
                "name": "Method 4: Offline mode",
                "cmd": "npm install --offline"
            }
        ]
        
        for method in methods:
            print(f"[INFO] Trying {method['name']}...")
            print(f"[DEBUG] Command: {method['cmd']}")
            print()
            
            result = subprocess.run(method['cmd'], shell=True, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print(f"[SUCCESS] {method['name']} succeeded!")
                print("[SUCCESS] Node.js dependencies installed successfully")
                return True
            else:
                print(f"[WARNING] {method['name']} failed:")
                print(f"[ERROR] {result.stderr[:300]}...")
                print()
        
        print("[ERROR] All Node.js dependency installation methods failed")
        print("[INFO] You may need to check your network connection and proxy settings")
        return False
        
    finally:
        os.chdir(original_dir)

def main():
    """Main execution function"""
    print("=" * 60)
    print("   Manual Dependencies Installation with Proxy Support")
    print("=" * 60)
    print()
    print("This script will install Python and Node.js dependencies")
    print("with proxy support before creating the standalone executable.")
    print()
    
    # Install Python dependencies
    python_success = install_python_dependencies_manual()
    
    print()
    print("=" * 60)
    print()
    
    # Install Node.js dependencies
    nodejs_success = install_nodejs_dependencies_manual()
    
    print()
    print("=" * 60)
    print("   Installation Summary")
    print("=" * 60)
    print()
    
    if python_success:
        print("[SUCCESS] Python dependencies installed")
    else:
        print("[ERROR] Python dependencies installation failed")
    
    if nodejs_success:
        print("[SUCCESS] Node.js dependencies installed")
    else:
        print("[ERROR] Node.js dependencies installation failed")
    
    if python_success and nodejs_success:
        print()
        print("[SUCCESS] All dependencies installed successfully!")
        print("[INFO] You can now run CREATE_STANDALONE_EXECUTABLE.bat")
    else:
        print()
        print("[ERROR] Some dependencies failed to install")
        print("[INFO] Please check the error messages above and try again")
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
