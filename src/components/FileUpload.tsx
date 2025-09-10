// Rules applied
import React, { useRef, useState, useCallback } from 'react';
import { AudioFile } from '../types/audio';

interface FileUploadProps {
  onFileUpload: (file: AudioFile) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback(async (file: File) => {
    try {
      if (!file.type.startsWith('audio/')) {
        throw new Error('Please select an audio file (MP3, WAV, etc.)');
      }

      if (file.size > 100 * 1024 * 1024) { // 100MB limit
        throw new Error('File size too large. Please select a file under 100MB');
      }

      const url = URL.createObjectURL(file);
      
      // Get audio duration
      const audio = new Audio();
      audio.src = url;
      
      const duration = await new Promise<number>((resolve) => {
        audio.addEventListener('loadedmetadata', () => {
          resolve(audio.duration);
        });
        audio.addEventListener('error', () => {
          resolve(0);
        });
      });

      const audioFile: AudioFile = {
        id: Date.now().toString(),
        name: file.name,
        url,
        duration,
        file,
        type: 'original'
      };

      onFileUpload(audioFile);
      setError(null);
    } catch (error) {
      console.error('Error processing file:', error);
      setError(error instanceof Error ? error.message : 'Error processing file');
    }
  }, [onFileUpload]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFile(files[0]);
    }
  }, [handleFile]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFile(files[0]);
    }
  }, [handleFile]);

  const handleClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return (
    <div className="file-upload">
      <div
        className={`upload-area ${isDragOver ? 'drag-over' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <div className="upload-content">
          <div className="upload-icon">📁</div>
          <h3>Drag & Drop MP3 Files Here</h3>
          <p>or click to browse files</p>
          <p className="file-types">Supported: MP3, WAV, OGG</p>
        </div>
      </div>
      
      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*"
        onChange={handleFileSelect}
        style={{ display: 'none' }}
      />
      
      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;
