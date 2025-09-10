// Rules applied
import React, { useState, useEffect } from 'react';
import './App.css';
import AudioPlayer from './components/AudioPlayer';
import FileUpload from './components/FileUpload';
import RingtoneList from './components/RingtoneList';
import ScheduleRingtone from './components/ScheduleRingtone';
import { AudioFile } from './types/audio';
import ringtoneService, { API_BASE_URL } from './services/ringtoneService';

type MainTabType = 'creator' | 'ringtones' | 'schedule';

function App() {
  const [selectedFile, setSelectedFile] = useState<AudioFile | null>(null);
  const [ringtones, setRingtones] = useState<AudioFile[]>([]);
  const [activeMainTab, setActiveMainTab] = useState<MainTabType>('creator');

  // Load existing ringtones from backend on startup
  useEffect(() => {
    loadExistingRingtones();
  }, []);

  const loadExistingRingtones = async () => {
    try {
      console.log('🔄 Loading existing ringtones from backend...');
      const result = await ringtoneService.listRingtones();
      console.log('Backend response:', result);
      
      if (result.success && result.ringtones) {
        console.log('🔍 Raw ringtones from backend:', result.ringtones);
        console.log('🔍 First ringtone has_metadata:', result.ringtones[0]?.has_metadata);
        console.log('🔍 First ringtone has_metadata type:', typeof result.ringtones[0]?.has_metadata);
        
        // Convert backend ringtones to AudioFile format
        const existingRingtones: AudioFile[] = result.ringtones
          .map(ringtone => ({
            id: ringtone.id,
            name: ringtone.original_name || ringtone.name,
            url: `${API_BASE_URL}/ringtones/${ringtone.folder}/${ringtone.name}`,
            duration: ringtone.duration || 0,
            file: null as any, // We don't have the actual file object
            type: 'ringtone' as const,
            startTime: ringtone.start_time,
            endTime: ringtone.end_time,
            filePath: ringtone.file_path // Include the file path from backend
          }));
        
        setRingtones(existingRingtones);
        console.log(`✅ Loaded ${existingRingtones.length} existing ringtones from backend:`, existingRingtones);
      } else {
        console.warn('⚠️ Backend response indicates failure or no data:', result);
        setRingtones([]);
      }
    } catch (error) {
      console.error('❌ Error loading existing ringtones:', error);
      setRingtones([]);
    }
  };

  const handleFileUpload = (file: AudioFile) => {
    try {
      setSelectedFile(file);
      console.log('File uploaded successfully:', file.name);
    } catch (error) {
      console.error('Error uploading file:', error);
      alert(`Error uploading file: ${error}`);
    }
  };

  const handleRingtoneCreated = async (ringtone: AudioFile) => {
    try {
      console.log('🎵 Ringtone created, updating UI...');
      
      // Add to local state immediately for instant feedback
      setRingtones(prev => [...prev, ringtone]);
      
      // Wait a moment for backend to process, then refresh from backend
      setTimeout(async () => {
        try {
          console.log('🔄 Refreshing ringtone list from backend...');
          await loadExistingRingtones();
        } catch (error) {
          console.error('❌ Error refreshing ringtone list:', error);
        }
      }, 1500); // Increased delay to ensure backend processing is complete
      
      console.log('✅ Ringtone created successfully:', ringtone.name);
    } catch (error) {
      console.error('❌ Error creating ringtone:', error);
      alert(`Error creating ringtone: ${error}`);
    }
  };

  const handleEditRingtone = (ringtone: AudioFile) => {
    try {
      console.log('🔄 Editing ringtone:', ringtone.name);
      
      // Switch to creator tab
      setActiveMainTab('creator');
      
      // Set the ringtone as the selected file for editing
      setSelectedFile(ringtone);
      
      console.log('✅ Switched to creator tab with ringtone for editing');
    } catch (error) {
      console.error('❌ Error editing ringtone:', error);
      alert(`Error editing ringtone: ${error}`);
    }
  };

  const handleDeleteLocalRingtone = (ringtoneId: string) => {
    try {
      console.log('🗑️ Deleting local ringtone:', ringtoneId);
      setRingtones(prev => prev.filter(ringtone => ringtone.id !== ringtoneId));
      console.log('✅ Local ringtone deleted successfully');
    } catch (error) {
      console.error('❌ Error deleting local ringtone:', error);
      alert(`Error deleting local ringtone: ${error}`);
    }
  };

  const renderTabContent = () => {
    if (activeMainTab === 'creator') {
      return (
        <div className="creator-tab-content">
          <div className="upload-section">
            <FileUpload onFileUpload={handleFileUpload} />
          </div>
          
          {selectedFile && (
            <div className="player-section">
              <h2>Audio Editor</h2>
              <AudioPlayer 
                audioFile={selectedFile} 
                onRingtoneCreated={handleRingtoneCreated}
              />
            </div>
          )}
        </div>
      );
    } else if (activeMainTab === 'ringtones') {
      return (
        <div className="ringtones-tab-content">
          <RingtoneList 
            ringtones={ringtones} 
            onRingtonesUpdated={() => {
              console.log('Ringtones updated from backend');
              loadExistingRingtones(); // Refresh the list
            }}
            onEditRingtone={handleEditRingtone} // Pass the edit callback
            onDeleteLocalRingtone={handleDeleteLocalRingtone} // Pass the delete callback
          />
        </div>
      );
    } else {
      return (
        <div className="schedule-tab-content">
          <ScheduleRingtone 
            ringtones={ringtones}
          />
        </div>
      );
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎵 Ringtone Creator</h1>
        <p>Upload MP3 files and create custom ringtones</p>
      </header>
      
      {/* Main Tab Navigation */}
      <div className="main-tab-navigation">
        <button 
          className={`main-tab-button ${activeMainTab === 'creator' ? 'active' : ''}`}
          onClick={() => setActiveMainTab('creator')}
        >
          🎵 Ringtone Creator
        </button>
        <button 
          className={`main-tab-button ${activeMainTab === 'ringtones' ? 'active' : ''}`}
          onClick={() => setActiveMainTab('ringtones')}
        >
          📱 Existing Ringtones ({ringtones.length})
        </button>
        <button 
          className={`main-tab-button ${activeMainTab === 'schedule' ? 'active' : ''}`}
          onClick={() => setActiveMainTab('schedule')}
        >
          ⏰ Schedule Ringtone
        </button>

      </div>
      
      <main className="App-main">
        {renderTabContent()}
      </main>
    </div>
  );
}

export default App;
