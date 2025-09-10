# FFmpeg Installation Guide for Portable App

## Issue
The portable app is showing FFmpeg warnings because FFmpeg is not installed. FFmpeg is required for MP3 conversion functionality.

## Current Status
- ✅ WAV ringtone creation works
- ❌ MP3 conversion is disabled (FFmpeg missing)
- ⚠️ You'll see warnings about FFmpeg not being found

## Solutions

### Option 1: Manual FFmpeg Installation (Recommended)

1. **Download FFmpeg:**
   - Go to: https://ffmpeg.org/download.html
   - Download the Windows build (static version)
   - Or use: https://github.com/BtbN/FFmpeg-Builds/releases

2. **Install to Portable App:**
   - Extract the downloaded ZIP file
   - Copy the `bin` folder contents to: `portable_app/ffmpeg/bin/`
   - Ensure `ffmpeg.exe` is in: `portable_app/ffmpeg/bin/ffmpeg.exe`

3. **Verify Installation:**
   - Restart the portable app
   - The warnings should disappear
   - MP3 conversion should work

### Option 2: System-wide FFmpeg Installation

1. **Using Chocolatey (if available):**
   ```powershell
   choco install ffmpeg
   ```

2. **Using WinGet (Windows 10/11):**
   ```powershell
   winget install "FFmpeg (Essentials Build)"
   ```

3. **Manual System Installation:**
   - Download FFmpeg from official site
   - Extract to `C:\ffmpeg\`
   - Add `C:\ffmpeg\bin` to your system PATH

### Option 3: Use WAV Only (No FFmpeg Required)

If you don't need MP3 conversion:
- The app works perfectly with WAV files
- WAV files are higher quality than MP3
- No additional software required

## Testing FFmpeg Installation

After installation, test by running:
```powershell
cd portable_app/ffmpeg/bin
./ffmpeg.exe -version
```

## Troubleshooting

### Network Issues
If you can't download FFmpeg due to network restrictions:
1. Use a different network connection
2. Download on another computer and transfer the files
3. Ask your IT department for the FFmpeg installer

### Permission Issues
If you get permission errors:
1. Run PowerShell as Administrator
2. Or install to a user directory instead of system directories

### Still Getting Warnings
If warnings persist after installation:
1. Restart the portable app completely
2. Check that `ffmpeg.exe` is in the correct location
3. Verify the file is not corrupted

## Current App Functionality

**Without FFmpeg:**
- ✅ Upload audio files
- ✅ Create WAV ringtones
- ✅ Play ringtones
- ✅ Schedule ringtones
- ❌ MP3 conversion (disabled)

**With FFmpeg:**
- ✅ All above features
- ✅ MP3 conversion enabled
- ✅ Dual format output (WAV + MP3)

## Support

If you continue to have issues:
1. Check the `ai-actions.log` file for detailed error messages
2. Ensure you have the latest version of the portable app
3. Try the manual installation method first
