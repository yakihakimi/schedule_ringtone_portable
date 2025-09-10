#!/usr/bin/env python3
"""
Local package import handler for portable application
This module ensures that required packages are available even if not installed system-wide
"""
import sys
import os
import importlib.util
import zipfile
import tempfile
from pathlib import Path

# Get the directory where this script is located
BACKEND_DIR = Path(__file__).parent
PACKAGES_DIR = BACKEND_DIR / "packages"

def setup_local_packages():
    """
    Setup local packages by adding them to sys.path and extracting wheels if needed
    """
    if not PACKAGES_DIR.exists():
        print(f"⚠️ Packages directory not found: {PACKAGES_DIR}")
        return False
    
    # Add packages directory to Python path
    if str(PACKAGES_DIR) not in sys.path:
        sys.path.insert(0, str(PACKAGES_DIR))
        print(f"✅ Added packages directory to Python path: {PACKAGES_DIR}")
    
    # Extract wheel files if needed
    extracted_packages = []
    for wheel_file in PACKAGES_DIR.glob("*.whl"):
        try:
            # Extract wheel to a temporary directory
            with zipfile.ZipFile(wheel_file, 'r') as wheel:
                # Get package name from wheel filename
                package_name = wheel_file.stem.split('-')[0].replace('_', '-')
                
                # Create extraction directory
                extract_dir = PACKAGES_DIR / f"{package_name}_extracted"
                if not extract_dir.exists():
                    wheel.extractall(extract_dir)
                    extracted_packages.append(extract_dir)
                    print(f"✅ Extracted wheel: {wheel_file.name} -> {extract_dir}")
        except Exception as e:
            print(f"⚠️ Failed to extract wheel {wheel_file.name}: {e}")
    
    # Add extracted package directories to sys.path
    for extract_dir in extracted_packages:
        if str(extract_dir) not in sys.path:
            sys.path.insert(0, str(extract_dir))
    
    return True

def safe_import(module_name, package_name=None, fallback_import=None):
    """
    Safely import a module with fallback to local packages
    
    Args:
        module_name: Name of the module to import
        package_name: Name of the package (for pip-style imports)
        fallback_import: Alternative import name if the main one fails
    
    Returns:
        The imported module or None if import failed
    """
    try:
        # Try normal import first
        return importlib.import_module(module_name)
    except ImportError as e:
        print(f"⚠️ Failed to import {module_name}: {e}")
        
        # Try fallback import name if provided
        if fallback_import:
            try:
                return importlib.import_module(fallback_import)
            except ImportError:
                pass
        
        # Try to import from local packages
        if PACKAGES_DIR.exists():
            try:
                # Look for the package in extracted directories
                for item in PACKAGES_DIR.iterdir():
                    if item.is_dir() and item.name.endswith('_extracted'):
                        package_dir = item
                        # Add to sys.path temporarily
                        if str(package_dir) not in sys.path:
                            sys.path.insert(0, str(package_dir))
                        
                        try:
                            return importlib.import_module(module_name)
                        except ImportError:
                            continue
            except Exception as e:
                print(f"⚠️ Failed to import {module_name} from local packages: {e}")
        
        print(f"❌ Could not import {module_name} from system or local packages")
        return None

def import_required_packages():
    """
    Import all required packages with fallback to local versions
    """
    print("🔧 Setting up local package imports...")
    
    # Setup local packages
    setup_local_packages()
    
    # Import required packages
    packages = {
        'flask': 'Flask',
        'flask_cors': 'flask_cors',
        'pydub': 'pydub',
        'pygame': 'pygame',
        'requests': 'requests',
        'dateutil': 'python_dateutil',
        'psutil': 'psutil',
        'werkzeug': 'werkzeug'
    }
    
    imported_packages = {}
    
    for import_name, display_name in packages.items():
        module = safe_import(import_name)
        if module:
            imported_packages[import_name] = module
            print(f"✅ Successfully imported {display_name}")
        else:
            print(f"❌ Failed to import {display_name}")
    
    return imported_packages

# Auto-setup when this module is imported
if __name__ != "__main__":
    # Only auto-setup if we're being imported, not run directly
    setup_local_packages()
