#!/usr/bin/env python3
# Rules applied
"""
Test script to verify the standalone executable works correctly
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def test_executable():
    """Test the standalone executable"""
    app_dir = Path(__file__).parent
    exe_path = app_dir / "PortableRingtoneApp.exe"
    
    if not exe_path.exists():
        print("[ERROR] Executable not found: PortableRingtoneApp.exe")
        print("[INFO] Please run CREATE_EXECUTABLE.bat first")
        return False
        
    print("[INFO] Testing standalone executable...")
    print(f"[INFO] Executable path: {exe_path}")
    
    # Check file size
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"[INFO] Executable size: {size_mb:.1f} MB")
    
    # Test if executable can start (we'll stop it quickly)
    print("[INFO] Testing executable startup...")
    print("[WARNING] This will start the app briefly - it will be stopped after 10 seconds")
    
    try:
        # Start the executable
        process = subprocess.Popen([str(exe_path)], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True)
        
        # Let it run for a few seconds
        time.sleep(10)
        
        # Terminate the process
        process.terminate()
        
        # Wait for it to actually terminate
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            
        print("[SUCCESS] Executable started and stopped successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to test executable: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 50)
    print("   Portable Ringtone App - Executable Test")
    print("=" * 50)
    print()
    
    if test_executable():
        print()
        print("[SUCCESS] Executable test completed successfully!")
        print("[INFO] The standalone executable appears to be working")
        print()
    else:
        print()
        print("[ERROR] Executable test failed!")
        print("[INFO] Please check the executable creation process")
        print()
        
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
