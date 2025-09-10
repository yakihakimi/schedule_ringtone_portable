# Single Instance Detection Fix

## Problem Identified

The executable was incorrectly detecting multiple instances when only one was running:
```
[DEBUG] Found 2 similar processes
[WARNING] Multiple instances detected
[ERROR] Another instance of the application is already running
```

**Root Cause**: The single instance check was counting the current process itself as a "similar process", leading to false positives.

## Solution: Dual-Method Single Instance Detection

I've implemented a robust dual-method approach that combines lock file management with improved process detection:

### 1. Lock File Method (Primary)

**How it works:**
- Creates a lock file (`portable_ringtone_app.lock`) containing the current process PID
- Checks if lock file exists and if the PID is still running
- Removes stale lock files from crashed/terminated processes
- Automatically cleans up lock file on application exit

**Benefits:**
- **More Reliable**: Not affected by process name variations
- **Crash Recovery**: Automatically handles stale lock files
- **Cross-Platform**: Works consistently across different systems
- **Automatic Cleanup**: Uses `atexit` to ensure cleanup on exit

### 2. Process Detection Method (Backup)

**Improved Logic:**
- **Excludes Current Process**: Skips the current process PID to avoid false positives
- **Better Filtering**: Only counts processes with matching command lines
- **Detailed Logging**: Shows exactly which processes are found
- **Fallback Safety**: Used as backup if lock file method fails

## Implementation Details

### Lock File Management

```python
def check_single_instance(self):
    # Method 1: Lock file approach
    lock_file = self.app_dir / "portable_ringtone_app.lock"
    
    if lock_file.exists():
        # Check if process is still running
        with open(lock_file, 'r') as f:
            pid = int(f.read().strip())
        
        try:
            proc = psutil.Process(pid)
            if proc.is_running():
                return False  # Another instance is running
            else:
                lock_file.unlink()  # Remove stale lock file
        except psutil.NoSuchProcess:
            lock_file.unlink()  # Remove stale lock file
    
    # Create new lock file
    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))
```

### Automatic Cleanup

```python
def cleanup_lock_file(self):
    """Clean up the lock file when the application exits"""
    try:
        lock_file = self.app_dir / "portable_ringtone_app.lock"
        if lock_file.exists():
            lock_file.unlink()
    except Exception as e:
        print(f"[WARNING] Could not clean up lock file: {e}")

# Register cleanup function
atexit.register(self.cleanup_lock_file)
```

### Improved Process Detection

```python
# Count processes with the same name, excluding the current process
same_name_processes = []
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        # Skip the current process
        if proc.info['pid'] == current_pid:
            continue
            
        if proc.info['name'] == current_name:
            # Check if it's the same executable
            if proc.info['cmdline'] and len(proc.info['cmdline']) > 0:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'PortableRingtoneApp' in cmdline or 'py_start_app_standalone' in cmdline:
                    same_name_processes.append(proc.info['pid'])
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
```

## Cleanup Tools

### Manual Cleanup Script

**`cleanup_lock_files.py`** - Interactive cleanup tool:
- Finds all lock files in the directory
- Shows what files will be deleted
- Asks for confirmation before deletion
- Provides detailed feedback

**`CLEANUP_LOCK_FILES.bat`** - Easy-to-use batch file:
- Runs the cleanup script
- Handles Python path issues
- Provides clear instructions

### Usage

```bash
# Run the cleanup tool
CLEANUP_LOCK_FILES.bat

# Or run directly
python cleanup_lock_files.py
```

## Expected Behavior

### First Run
```
[DEBUG] Checking for multiple instances...
[DEBUG] Lock file path: C:\yaki\c\portable_ringtone_app.lock
[DEBUG] Created lock file with PID: 18904
[DEBUG] Also checking process list as backup...
[DEBUG] Current process: PortableRingtoneApp_Robust.exe (PID: 18904)
[DEBUG] Skipping current process (PID: 18904)
[DEBUG] Found 0 other similar processes (excluding current)
[SUCCESS] Single instance check passed
```

### Second Run (While First is Running)
```
[DEBUG] Checking for multiple instances...
[DEBUG] Lock file path: C:\yaki\c\portable_ringtone_app.lock
[DEBUG] Lock file exists, checking if process is still running...
[DEBUG] Lock file contains PID: 18904
[WARNING] Another instance is running (PID: 18904)
[ERROR] Another instance of the application is already running
```

### After Crash/Termination
```
[DEBUG] Checking for multiple instances...
[DEBUG] Lock file path: C:\yaki\c\portable_ringtone_app.lock
[DEBUG] Lock file exists, checking if process is still running...
[DEBUG] Lock file contains PID: 18904
[DEBUG] Process 18904 is not running, removing stale lock file
[DEBUG] Created lock file with PID: 18905
[SUCCESS] Single instance check passed
```

## Troubleshooting

### If you still get "multiple instances detected":

1. **Run the cleanup tool:**
   ```bash
   CLEANUP_LOCK_FILES.bat
   ```

2. **Check for zombie processes:**
   ```bash
   tasklist | findstr PortableRingtoneApp
   ```

3. **Kill any remaining processes:**
   ```bash
   taskkill /F /IM PortableRingtoneApp_Robust.exe
   ```

4. **Check for lock files manually:**
   ```bash
   dir *.lock
   ```

### If the executable still won't start:

1. **Check the debug output** for specific error messages
2. **Verify the lock file location** is correct
3. **Check file permissions** in the executable directory
4. **Try running as administrator** if permission issues exist

## File Changes

### Modified Files:
- `py_start_app_standalone.py` - Enhanced single instance detection with lock file method
- Added `atexit` import for automatic cleanup

### New Files:
- `cleanup_lock_files.py` - Manual cleanup tool
- `CLEANUP_LOCK_FILES.bat` - Batch file for easy cleanup

### Key Improvements:
- **Lock File Method**: More reliable than process detection alone
- **Automatic Cleanup**: Ensures lock files are removed on exit
- **Stale File Handling**: Removes lock files from crashed processes
- **Improved Process Detection**: Excludes current process to avoid false positives
- **Comprehensive Logging**: Detailed debug output for troubleshooting
- **Manual Cleanup Tools**: Easy way to resolve lock file conflicts

The fix ensures that the single instance detection works correctly and doesn't prevent legitimate application starts while still preventing actual multiple instances.
