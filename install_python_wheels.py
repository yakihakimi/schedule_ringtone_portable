#!/usr/bin/env python3
# Rules applied
"""
Specialized Python wheel installation script
Handles wheel build errors and uses precompiled wheels when possible
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_python_wheels():
    """Install Python dependencies using precompiled wheels"""
    print("=" * 50)
    print("   Python Wheel Installation (Precompiled Packages)")
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
    
    print("[INFO] Installing Python dependencies using precompiled wheels...")
    print(f"[INFO] Proxy: {proxy_config}")
    print(f"[INFO] Target directory: {packages_dir}")
    print()
    
    # Try different wheel installation methods
    methods = [
        {
            "name": "Method 1: Precompiled wheels only (recommended)",
            "cmd": f"pip install --proxy {proxy_config} --target {packages_dir} -r {requirements_file} --only-binary=all --timeout 120"
        },
        {
            "name": "Method 2: Precompiled wheels with retries",
            "cmd": f"pip install --proxy {proxy_config} --target {packages_dir} -r {requirements_file} --only-binary=all --timeout 120 --retries 3"
        },
        {
            "name": "Method 3: Prefer wheels but allow source",
            "cmd": f"pip install --proxy {proxy_config} --target {packages_dir} -r {requirements_file} --prefer-binary --timeout 120"
        },
        {
            "name": "Method 4: No proxy with wheels only",
            "cmd": f"pip install --target {packages_dir} -r {requirements_file} --only-binary=all --timeout 120"
        },
        {
            "name": "Method 5: Force reinstall with wheels",
            "cmd": f"pip install --proxy {proxy_config} --target {packages_dir} -r {requirements_file} --only-binary=all --force-reinstall --timeout 120"
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
            print(f"[ERROR] {result.stderr[:300]}...")
            print()
    
    print("[ERROR] All wheel installation methods failed")
    print("[INFO] This might be due to:")
    print("  - Network connectivity issues")
    print("  - Proxy configuration problems")
    print("  - Package compatibility issues")
    print("  - Missing build tools")
    print()
    print("[INFO] You can try installing packages individually:")
    print("  pip install --proxy http://proxy-enclave.altera.com:912 --target python_packages flask --only-binary=all")
    print("  pip install --proxy http://proxy-enclave.altera.com:912 --target python_packages flask-cors --only-binary=all")
    print("  pip install --proxy http://proxy-enclave.altera.com:912 --target python_packages pydub --only-binary=all")
    return False

def install_individual_packages():
    """Install packages individually to identify problematic ones"""
    print("=" * 50)
    print("   Individual Package Installation")
    print("=" * 50)
    print()
    
    app_dir = Path(__file__).parent
    packages_dir = app_dir / "python_packages"
    packages_dir.mkdir(exist_ok=True)
    
    proxy_config = "http://proxy-enclave.altera.com:912"
    
    # Common packages that usually have precompiled wheels
    packages = [
        "flask",
        "flask-cors", 
        "pydub",
        "requests",
        "werkzeug",
        "jinja2",
        "markupsafe",
        "itsdangerous",
        "click",
        "blinker"
    ]
    
    print("[INFO] Installing packages individually...")
    print()
    
    success_count = 0
    failed_packages = []
    
    for package in packages:
        print(f"[INFO] Installing {package}...")
        cmd = f"pip install --proxy {proxy_config} --target {packages_dir} {package} --only-binary=all --timeout 120"
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"[SUCCESS] {package} installed successfully")
            success_count += 1
        else:
            print(f"[WARNING] {package} failed to install")
            failed_packages.append(package)
            print(f"[ERROR] {result.stderr[:200]}...")
        print()
    
    print("=" * 50)
    print("   Individual Installation Summary")
    print("=" * 50)
    print()
    print(f"[SUCCESS] {success_count} packages installed successfully")
    print(f"[WARNING] {len(failed_packages)} packages failed")
    
    if failed_packages:
        print(f"[INFO] Failed packages: {', '.join(failed_packages)}")
        print("[INFO] You may need to install these manually or find alternatives")
    
    return success_count > 0

def main():
    """Main execution function"""
    print("=" * 60)
    print("   Python Wheel Installation Tool")
    print("=" * 60)
    print()
    print("This script installs Python dependencies using precompiled wheels")
    print("to avoid build errors and compilation issues.")
    print()
    
    # Try wheel installation first
    wheel_success = install_python_wheels()
    
    if not wheel_success:
        print()
        print("=" * 60)
        print()
        print("[INFO] Wheel installation failed, trying individual packages...")
        individual_success = install_individual_packages()
        
        if individual_success:
            print()
            print("[SUCCESS] Some packages installed successfully!")
            print("[INFO] You can proceed with creating the standalone executable")
        else:
            print()
            print("[ERROR] All installation methods failed")
            print("[INFO] Please check your network connection and proxy settings")
    else:
        print()
        print("[SUCCESS] All packages installed successfully!")
        print("[INFO] You can now run CREATE_STANDALONE_EXECUTABLE.bat")
    
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
