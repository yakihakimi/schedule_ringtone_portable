// Rules applied
import React, { useState, useRef, useEffect } from 'react';
import { AudioFile } from '../types/audio';
import ringtoneService, { RingtoneInfo, API_BASE_URL } from '../services/ringtoneService';

interface RingtoneListProps {
  ringtones: AudioFile[];
  onRingtonesUpdated?: () => void;
  onEditRingtone?: (ringtone: AudioFile) => void; // Add edit callback prop
  onDeleteLocalRingtone?: (id: string) => void; // Add delete callback prop for local ringtones
}

const RingtoneList: React.FC<RingtoneListProps> = ({ ringtones, onRingtonesUpdated, onEditRingtone, onDeleteLocalRingtone }) => {
  const [playingId, setPlayingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendRingtones, setBackendRingtones] = useState<RingtoneInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const audioRefs = useRef<{ [key: string]: HTMLAudioElement }>({});

  // Load ringtones from backend
  useEffect(() => {
    console.log('🔄 RingtoneList: Loading backend ringtones...');
    loadBackendRingtones();
  }, []);

  const loadBackendRingtones = async () => {
    try {
      console.log('🔄 RingtoneList: Starting to load backend ringtones...');
      setIsLoading(true);
      setError(null);
      
      const result = await ringtoneService.listRingtones();
      console.log('🔄 RingtoneList: Backend response:', result);
      
      if (result.success && result.ringtones) {
        setBackendRingtones(result.ringtones);
        console.log('✅ RingtoneList: Successfully loaded backend ringtones:', result.ringtones);
        console.log('✅ RingtoneList: Count:', result.ringtones.length);
      } else {
        console.warn('⚠️ RingtoneList: Backend response indicates failure:', result);
        setBackendRingtones([]);
        if (result.error) {
          setError(`Failed to load ringtones: ${result.error}`);
        }
      }
    } catch (error) {
      console.error('❌ RingtoneList: Error loading ringtones from backend:', error);
      setError(`Error loading ringtones: ${error}`);
      setBackendRingtones([]);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to sort ringtones by creation time (newest first)
  const sortRingtonesByTime = (ringtones: RingtoneInfo[]) => {
    return ringtones.sort((a, b) => {
      const timeA = new Date(a.created).getTime();
      const timeB = new Date(b.created).getTime();
      return timeB - timeA; // Descending order (newest first)
    });
  };

  // Helper function to group ringtones by format
  const groupRingtonesByFormat = (ringtones: RingtoneInfo[]) => {
    const grouped = {
      mp3: [] as RingtoneInfo[],
      wav: [] as RingtoneInfo[]
    };

    ringtones.forEach(ringtone => {
      if (ringtone.format === 'mp3') {
        grouped.mp3.push(ringtone);
      } else if (ringtone.format === 'wav') {
        grouped.wav.push(ringtone);
      }
    });

    // Sort each group by time
    grouped.mp3 = sortRingtonesByTime(grouped.mp3);
    grouped.wav = sortRingtonesByTime(grouped.wav);

    return grouped;
  };

  // Helper function to convert RingtoneInfo to AudioFile format
  const convertToAudioFile = (ringtone: RingtoneInfo): AudioFile => {
    return {
      id: ringtone.id,
      name: ringtone.original_name || ringtone.name,
      url: `${API_BASE_URL}/ringtones/${ringtone.folder || 'wav_ringtones'}/${ringtone.name}`,
      duration: ringtone.duration || 0,
      file: null as any, // We don't have the actual file object
      type: 'ringtone' as const,
      startTime: ringtone.start_time,
      endTime: ringtone.end_time,
      filePath: ringtone.file_path // Include the file path from backend
    };
  };

  // Helper function to filter ringtones based on search query
  const filterRingtones = (ringtones: RingtoneInfo[], query: string): RingtoneInfo[] => {
    if (!query.trim()) {
      return ringtones;
    }
    
    const lowercaseQuery = query.toLowerCase().trim();
    return ringtones.filter(ringtone => {
      const name = (ringtone.original_name || ringtone.name).toLowerCase();
      return name.includes(lowercaseQuery);
    });
  };

  // Helper function to filter local ringtones based on search query
  const filterLocalRingtones = (ringtones: AudioFile[], query: string): AudioFile[] => {
    if (!query.trim()) {
      return ringtones;
    }
    
    const lowercaseQuery = query.toLowerCase().trim();
    return ringtones.filter(ringtone => {
      const name = ringtone.name.toLowerCase();
      return name.includes(lowercaseQuery);
    });
  };

  const handlePlay = (ringtone: AudioFile) => {
    try {
      // Stop any currently playing audio
      if (playingId && audioRefs.current[playingId]) {
        audioRefs.current[playingId].pause();
        audioRefs.current[playingId].currentTime = 0;
      }

      // Play the selected ringtone
      const audio = audioRefs.current[ringtone.id];
      if (audio) {
        audio.play();
        setPlayingId(ringtone.id);
        
        // Reset when audio ends
        audio.onended = () => {
          setPlayingId(null);
        };
      }
    } catch (error) {
      console.error('Error playing ringtone:', error);
      setError(`Error playing ringtone: ${error}`);
    }
  };

  const handleStop = (ringtone: AudioFile) => {
    try {
      const audio = audioRefs.current[ringtone.id];
      if (audio) {
        audio.pause();
        audio.currentTime = 0;
        setPlayingId(null);
      }
    } catch (error) {
      console.error('Error stopping ringtone:', error);
      setError(`Error stopping ringtone: ${error}`);
    }
  };

  const handleDownload = async (ringtone: AudioFile) => {
    try {
      // Try to download from backend first
      const backendRingtone = backendRingtones.find(br => br.name === ringtone.name);
      if (backendRingtone) {
        await ringtoneService.downloadRingtone(backendRingtone.name, backendRingtone.folder);
        return;
      }
      
      // Fallback to local download
      const link = document.createElement('a');
      link.href = ringtone.url;
      link.download = ringtone.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error downloading ringtone:', error);
      setError(`Error downloading ringtone: ${error}`);
    }
  };

  const handleEdit = (ringtone: AudioFile) => {
    try {
      console.log('🔄 Editing ringtone:', ringtone.name);
      if (onEditRingtone) {
        onEditRingtone(ringtone);
      }
    } catch (error) {
      console.error('Error editing ringtone:', error);
      setError(`Error editing ringtone: ${error}`);
    }
  };

  const handleDelete = async (ringtone: RingtoneInfo) => {
    try {
      const result = await ringtoneService.deleteRingtone(ringtone.name, ringtone.folder);
      if (result.success) {
        console.log('Ringtone deleted successfully:', ringtone.name);
        await loadBackendRingtones(); // Reload the list
        if (onRingtonesUpdated) {
          onRingtonesUpdated();
        }
      } else {
        setError(`Failed to delete ringtone: ${result.error}`);
      }
    } catch (error) {
      console.error('Error deleting ringtone:', error);
      setError(`Error deleting ringtone: ${error}`);
    }
  };

  const handleDeleteLocal = (ringtone: AudioFile) => {
    try {
      console.log('🗑️ Deleting local ringtone:', ringtone.name);
      if (onDeleteLocalRingtone) {
        onDeleteLocalRingtone(ringtone.id);
      }
    } catch (error) {
      console.error('Error deleting local ringtone:', error);
      setError(`Error deleting local ringtone: ${error}`);
    }
  };

  // Render a single ringtone item
  const renderRingtoneItem = (ringtone: RingtoneInfo | AudioFile, isLocal: boolean = false) => {
    const isLocalRingtone = isLocal;
    const ringtoneData = isLocalRingtone ? ringtone as AudioFile : ringtone as RingtoneInfo;
    
    return (
      <div key={ringtoneData.id} className={`ringtone-item ${isLocalRingtone ? 'local' : 'saved'}`}>
        <div className="ringtone-info">
          <h4>{ringtoneData.name}</h4>
          <p>Duration: {Math.floor(ringtoneData.duration || 0)}s</p>
          {isLocalRingtone && (ringtoneData as AudioFile).startTime !== undefined && (ringtoneData as AudioFile).endTime !== undefined && (
            <p>From: {Math.floor((ringtoneData as AudioFile).startTime!)}s - To: {Math.floor((ringtoneData as AudioFile).endTime!)}s</p>
          )}
          {!isLocalRingtone && (ringtoneData as RingtoneInfo).start_time !== undefined && (ringtoneData as RingtoneInfo).end_time !== undefined && (
            <p>From: {Math.floor((ringtoneData as RingtoneInfo).start_time!)}s - To: {Math.floor((ringtoneData as RingtoneInfo).end_time!)}s</p>
          )}
          {!isLocalRingtone && (ringtoneData as RingtoneInfo).format && (
            <p>Format: {(ringtoneData as RingtoneInfo).format?.toUpperCase()}</p>
          )}
        </div>
        
        <div className="ringtone-controls">
          {playingId === ringtoneData.id ? (
            <button 
              className="stop-button"
              onClick={() => handleStop(ringtoneData as AudioFile)}
            >
              ⏹️ Stop
            </button>
          ) : (
            <button 
              className="play-button"
              onClick={() => handlePlay(ringtoneData as AudioFile)}
            >
              ▶️ Play
            </button>
          )}
          
          <button 
            className="edit-button"
            onClick={() => handleEdit(isLocalRingtone ? ringtoneData as AudioFile : convertToAudioFile(ringtoneData as RingtoneInfo))}
            title="Edit this ringtone"
          >
            ✏️ Edit
          </button>
          
          <button 
            className="download-button"
            onClick={() => handleDownload(ringtoneData as AudioFile)}
          >
            💾 Download
          </button>

          {isLocalRingtone ? (
            <button 
              className="delete-button"
              onClick={() => handleDeleteLocal(ringtoneData as AudioFile)}
              title="Delete this ringtone"
            >
              🗑️ Delete
            </button>
          ) : (
            <button 
              className="delete-button"
              onClick={() => handleDelete(ringtoneData as RingtoneInfo)}
              title="Delete this ringtone"
            >
              🗑️ Delete
            </button>
          )}
        </div>
        
        <audio
          ref={(el) => {
            if (el) audioRefs.current[ringtoneData.id] = el;
          }}
          src={isLocalRingtone ? (ringtoneData as AudioFile).url : `${API_BASE_URL}/ringtones/${(ringtoneData as RingtoneInfo).folder || 'wav_ringtones'}/${(ringtoneData as RingtoneInfo).name}`}
          preload="metadata"
        />
      </div>
    );
  };

  // Check if we have any ringtones to display
  const hasAnyRingtones = ringtones.length > 0 || backendRingtones.length > 0;
  
  // Group and sort backend ringtones by format
  const groupedBackendRingtones = groupRingtonesByFormat(backendRingtones);
  
  // Filter ringtones based on search query
  const filteredMp3Ringtones = filterRingtones(groupedBackendRingtones.mp3, searchQuery);
  const filteredWavRingtones = filterRingtones(groupedBackendRingtones.wav, searchQuery);
  const filteredLocalRingtones = filterLocalRingtones(ringtones, searchQuery);
  
  // Check if we have search results
  const hasSearchResults = filteredMp3Ringtones.length > 0 || filteredWavRingtones.length > 0 || filteredLocalRingtones.length > 0;

  if (!hasAnyRingtones && !isLoading) {
    return (
      <div className="ringtone-list empty">
        <h2>📱 Your Ringtones</h2>
        <p>No ringtones created yet. Upload an audio file and create your first ringtone!</p>
        <button 
          className="refresh-button"
          onClick={loadBackendRingtones}
          disabled={isLoading}
        >
          🔄 Refresh Ringtones
        </button>
      </div>
    );
  }

  // Show no search results message if searching but no results found
  if (searchQuery && !hasSearchResults && !isLoading) {
    return (
      <div className="ringtone-list">
        <h2>📱 Your Ringtones</h2>
        
        {/* Search Bar */}
        <div className="search-section">
          <div className="search-input-container">
            <input
              type="text"
              placeholder="🔍 Search ringtones..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            {searchQuery && (
              <button
                className="clear-search-button"
                onClick={() => setSearchQuery('')}
                title="Clear search"
              >
                ✕
              </button>
            )}
          </div>
          <p className="search-info">
            Showing results for "{searchQuery}"
          </p>
        </div>
        
        <div className="no-results">
          <p>🔍 No ringtones found matching "{searchQuery}"</p>
          <button 
            className="clear-search-button"
            onClick={() => setSearchQuery('')}
          >
            Clear Search
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="ringtone-list">
      <h2>📱 Your Ringtones</h2>
      
      {/* Search Bar */}
      <div className="search-section">
        <div className="search-input-container">
          <input
            type="text"
            placeholder="🔍 Search ringtones..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          {searchQuery && (
            <button
              className="clear-search-button"
              onClick={() => setSearchQuery('')}
              title="Clear search"
            >
              ✕
            </button>
          )}
        </div>
        {searchQuery && (
          <p className="search-info">
            Showing results for "{searchQuery}"
          </p>
        )}
      </div>
      
      {/* MP3 Ringtones Section */}
      {filteredMp3Ringtones.length > 0 && (
        <div className="ringtone-section">
          <h3>🎵 MP3 Ringtones ({filteredMp3Ringtones.length})</h3>
          {filteredMp3Ringtones.map((ringtone) => renderRingtoneItem(ringtone, false))}
        </div>
      )}

      {/* WAV Ringtones Section */}
      {filteredWavRingtones.length > 0 && (
        <div className="ringtone-section">
          <h3>🎶 WAV Ringtones ({filteredWavRingtones.length})</h3>
          {filteredWavRingtones.map((ringtone) => renderRingtoneItem(ringtone, false))}
        </div>
      )}

      {/* All Created Ringtones */}
      {filteredLocalRingtones.length > 0 && (
        <div className="ringtone-section">
          <h3>🆕 All Created Ringtones ({filteredLocalRingtones.length})</h3>
          {filteredLocalRingtones.map((ringtone) => renderRingtoneItem(ringtone, true))}
        </div>
      )}
      
      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      <div className="refresh-section">
        <button 
          className="refresh-button"
          onClick={loadBackendRingtones}
          disabled={isLoading}
        >
          🔄 Refresh Ringtones
        </button>
        <p className="refresh-info">Click to refresh the list of saved ringtones from the backend</p>
      </div>
    </div>
  );
};

export default RingtoneList;
