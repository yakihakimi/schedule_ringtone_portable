# 🎵 Portable Ringtone Creator App

A portable version of the Ringtone Creator application that can be copied to any Windows computer and run without installation.

## 📋 Requirements

The portable app can automatically install Python if it's not present on the target computer:

- **Python 3.13+** - Will be automatically downloaded and installed if not present
- **Node.js LTS** - Download from [nodejs.org](https://nodejs.org/) (manual installation required)
- **npm** (comes with Node.js)

### 🔧 Automatic Python Installation

If Python is not installed, the app will automatically:
1. Download Python 3.13.1 from the official Python website
2. Install it silently with all necessary components
3. Add Python to the system PATH
4. Verify the installation

**No manual intervention required!** The installation process is completely automated.

## 🚀 Quick Start

### First Time Setup (Required)
1. **Copy the entire `portable_app` folder** to your computer
2. **Run `SETUP_WITH_FFMPEG.bat`** to install all dependencies including FFmpeg
   - This will automatically install Python if needed
   - You only need to install Node.js manually
3. **Or run `SETUP.bat`** for basic setup (FFmpeg installation optional)
4. **Or run `INSTALL_PYTHON.bat`** to install only Python

### 🔧 Installation Scripts

The app includes several installation scripts:

- **`INSTALL_PYTHON.bat`** - Simple Python installer (recommended for Python-only installation)
- **`install_python_auto.bat`** - Advanced Python installer with full automation
- **`install_python_auto.ps1`** - PowerShell version of the Python installer
- **`SETUP_WITH_FFMPEG.bat`** - Complete setup including Python, Node.js dependencies, and FFmpeg
- **`SETUP.bat`** - Basic setup without FFmpeg

### Running the App
**🎯 Recommended: Just double-click `START.bat`** - It handles everything automatically!

The app includes multiple launchers with different levels of automation:

1. **`START.bat`** - One-click launcher (calls universal launcher)
2. **`START_APP.bat`** - Main launcher with comprehensive checks
3. **`START_APP_UNIVERSAL.bat`** - Universal launcher (handles all scenarios)
4. **`START_APP.ps1`** - PowerShell launcher with advanced features
5. **`START_APP_SIMPLE.ps1`** - Simple PowerShell launcher
6. **`START_APP_FIXED.bat`** - Fixed batch launcher
7. **`MANUAL_START.bat`** - Manual step-by-step launcher

**How it works:** The launchers automatically try different methods until one succeeds. If something fails, they call other batch files accordingly.

**Browser Opening:** By default, React automatically opens your browser when the frontend starts. If you prefer manual control, use `START_APP_NO_AUTO_BROWSER.bat`.

### Manual Start (Alternative)
1. Open a command prompt in this directory
2. Run: `cd backend && python server.py` (in one window)
3. Run: `npm start` (in another window)
4. Open your browser to `http://localhost:3000`

## 📁 Directory Structure

```
portable_app/
├── backend/                 # Backend server files
│   ├── server.py           # Main Flask server
│   ├── play_ringtone.py    # Ringtone playback script
│   └── requirements.txt    # Python dependencies
├── src/                    # React frontend source
├── public/                 # Public web assets
├── node_modules/           # Frontend dependencies
├── ffmpeg/                 # FFmpeg installation directory
│   └── bin/               # FFmpeg executables (auto-installed)
├── package.json           # Node.js configuration
├── tsconfig.json          # TypeScript configuration
├── SETUP.bat              # Basic setup script
├── SETUP_WITH_FFMPEG.bat  # Complete setup with FFmpeg
├── INSTALL_FFMPEG.bat     # FFmpeg installation script
├── install_ffmpeg_auto.py # Python FFmpeg installer
├── install_ffmpeg_auto.ps1 # PowerShell FFmpeg installer
├── test_ffmpeg_install.bat # FFmpeg installation test
├── START.bat              # One-click launcher (recommended)
├── START_APP.bat          # Main launcher with full checks
├── START_APP_UNIVERSAL.bat # Universal launcher (handles everything)
├── START_APP_NO_PROFILE.bat # No-profile launcher (bypasses PowerShell issues)
├── START_APP_NO_AUTO_BROWSER.bat # Manual browser control launcher
├── START_APP.ps1          # PowerShell launcher
├── START_APP_FIXED.bat    # Fixed batch launcher
├── START_APP_SIMPLE.ps1   # Simple PowerShell launcher
├── MANUAL_START.bat       # Manual step-by-step launcher
├── FFMPEG_INSTALLATION_GUIDE.md # FFmpeg installation guide
└── README.md              # This file
```

## 🔧 Features

- **Audio Upload**: Upload MP3 or WAV files
- **Ringtone Creation**: Create custom ringtones with start/end time selection
- **Dual Format Output**: Creates both WAV and MP3 versions
- **Automatic FFmpeg Installation**: Downloads and installs FFmpeg automatically
- **Ringtone Management**: View, play, edit, and delete ringtones
- **Scheduled Playback**: Schedule ringtones to play at specific times
- **Search Functionality**: Find ringtones quickly
- **Portable**: No installation required, just copy and run
- **Proxy Support**: Works behind corporate firewalls with proxy configuration

## 🌐 Access Points

- **Frontend**: http://localhost:3000 (Main application)
- **Backend API**: http://localhost:5000 (REST API)

## 📝 Usage Instructions

1. **Upload Audio**: Click "Choose File" to select an MP3 or WAV file
2. **Create Ringtone**: 
   - Set start and end times using the audio player
   - Click "Create Ringtone" to generate your custom ringtone
3. **Manage Ringtones**: 
   - View all created ringtones in the "Existing Ringtones" tab
   - Play, edit, download, or delete ringtones
   - Use the search bar to find specific ringtones
4. **Schedule Ringtones**: 
   - Go to the "Schedule Ringtone" tab
   - Select a ringtone and set the time
   - The ringtone will play automatically at the scheduled time

## 🛠️ Troubleshooting

### "Python is not installed" Error
- Download and install Python from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation
- Restart your command prompt after installation

### "Node.js is not installed" Error
- Download and install Node.js LTS from [nodejs.org](https://nodejs.org/)
- npm will be installed automatically with Node.js
- Restart your command prompt after installation

### "Frontend dependencies not found" Error
- Run `SETUP.bat` to install all dependencies
- Or manually run: `npm install`
- Wait for installation to complete
- Try starting the app again

### "The filename, directory name, or volume label syntax is incorrect" Error
- Make sure you copied the entire `portable_app` folder
- Don't copy individual files - copy the whole folder
- Avoid copying to paths with special characters or spaces
- Try copying to a simple path like `C:\ringtone_app\`
- Run `SETUP.bat` after copying to the new location

### Port Already in Use Error
- Close any other applications using ports 3000 or 5000
- Or restart your computer to free up the ports

### Backend Server Won't Start
- Make sure Python is installed and in PATH
- Install Python dependencies: `pip install -r backend/requirements.txt`
- Check that no other application is using port 5000

### FFmpeg Warnings (MP3 Conversion Issues)
If you see warnings about FFmpeg not being found:
- **WAV ringtones work perfectly** without FFmpeg
- **MP3 conversion is disabled** when FFmpeg is missing
- To enable MP3 conversion:
  1. Run `INSTALL_FFMPEG.bat` for automatic installation
  2. Or run `SETUP_WITH_FFMPEG.bat` for complete setup with FFmpeg
  3. The app will automatically download and install FFmpeg
  4. See `FFMPEG_INSTALLATION_GUIDE.md` for manual installation steps
- **Alternative**: Use WAV format only (higher quality, no additional software needed)

### PowerShell Profile Issues (Anaconda/Conda Errors)
If you see errors like "conda.exe not found" or PowerShell profile issues:
- **Solution 1**: Use `START_APP_NO_PROFILE.bat` - bypasses PowerShell profile issues
- **Solution 2**: The main launchers now automatically try `-NoProfile` flag first
- **Solution 3**: Use batch file launchers instead of PowerShell ones
- **Root cause**: PowerShell profile trying to load Anaconda/Conda that's not properly installed

### Frontend Server Won't Start
- Make sure Node.js and npm are installed
- Run `npm install` to install dependencies
- Check that no other application is using port 3000

## 🔒 Security Notes

- The app runs locally on your computer
- No data is sent to external servers
- All ringtones are stored locally in the `backend` directory
- The app requires internet only for downloading dependencies

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Ensure all requirements are installed
3. Try running the manual start option
4. Check that ports 3000 and 5000 are not in use by other applications

## 🎯 System Requirements

- **Operating System**: Windows 10/11
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space
- **Network**: Internet connection for initial dependency installation

## 📄 License

This portable app is provided as-is for personal use. Please ensure you have the rights to any audio files you upload and create ringtones from.
