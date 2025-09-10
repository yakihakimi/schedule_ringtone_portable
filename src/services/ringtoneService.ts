// Rules applied
import { AudioFile } from '../types/audio';

// Rules applied
// Dynamic API URL based on current host
const getApiBaseUrl = (): string => {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  const port = '5000'; // Backend port
  
  // If accessing via localhost, use localhost for API
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `${protocol}//${hostname}:${port}/api`;
  }
  
  // For network access, use the same hostname but port 5000
  return `${protocol}//${hostname}:${port}/api`;
};

export const API_BASE_URL = getApiBaseUrl();

export interface RingtoneInfo {
  id: string;
  name: string;
  size: number;
  created: string;
  modified: string;
  file_path: string;
  original_name?: string;
  start_time?: number;
  end_time?: number;
  duration?: number;
  has_metadata: boolean;
  mp3_filename?: string;
  mp3_available?: boolean;
  format?: string;
  folder?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  error?: string;
  data?: T;
  ringtones?: T;  // For listRingtones endpoint
  count?: number;  // For listRingtones endpoint
}

class RingtoneService {
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  async saveRingtone(audioFile: AudioFile): Promise<{ 
    success: boolean;
    message: string;
    filename: string; 
    file_path: string; 
    size: number; 
    created: string; 
    metadata: any;
    mp3_available: boolean;
    format: string;
    folder: string;
    mp3_filename?: string;
    mp3_path?: string;
    error?: string;
  }> {
    try {
      // Convert the audio file to a blob if it's not already
      let fileToUpload: File;
      
      if (audioFile.file instanceof File) {
        fileToUpload = audioFile.file;
      } else {
        // If we have a URL, fetch it and create a file
        const response = await fetch(audioFile.url);
        const blob = await response.blob();
        fileToUpload = new File([blob], audioFile.name, { type: blob.type });
      }

      const formData = new FormData();
      formData.append('file', fileToUpload);
      
      // Add metadata
      formData.append('original_name', audioFile.name.replace('Ringtone_', ''));
      formData.append('start_time', (audioFile.startTime || 0).toString());
      formData.append('end_time', (audioFile.endTime || 0).toString());
      formData.append('duration', audioFile.duration.toString());

      const response = await fetch(`${API_BASE_URL}/ringtones`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error saving ringtone:', error);
      return {
        success: false,
        message: 'Failed to save ringtone',
        filename: '',
        file_path: '',
        size: 0,
        created: '',
        metadata: {},
        mp3_available: false,
        format: '',
        folder: '',
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  async listRingtones(): Promise<ApiResponse<RingtoneInfo[]>> {
    return this.makeRequest<RingtoneInfo[]>('/ringtones');
  }

  async downloadRingtone(filename: string, folder?: string): Promise<void> {
    try {
      let endpoint = `/ringtones/${filename}`;
      
      // If folder is provided, use the new folder-based endpoint
      if (folder) {
        endpoint = `/ringtones/${folder}/${filename}`;
      }
      
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading ringtone:', error);
      throw error;
    }
  }

  async deleteRingtone(filename: string, folder?: string): Promise<ApiResponse<{ filename: string; folder?: string }>> {
    let endpoint = `/ringtones/${filename}`;
    
    // If folder is provided, use the new folder-based endpoint
    if (folder) {
      endpoint = `/ringtones/${folder}/${filename}`;
    }
    
    return this.makeRequest<{ filename: string; folder?: string }>(endpoint, {
      method: 'DELETE',
    });
  }

  async uploadAudioFile(file: File): Promise<ApiResponse<{ filename: string; file_path: string; size: number; uploaded: string }>> {
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error uploading audio file:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  }

  async checkServerHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`);
      return response.ok;
    } catch (error) {
      console.error('Server health check failed:', error);
      return false;
    }
  }
}

export const ringtoneService = new RingtoneService();
export default ringtoneService;
