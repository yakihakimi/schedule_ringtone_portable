@echo off
echo Starting ringtone playback...
python "%~dp0play_ringtone.py" %*
echo.
echo Script execution completed.
echo Press any key to close this window...
pause > nul
