// Rules applied
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { AudioFile } from '../types/audio';
import ringtoneService from '../services/ringtoneService';

interface AudioPlayerProps {
  audioFile: AudioFile;
  onRingtoneCreated: (ringtone: AudioFile) => void;
}

const AudioPlayer: React.FC<AudioPlayerProps> = ({ audioFile, onRingtoneCreated }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [startTime, setStartTime] = useState(0);
  const [endTime, setEndTime] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [isCreatingRingtone, setIsCreatingRingtone] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  useEffect(() => {
    if (audioRef.current) {
      setDuration(audioFile.duration);
      setEndTime(audioFile.duration);
    }
  }, [audioFile]);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const updateTime = () => setCurrentTime(audio.currentTime);
    const handleEnded = () => setIsPlaying(false);
    const handleError = (e: Event) => {
      console.error('Audio error:', e);
      setError('Error playing audio file');
    };

    audio.addEventListener('timeupdate', updateTime);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);

    return () => {
      audio.removeEventListener('timeupdate', updateTime);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
    };
  }, []);

  const togglePlayPause = useCallback(() => {
    try {
      if (!audioRef.current) return;

      if (isPlaying) {
        audioRef.current.pause();
        setIsPlaying(false);
      } else {
        audioRef.current.play();
        setIsPlaying(true);
      }
    } catch (error) {
      console.error('Error toggling play/pause:', error);
      setError(`Play/Pause error: ${error}`);
    }
  }, [isPlaying]);

  const handleSeek = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    try {
      if (!audioRef.current || !progressRef.current) return;

      const rect = progressRef.current.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const percentage = clickX / rect.width;
      const newTime = percentage * duration;
      
      audioRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    } catch (error) {
      console.error('Error seeking:', error);
      setError(`Seek error: ${error}`);
    }
  }, [duration]);

  const handleVolumeChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    try {
      const newVolume = parseFloat(e.target.value);
      setVolume(newVolume);
      if (audioRef.current) {
        audioRef.current.volume = newVolume;
      }
    } catch (error) {
      console.error('Error changing volume:', error);
      setError(`Volume error: ${error}`);
    }
  }, []);

  const formatTime = useCallback((time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }, []);

  const pinStartTime = useCallback(() => {
    try {
      setStartTime(currentTime);
      setError(null);
    } catch (error) {
      console.error('Error pinning start time:', error);
      setError(`Error pinning start time: ${error}`);
    }
  }, [currentTime]);

  const pinEndTime = useCallback(() => {
    try {
      setEndTime(currentTime);
      setError(null);
    } catch (error) {
      console.error('Error pinning end time:', error);
      setError(`Error pinning end time: ${error}`);
    }
  }, [currentTime]);

  const createRingtone = useCallback(async () => {
    try {
      if (startTime >= endTime) {
        throw new Error('Start time must be before end time');
      }

      if (endTime - startTime < 1) {
        throw new Error('Ringtone must be at least 1 second long');
      }

      // Removed 30-second limit - ringtones can now be any length

      setIsCreatingRingtone(true);
      setError(null);

      // Create AudioContext if not exists
      if (!audioContextRef.current) {
        audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
      }

      const audioContext = audioContextRef.current;
      
      // Fetch the audio file
      const response = await fetch(audioFile.url);
      const arrayBuffer = await response.arrayBuffer();
      
      // Decode the audio data
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      
      // Calculate the sample positions
      const sampleRate = audioBuffer.sampleRate;
      const startSample = Math.floor(startTime * sampleRate);
      const endSample = Math.floor(endTime * sampleRate);
      const segmentLength = endSample - startSample;
      
      // Create a new audio buffer for the segment
      const segmentBuffer = audioContext.createBuffer(
        audioBuffer.numberOfChannels,
        segmentLength,
        sampleRate
      );
      
      // Copy the audio data for each channel
      for (let channel = 0; channel < audioBuffer.numberOfChannels; channel++) {
        const channelData = audioBuffer.getChannelData(channel);
        const segmentData = segmentBuffer.getChannelData(channel);
        
        for (let i = 0; i < segmentLength; i++) {
          segmentData[i] = channelData[startSample + i];
        }
      }
      
      // Convert the audio buffer to a blob
      const offlineContext = new OfflineAudioContext(
        segmentBuffer.numberOfChannels,
        segmentBuffer.length,
        segmentBuffer.sampleRate
      );
      
      const source = offlineContext.createBufferSource();
      source.buffer = segmentBuffer;
      source.connect(offlineContext.destination);
      source.start();
      
      const renderedBuffer = await offlineContext.startRendering();
      
      // Convert to WAV format (MP3 encoding is not supported in browsers)
      const wavBlob = audioBufferToWav(renderedBuffer);
      const ringtoneFile = new File([wavBlob], `ringtone_${Date.now()}.wav`, { type: 'audio/wav' });
      const ringtoneUrl = URL.createObjectURL(wavBlob);

      const ringtone: AudioFile = {
        id: Date.now().toString(),
        name: `Ringtone_${audioFile.name}`,
        url: ringtoneUrl,
        duration: endTime - startTime,
        file: ringtoneFile,
        type: 'ringtone',
        startTime,
        endTime
      };

      onRingtoneCreated(ringtone);
      
             // Save ringtone to backend
       try {
         console.log('🔄 Sending ringtone to backend...');
         const saveResult = await ringtoneService.saveRingtone(ringtone);
         console.log('📥 Received response from backend:', saveResult);
         console.log('📥 Response type:', typeof saveResult);
         console.log('📥 Response keys:', Object.keys(saveResult));
         
         if (saveResult.success) {
           console.log('🎵 SUCCESS: Ringtone created and saved to backend successfully!');
           console.log('📁 Filename:', saveResult.filename);
           console.log('📁 File path:', saveResult.file_path);
           console.log('📁 Format:', saveResult.format);
           console.log('📁 Folder:', saveResult.folder);
           
           if (saveResult.mp3_available) {
             console.log('🎵 MP3 version also available!');
             console.log('📁 MP3 filename:', saveResult.mp3_filename);
             console.log('📁 MP3 path:', saveResult.mp3_path);
           }
           
           // Show success message to user
           setError(null);
           
           let successMessage = `🎵 SUCCESS: Ringtone created successfully!\n\n📁 ${saveResult.format?.toUpperCase()} format saved to: ${saveResult.folder}\n📁 ${saveResult.format?.toUpperCase()} filename: ${saveResult.filename}`;
           
           if (saveResult.mp3_available) {
             successMessage += `\n\n🎵 MP3 format also created successfully!\n📁 MP3 saved to: mp3_ringtones\n📁 MP3 filename: ${saveResult.mp3_filename}\n\n✅ Both WAV and MP3 formats are now available!`;
           } else {
             successMessage += `\n\n⚠️ MP3 version creation failed or skipped\n💡 Only ${saveResult.format?.toUpperCase()} format was created`;
           }
           
           setSuccessMessage(successMessage);
          
          // Auto-hide success message after 10 seconds
          setTimeout(() => {
            setSuccessMessage(null);
          }, 10000);
        } else {
          console.error('Failed to save ringtone to backend:', saveResult.error);
          setError(`Ringtone created but failed to save to backend: ${saveResult.error}`);
        }
      } catch (saveError) {
        console.error('Error saving ringtone to backend:', saveError);
        setError(`Ringtone created but failed to save to backend: ${saveError}`);
      }
      
      setError(null);
    } catch (error) {
      console.error('Error creating ringtone:', error);
      setError(`Error creating ringtone: ${error}`);
    } finally {
      setIsCreatingRingtone(false);
    }
  }, [startTime, endTime, audioFile, onRingtoneCreated]);

  // Helper function to convert AudioBuffer to WAV format
  const audioBufferToWav = (buffer: AudioBuffer): Blob => {
    const numChannels = buffer.numberOfChannels;
    const sampleRate = buffer.sampleRate;
    const length = buffer.length;
    
    // WAV file header
    const arrayBuffer = new ArrayBuffer(44 + length * numChannels * 2);
    const view = new DataView(arrayBuffer);
    
    // RIFF chunk descriptor
    const writeString = (offset: number, string: string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };
    
    writeString(0, 'RIFF');
    view.setUint32(4, 36 + length * numChannels * 2, true);
    writeString(8, 'WAVE');
    
    // fmt sub-chunk
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * numChannels * 2, true);
    view.setUint16(32, numChannels * 2, true);
    view.setUint16(34, 16, true);
    
    // data sub-chunk
    writeString(36, 'data');
    view.setUint32(40, length * numChannels * 2, true);
    
    // Write audio data
    let offset = 44;
    for (let i = 0; i < length; i++) {
      for (let channel = 0; channel < numChannels; channel++) {
        const sample = Math.max(-1, Math.min(1, buffer.getChannelData(channel)[i]));
        view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
        offset += 2;
      }
    }
    
    return new Blob([arrayBuffer], { type: 'audio/wav' });
  };

  return (
    <div className="audio-player">
      <div className="audio-info">
        <h3>{audioFile.name}</h3>
        <p>Duration: {formatTime(duration)}</p>
      </div>

      <audio ref={audioRef} src={audioFile.url} preload="metadata" />

      <div className="controls">
        <button 
          className={`play-button ${isPlaying ? 'playing' : ''}`}
          onClick={togglePlayPause}
        >
          {isPlaying ? '⏸️ Pause' : '▶️ Play'}
        </button>

        <div className="progress-container">
          <div 
            ref={progressRef}
            className="progress-bar"
            onClick={handleSeek}
          >
            <div 
              className="progress-fill"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            />
            <div 
              className="progress-handle"
              style={{ left: `${(currentTime / duration) * 100}%` }}
            />
          </div>
          <div className="time-display">
            {formatTime(currentTime)} / {formatTime(duration)}
          </div>
        </div>

        <div className="volume-control">
          <label>Volume:</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={handleVolumeChange}
          />
          <span>{Math.round(volume * 100)}%</span>
        </div>
      </div>

      <div className="ringtone-editor">
        <h4>Create Ringtone</h4>
        <div className="time-inputs">
          <div className="time-input">
            <label>Start Time:</label>
            <div className="time-controls">
              <input
                type="range"
                min="0"
                max={duration}
                step="0.1"
                value={startTime}
                onChange={(e) => setStartTime(parseFloat(e.target.value))}
              />
              <span>{formatTime(startTime)}</span>
              <button 
                className="pin-time-btn"
                onClick={pinStartTime}
                title="Pin current playing time as start time"
              >
                📌 Pin Current Time
              </button>
            </div>
          </div>
          
          <div className="time-input">
            <label>End Time:</label>
            <div className="time-controls">
              <input
                type="range"
                min="0"
                max={duration}
                step="0.1"
                value={endTime}
                onChange={(e) => setEndTime(parseFloat(e.target.value))}
              />
              <span>{formatTime(endTime)}</span>
              <button 
                className="pin-time-btn"
                onClick={pinEndTime}
                title="Pin current playing time as end time"
              >
                📌 Pin Current Time
              </button>
            </div>
          </div>
        </div>
        
        <div className="ringtone-preview">
          <p>Ringtone Length: {formatTime(endTime - startTime)}</p>
        </div>
        
        <button 
          className="create-ringtone-btn"
          onClick={createRingtone}
          disabled={startTime >= endTime || isCreatingRingtone}
        >
          {isCreatingRingtone ? '⏳ Creating...' : '✂️ Create Ringtone'}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}
      
      {successMessage && (
        <div className="success-message">
          <p style={{ whiteSpace: 'pre-line' }}>{successMessage}</p>
          <button onClick={() => setSuccessMessage(null)}>Dismiss</button>
        </div>
      )}
    </div>
  );
};

export default AudioPlayer;
