# Rules applied
import subprocess
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WindowsTaskSchedulerService:
    """
    Service to manage Windows Task Scheduler tasks for ringtone scheduling.
    This service creates, updates, deletes, and manages Windows scheduled tasks.
    """
    
    def __init__(self):
        self.task_folder = ""  # Use root folder instead of custom folder
        self.ringtone_player_script = self._get_ringtone_player_script_path()
        self.python_exe = self._find_python_executable()
        # No need to ensure task folder exists for root folder
    
    def _get_ringtone_player_script_path(self) -> str:
        """Get the path to the ringtone player Python script."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, "play_ringtone.py")
    
    def _find_python_executable(self) -> str:
        """Find any installed Python executable on the system."""
        # Rules applied - Check for Python in common locations
        possible_paths = [
            r"C:\Program Files\Python313\pythonw.exe",  # Rules specified path
            r"C:\Program Files\Python312\pythonw.exe",
            r"C:\Program Files\Python311\pythonw.exe",
            r"C:\Program Files\Python310\pythonw.exe",
            r"C:\Program Files\Python39\pythonw.exe",
            r"C:\Program Files\Python38\pythonw.exe",
            r"C:\Users\{}\AppData\Local\Programs\Python\Python313\pythonw.exe".format(os.getenv('USERNAME', '')),
            r"C:\Users\{}\AppData\Local\Programs\Python\Python312\pythonw.exe".format(os.getenv('USERNAME', '')),
            r"C:\Users\{}\AppData\Local\Programs\Python\Python311\pythonw.exe".format(os.getenv('USERNAME', '')),
            r"C:\Users\{}\AppData\Local\Programs\Python\Python310\pythonw.exe".format(os.getenv('USERNAME', '')),
            r"C:\Users\{}\AppData\Local\Programs\Python\Python39\pythonw.exe".format(os.getenv('USERNAME', '')),
            r"C:\Users\{}\AppData\Local\Programs\Python\Python38\pythonw.exe".format(os.getenv('USERNAME', '')),
        ]
        
        # First check the rules-specified path
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"✅ Found Python executable: {path}")
                return path
        
        # Try to find Python in PATH
        try:
            result = subprocess.run(['where', 'pythonw.exe'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                python_path = result.stdout.strip().split('\n')[0]
                if os.path.exists(python_path):
                    logger.info(f"✅ Found Python executable in PATH: {python_path}")
                    return python_path
        except Exception as e:
            logger.warning(f"⚠️ Could not find Python in PATH: {e}")
        
        # Try to find Python in PATH (alternative)
        try:
            result = subprocess.run(['where', 'python.exe'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                python_path = result.stdout.strip().split('\n')[0]
                if os.path.exists(python_path):
                    logger.info(f"✅ Found Python executable in PATH: {python_path}")
                    return python_path
        except Exception as e:
            logger.warning(f"⚠️ Could not find Python in PATH: {e}")
        
        # Fallback to the rules-specified path (even if it doesn't exist)
        fallback_path = r"C:\Program Files\Python313\pythonw.exe"
        logger.warning(f"⚠️ No Python executable found, using fallback: {fallback_path}")
        return fallback_path
    
    
    
    def _run_schtasks_command(self, args: List[str]) -> Tuple[bool, str, str]:
        """Run a schtasks command and return success status, stdout, and stderr."""
        try:
            cmd = ["schtasks"] + args
            logger.info(f"🔧 Running command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=False,
                timeout=30
            )
            
            success = result.returncode == 0
            logger.info(f"📋 Command result - Success: {success}, Return code: {result.returncode}")
            
            if result.stdout:
                logger.info(f"📤 stdout: {result.stdout}")
            if result.stderr:
                logger.info(f"📤 stderr: {result.stderr}")
            
            return success, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            logger.error("❌ Command timed out")
            return False, "", "Command timed out"
        except Exception as e:
            logger.error(f"❌ Error running command: {e}")
            return False, "", str(e)
    
    
    def create_scheduled_task(self, task_name: str, ringtone_path: str, time: str, days: List[int]) -> bool:
        """
        Create a Windows scheduled task for a ringtone.
        
        Args:
            task_name: Unique name for the task
            ringtone_path: Full path to the ringtone file
            time: Time in HH:MM format
            days: List of days (0=Sunday, 1=Monday, etc.)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure the ringtone player script exists
            if not os.path.exists(self.ringtone_player_script):
                logger.error(f"❌ Ringtone player script not found: {self.ringtone_player_script}")
                return False
            
            # Convert days to schtasks format
            day_mapping = {
                0: "SUN",  # Sunday
                1: "MON",  # Monday
                2: "TUE",  # Tuesday
                3: "WED",  # Wednesday
                4: "THU",  # Thursday
                5: "FRI",  # Friday
                6: "SAT"   # Saturday
            }
            
            day_list = ",".join([day_mapping[day] for day in days])
            
            # Use the detected Python executable
            python_exe = self.python_exe
            test_command = f'"{python_exe}" "{self.ringtone_player_script}" "{ringtone_path}"'
            
            logger.info(f"🔍 Using Python executable: {python_exe}")
            logger.info(f"🔍 Test command length: {len(test_command)} chars")
            
            if len(test_command) > 261:
                # For existing long filenames, create a Python wrapper script
                logger.info(f"⚠️ Command too long ({len(test_command)} chars), creating Python wrapper")
                wrapper_script = os.path.join(os.path.dirname(__file__), "play_ringtone_wrapper.py")
                
                # Create a Python wrapper script that imports and calls the main function
                wrapper_content = f'''#!/usr/bin/env python3
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the play_ringtone script
from play_ringtone import main

# Set the command line arguments
sys.argv = ["play_ringtone_wrapper.py", r"{ringtone_path}"]

# Run the main function
main()
'''
                try:
                    with open(wrapper_script, 'w', encoding='utf-8') as f:
                        f.write(wrapper_content)
                    logger.info(f"✅ Created Python wrapper: {wrapper_script}")
                except Exception as e:
                    logger.error(f"❌ Error creating Python wrapper: {e}")
                    return False
                
                args = [
                    "/create",
                    "/tn", f"Ringtone_{task_name}",
                    "/tr", f"\"{python_exe}\" \"{wrapper_script}\"",
                    "/sc", "weekly",
                    "/d", day_list,
                    "/st", time,
                    "/f"  # Force creation
                ]
            else:
                # Use pythonw.exe directly for short filenames
                logger.info(f"✅ Command length OK ({len(test_command)} chars), using Python directly")
                args = [
                    "/create",
                    "/tn", f"Ringtone_{task_name}",
                    "/tr", f"\"{python_exe}\" \"{self.ringtone_player_script}\" \"{ringtone_path}\"",
                    "/sc", "weekly",
                    "/d", day_list,
                    "/st", time,
                    "/f"  # Force creation
                ]
            
            success, stdout, stderr = self._run_schtasks_command(args)
            
            if success:
                logger.info(f"✅ Created scheduled task: {task_name}")
                return True
            else:
                logger.error(f"❌ Failed to create scheduled task: {task_name}")
                logger.error(f"Error: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating scheduled task: {e}")
            return False
    
    def delete_scheduled_task(self, task_name: str) -> bool:
        """
        Delete a Windows scheduled task.
        
        Args:
            task_name: Name of the task to delete
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            args = [
                "/delete",
                "/tn", f"Ringtone_{task_name}",
                "/f"  # Force deletion
            ]
            
            success, stdout, stderr = self._run_schtasks_command(args)
            
            if success:
                logger.info(f"✅ Deleted scheduled task: {task_name}")
                return True
            else:
                logger.error(f"❌ Failed to delete scheduled task: {task_name}")
                logger.error(f"Error: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting scheduled task: {e}")
            return False
    
    def enable_scheduled_task(self, task_name: str) -> bool:
        """
        Enable a Windows scheduled task.
        
        Args:
            task_name: Name of the task to enable
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            args = [
                "/change",
                "/tn", f"Ringtone_{task_name}",
                "/enable"
            ]
            
            success, stdout, stderr = self._run_schtasks_command(args)
            
            if success:
                logger.info(f"✅ Enabled scheduled task: {task_name}")
                return True
            else:
                logger.error(f"❌ Failed to enable scheduled task: {task_name}")
                logger.error(f"Error: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error enabling scheduled task: {e}")
            return False
    
    def disable_scheduled_task(self, task_name: str) -> bool:
        """
        Disable a Windows scheduled task.
        
        Args:
            task_name: Name of the task to disable
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            args = [
                "/change",
                "/tn", f"Ringtone_{task_name}",
                "/disable"
            ]
            
            success, stdout, stderr = self._run_schtasks_command(args)
            
            if success:
                logger.info(f"✅ Disabled scheduled task: {task_name}")
                return True
            else:
                logger.error(f"❌ Failed to disable scheduled task: {task_name}")
                logger.error(f"Error: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error disabling scheduled task: {e}")
            return False
    
    def get_task_status(self, task_name: str) -> Optional[str]:
        """
        Get the status of a Windows scheduled task.
        
        Args:
            task_name: Name of the task to check
        
        Returns:
            str: Task status or None if not found
        """
        try:
            args = [
                "/query",
                "/tn", f"Ringtone_{task_name}",
                "/fo", "csv",
                "/v"
            ]
            
            success, stdout, stderr = self._run_schtasks_command(args)
            
            if success and stdout:
                # Parse the CSV output to find the status
                lines = stdout.strip().split('\n')
                if len(lines) > 1:
                    # Skip header line and get the first data line
                    data_line = lines[1]
                    # The status is typically in one of the columns
                    # This is a simplified parsing - you might need to adjust based on actual output
                    if "Ready" in data_line:
                        return "Ready"
                    elif "Disabled" in data_line:
                        return "Disabled"
                    elif "Running" in data_line:
                        return "Running"
                
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting task status: {e}")
            return None
    
    def list_all_tasks(self) -> List[Dict]:
        """
        List all ringtone scheduler tasks.
        
        Returns:
            List of task information dictionaries
        """
        try:
            args = [
                "/query",
                "/fo", "csv",
                "/v"
            ]
            
            success, stdout, stderr = self._run_schtasks_command(args)
            
            tasks = []
            if success and stdout:
                lines = stdout.strip().split('\n')
                if len(lines) > 1:
                    # Parse CSV output
                    for line in lines[1:]:  # Skip header
                        if "Ringtone_" in line:
                            # This is one of our tasks
                            parts = line.split(',')
                            if len(parts) > 0:
                                task_name = parts[0].strip('"')
                                # Extract just the task name without the Ringtone_ prefix
                                if "Ringtone_" in task_name:
                                    clean_name = task_name.replace("Ringtone_", "")
                                    tasks.append({
                                        "name": clean_name,
                                        "full_name": task_name,
                                        "status": "Unknown"  # Would need more parsing to get actual status
                                    })
            
            return tasks
            
        except Exception as e:
            logger.error(f"❌ Error listing tasks: {e}")
            return []
    
    def test_ringtone_playback(self, ringtone_path: str) -> bool:
        """
        Test playing a ringtone immediately.
        
        Args:
            ringtone_path: Path to the ringtone file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Use the detected Python executable
            python_exe = self.python_exe
            test_command = f'"{python_exe}" "{self.ringtone_player_script}" "{ringtone_path}"'
            
            logger.info(f"🔍 Using Python executable for test: {python_exe}")
            logger.info(f"🔍 Test command length: {len(test_command)} chars")
            
            if len(test_command) > 261:
                # Use batch file wrapper for existing ringtones with long filenames
                logger.info(f"⚠️ Command too long ({len(test_command)} chars), using batch file wrapper")
                batch_script = os.path.join(os.path.dirname(__file__), "play_ringtone_short.bat")
                
                # Create the batch file if it doesn't exist
                if not os.path.exists(batch_script):
                    self._create_short_batch_file()
                
                cmd = [batch_script, ringtone_path]
            else:
                # Use Python file directly for short filenames
                logger.info(f"✅ Command length OK ({len(test_command)} chars), using Python directly")
                cmd = [python_exe, self.ringtone_player_script, ringtone_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully tested ringtone: {ringtone_path}")
                return True
            else:
                logger.error(f"❌ Failed to test ringtone: {ringtone_path}")
                logger.error(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error testing ringtone: {e}")
            return False

# Create singleton instance
task_scheduler_service = WindowsTaskSchedulerService()
