#!/usr/bin/env python3
"""
Python script to play ringtone files using pygame or system audio.
This script is called by Windows Task Scheduler to play scheduled ringtones.
"""

import sys
import os
import time
import logging
from pathlib import Path

# Set up logging with proper file location

# Create log file in a safe location
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, 'ringtone_playback.log')

# Try to set up file logging, fall back to console only if it fails
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a'),
            logging.StreamHandler()
        ]
    )
except PermissionError:
    # Fall back to console-only logging if file logging fails
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
logger = logging.getLogger(__name__)

def play_ringtone_with_pygame(ringtone_path):
    """Play ringtone using pygame (preferred method)"""
    try:
        import os
        import sys
        
        # Set environment variables BEFORE importing pygame to suppress messages and windows
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
        os.environ['SDL_AUDIODRIVER'] = 'directsound'  # Use DirectSound for Windows
        
        # Redirect stdout and stderr BEFORE importing pygame
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        
        try:
            import pygame
            
            # Initialize pygame with no display and no video
            pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            
            # Ensure no display is initialized
            if not pygame.display.get_init():
                pygame.display.init()
                pygame.display.quit()  # Immediately quit display
            
            pygame.mixer.music.load(ringtone_path)
            pygame.mixer.music.play()
            
            # Wait for the music to finish playing
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.quit()
        finally:
            # Restore stdout and stderr
            sys.stdout.close()
            sys.stderr.close()
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        logger.info(f"Successfully played ringtone with pygame: {ringtone_path}")
        return True
        
    except ImportError:
        logger.warning("pygame not available, trying alternative method")
        return False
    except Exception as e:
        logger.error(f"Error playing ringtone with pygame: {e}")
        return False

def play_ringtone_with_winsound(ringtone_path):
    """Play ringtone using winsound (Windows only, WAV files only)"""
    try:
        import winsound
        
        # Check if file is WAV
        if not ringtone_path.lower().endswith('.wav'):
            logger.warning("⚠️ winsound only supports WAV files")
            return False
            
        # Play the sound synchronously (blocking)
        winsound.PlaySound(ringtone_path, winsound.SND_FILENAME)
        
        logger.info(f"Successfully played ringtone with winsound: {ringtone_path}")
        return True
        
    except ImportError:
        logger.warning("winsound not available")
        return False
    except Exception as e:
        logger.error(f"Error playing ringtone with winsound: {e}")
        return False

def play_ringtone_with_system(ringtone_path):
    """Play ringtone using system command (fallback method)"""
    try:
        import subprocess
        
        # Try different system commands based on OS
        if os.name == 'nt':  # Windows
            # Use Windows Media Player
            cmd = ['wmplayer', '/play', '/close', ringtone_path]
        else:  # Linux/Mac
            # Try common audio players
            for player in ['aplay', 'paplay', 'afplay']:
                try:
                    subprocess.run([player, ringtone_path], check=True, timeout=30)
                    logger.info(f"Successfully played ringtone with {player}: {ringtone_path}")
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
                    continue
                    
        logger.warning("No suitable system audio player found")
        return False
        
    except Exception as e:
        logger.error(f"Error playing ringtone with system command: {e}")
        return False

def main():
    """Main function to play ringtone"""
    # Check if running in verbose mode (default is silent mode)
    verbose_mode = len(sys.argv) > 2 and sys.argv[2] == '--verbose'
    silent_mode = not verbose_mode
    
    # Create a lock file to prevent multiple instances
    lock_file = os.path.join(os.path.dirname(__file__), 'play_ringtone.lock')
    
    # Check if another instance is already running
    if os.path.exists(lock_file):
        try:
            # Check if the lock file is recent (less than 30 seconds old)
            lock_age = time.time() - os.path.getmtime(lock_file)
            if lock_age < 30:
                logger.error("Another instance of the script is already running")
                sys.exit(1)
            else:
                # Remove stale lock file
                os.remove(lock_file)
        except:
            pass
    
    # Create lock file
    try:
        with open(lock_file, 'w') as f:
            f.write(str(os.getpid()))
    except:
        pass
    
    try:
        if not silent_mode:
            logger.info("=" * 60)
            logger.info("RINGTONE PLAYBACK SCRIPT STARTED")
            logger.info("=" * 60)
        
        if len(sys.argv) < 2:
            logger.error("Usage: python play_ringtone.py <ringtone_path> [--verbose]")
            sys.exit(1)
        
        ringtone_path = sys.argv[1]
        
        # Validate file exists
        if not os.path.exists(ringtone_path):
            logger.error(f"Ringtone file not found: {ringtone_path}")
            sys.exit(1)
        
        if not silent_mode:
            logger.info(f"Attempting to play ringtone: {ringtone_path}")
            logger.info(f"File size: {os.path.getsize(ringtone_path)} bytes")
            logger.info(f"File extension: {os.path.splitext(ringtone_path)[1]}")
        
        # Try different methods in order of preference
        # Use winsound first for Windows (no windows, more reliable)
        methods = [
            ("winsound", play_ringtone_with_winsound),
            ("pygame", play_ringtone_with_pygame),
            ("system", play_ringtone_with_system)
        ]
        
        for method_name, method_func in methods:
            if not silent_mode:
                logger.info(f"Trying {method_name} method...")
            if method_func(ringtone_path):
                if not silent_mode:
                    logger.info(f"Successfully played ringtone using {method_name}")
                sys.exit(0)
        
        # If all methods failed
        logger.error("All playback methods failed")
        sys.exit(1)
        
    finally:
        # Clean up lock file
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
        except:
            pass

if __name__ == "__main__":
    main()
