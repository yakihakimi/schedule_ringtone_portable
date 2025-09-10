# Rules applied
# PowerShell script to play ringtones via Windows Task Scheduler
param(
    [Parameter(Mandatory=$true)]
    [string]$RingtonePath,
    
    [Parameter(Mandatory=$false)]
    [int]$Volume = 50
)

try {
    # Log the action
    $logFile = Join-Path $env:TEMP "ringtone_scheduler.log"
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logFile -Value "$timestamp - Playing ringtone: $RingtonePath"
    
    # Check if the ringtone file exists
    if (-not (Test-Path $RingtonePath)) {
        Add-Content -Path $logFile -Value "$timestamp - ERROR: Ringtone file not found: $RingtonePath"
        exit 1
    }
    
    # Create WScript.Shell object to play the sound
    $shell = New-Object -ComObject WScript.Shell
    
    # Play the ringtone using Windows Media Player
    $shell.Run("wmplayer.exe /play /close `"$RingtonePath`"", 0, $false)
    
    # Alternative method using PowerShell's built-in sound capabilities
    # This method works for WAV files
    if ($RingtonePath -like "*.wav") {
        Add-Type -AssemblyName System.Windows.Forms
        $sound = [System.Media.SoundPlayer]::new($RingtonePath)
        $sound.PlaySync()
    }
    
    Add-Content -Path $logFile -Value "$timestamp - Successfully played ringtone: $RingtonePath"
    exit 0
    
} catch {
    $errorMsg = $_.Exception.Message
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logFile = Join-Path $env:TEMP "ringtone_scheduler.log"
    Add-Content -Path $logFile -Value "$timestamp - ERROR: $errorMsg"
    exit 1
}
