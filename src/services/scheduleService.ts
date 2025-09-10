// Rules applied
import { ScheduledRingtone, ScheduleFormData } from '../types/schedule';
import { AudioFile } from '../types/audio';
import { ringtoneService } from './ringtoneService';

// Rules applied
// Dynamic API URL based on current host
const getApiBaseUrl = (): string => {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  const port = '5000'; // Backend port
  
  // If accessing via localhost, use localhost for API
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `${protocol}//${hostname}:${port}`;
  }
  
  // For network access, use the same hostname but port 5000
  return `${protocol}//${hostname}:${port}`;
};

const API_BASE_URL = getApiBaseUrl();

// Rules applied
// Use a shared storage key that works across different origins
// This allows schedule data to be shared between localhost and network access
const STORAGE_KEY = 'ringtone-scheduler-schedules';

export class ScheduleService {
  private static instance: ScheduleService;
  private scheduledRingtones: ScheduledRingtone[] = [];
  private checkInterval: NodeJS.Timeout | null = null;
  private audioElement: HTMLAudioElement | null = null;

  private constructor() {
    this.initializeService();
  }

  private async initializeService(): Promise<void> {
    await this.loadFromStorage();
    this.startScheduleChecker();
  }

  public static getInstance(): ScheduleService {
    if (!ScheduleService.instance) {
      ScheduleService.instance = new ScheduleService();
    }
    return ScheduleService.instance;
  }

  // Load scheduled ringtones from localStorage and sync with backend
  private async loadFromStorage(): Promise<void> {
    try {
      // First, try to load from backend (for cross-origin sync)
      await this.loadFromBackend();
      
      // Fallback to localStorage if backend fails
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored && this.scheduledRingtones.length === 0) {
        this.scheduledRingtones = JSON.parse(stored);
        console.log('📅 Loaded scheduled ringtones from localStorage fallback:', this.scheduledRingtones.length);
        
        // Sync localStorage data to backend
        await this.syncToBackend();
      }
    } catch (error) {
      console.error('❌ Error loading scheduled ringtones:', error);
      this.scheduledRingtones = [];
    }
  }

  // Load schedule data from backend
  private async loadFromBackend(): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/schedules`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success && result.schedules) {
          this.scheduledRingtones = result.schedules;
          console.log('📅 Loaded scheduled ringtones from backend:', this.scheduledRingtones.length);
          
          // Update localStorage with backend data
          localStorage.setItem(STORAGE_KEY, JSON.stringify(this.scheduledRingtones));
        }
      } else {
        console.warn('⚠️ Failed to load schedules from backend, using localStorage');
      }
    } catch (error) {
      console.warn('⚠️ Backend schedule loading failed, using localStorage:', error);
    }
  }

  // Sync current data to backend
  private async syncToBackend(): Promise<void> {
    try {
      for (const schedule of this.scheduledRingtones) {
        await this.saveScheduleToBackend(schedule);
      }
      console.log('🔄 Synced localStorage data to backend');
    } catch (error) {
      console.warn('⚠️ Failed to sync to backend:', error);
    }
  }

  // Save individual schedule to backend
  private async saveScheduleToBackend(schedule: ScheduledRingtone): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/schedules`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(schedule)
      });

      if (!response.ok) {
        console.warn('⚠️ Failed to save schedule to backend:', schedule.id);
      }
    } catch (error) {
      console.warn('⚠️ Error saving schedule to backend:', error);
    }
  }


  // Save scheduled ringtones to localStorage and backend
  private async saveToStorage(): Promise<void> {
    try {
      // Save to localStorage
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.scheduledRingtones));
      console.log('💾 Saved scheduled ringtones to localStorage');
      
      // Also save to backend for cross-origin sync
      await this.syncToBackend();
    } catch (error) {
      console.error('❌ Error saving scheduled ringtones:', error);
    }
  }

  // Create a new scheduled ringtone
  public async createSchedule(ringtone: AudioFile, formData: ScheduleFormData): Promise<ScheduledRingtone> {
    try {
      console.log('🚀 Starting schedule creation process...');
      console.log('📋 Schedule data:', { ringtone: ringtone.name, time: formData.time, days: formData.days });
      
      let ringtoneFilePath: string;
      
      // Check if this is a backend ringtone (already has a file path)
      if (ringtone.url.startsWith('http://localhost:5000/api/ringtones/')) {
        console.log('📁 This is a backend ringtone, using file path from backend...');
        
        if (ringtone.filePath) {
          // Use the file path provided by the backend
          ringtoneFilePath = ringtone.filePath;
          console.log('✅ Using file path from backend:', ringtoneFilePath);
        } else {
          // Fallback: extract the file path from the URL
          console.log('⚠️ No file path provided, extracting from URL...');
          const urlParts = ringtone.url.split('/');
          const folder = urlParts[urlParts.length - 2]; // e.g., 'wav_ringtones' or 'mp3_ringtones'
          const filename = urlParts[urlParts.length - 1]; // e.g., 'ringtone_20231201_120000_song.wav'
          
          // Prefer WAV format for scheduling (more reliable for Windows Task Scheduler)
          let preferredFolder = folder;
          let preferredFilename = filename;
          
          if (folder === 'mp3_ringtones') {
            // Try to find the corresponding WAV file
            const wavFilename = filename.replace('.mp3', '.wav');
            preferredFolder = 'wav_ringtones';
            preferredFilename = wavFilename;
            console.log('🔄 Preferring WAV format for scheduling:', preferredFilename);
          }
          
          // Construct the file path using the preferred format
          ringtoneFilePath = `portable_app/backend/ringtones/${preferredFolder}/${preferredFilename}`;
          console.log('✅ Extracted file path from backend URL (preferred format):', ringtoneFilePath);
        }
      } else {
        // This is a local ringtone, save it to get the file path
        console.log('💾 Saving local ringtone to get file path...');
        const saveResult = await ringtoneService.saveRingtone(ringtone);
        
        if (!saveResult.success) {
          throw new Error(`Failed to save ringtone: ${saveResult.error || 'Unknown error'}`);
        }
        
        ringtoneFilePath = saveResult.file_path;
        console.log('✅ Local ringtone saved successfully:', ringtoneFilePath);
      }
      
      const newSchedule: ScheduledRingtone = {
        id: `schedule_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        ringtoneId: ringtone.id,
        ringtoneName: ringtone.name,
        ringtoneUrl: ringtone.url,
        ringtoneFilePath: ringtoneFilePath, // Store the actual file path
        time: formData.time,
        days: formData.days,
        isActive: true,
        scheduleSource: formData.scheduleSource, // Store the scheduling method
        createdAt: new Date().toISOString(),
      };

      console.log('📝 Created schedule object:', newSchedule);

      // Create Windows Task Scheduler task only if schedule source is 'device'
      if (formData.scheduleSource === 'device') {
        console.log('🔄 Schedule source is device, checking Windows Task Scheduler availability...');
        const taskSchedulerAvailable = await this.isTaskSchedulerAvailable();
        if (taskSchedulerAvailable) {
          console.log('✅ Windows Task Scheduler is available, creating task...');
          try {
            await this.createWindowsTask(newSchedule);
            console.log('✅ Windows Task Scheduler task created successfully');
          } catch (taskError) {
            console.warn('⚠️ Failed to create Windows Task Scheduler task, but continuing with local schedule:', taskError);
          }
        } else {
          console.log('ℹ️ Windows Task Scheduler not available, creating local schedule only');
        }
      } else {
        console.log('ℹ️ Schedule source is web, creating browser-based schedule only');
      }

      this.scheduledRingtones.push(newSchedule);
      await this.saveToStorage();
      
      console.log('✅ Created new schedule with Windows Task:', newSchedule);
      return newSchedule;
    } catch (error) {
      console.error('❌ Error creating schedule:', error);
      throw error;
    }
  }

  // Get all scheduled ringtones
  public getAllSchedules(): ScheduledRingtone[] {
    return [...this.scheduledRingtones];
  }

  // Get active scheduled ringtones
  public getActiveSchedules(): ScheduledRingtone[] {
    return this.scheduledRingtones.filter(schedule => schedule.isActive);
  }

  // Update a scheduled ringtone
  public async updateSchedule(id: string, updates: Partial<ScheduledRingtone>): Promise<boolean> {
    try {
      const index = this.scheduledRingtones.findIndex(schedule => schedule.id === id);
      if (index === -1) {
        console.warn('⚠️ Schedule not found for update:', id);
        return false;
      }

      this.scheduledRingtones[index] = { ...this.scheduledRingtones[index], ...updates };
      await this.saveToStorage();
      
      console.log('✅ Updated schedule:', id);
      return true;
    } catch (error) {
      console.error('❌ Error updating schedule:', error);
      return false;
    }
  }

  // Update a scheduled ringtone with form data
  public async updateScheduleWithFormData(id: string, ringtone: AudioFile, formData: ScheduleFormData): Promise<boolean> {
    try {
      const index = this.scheduledRingtones.findIndex(schedule => schedule.id === id);
      if (index === -1) {
        console.warn('⚠️ Schedule not found for update:', id);
        return false;
      }

      const oldSchedule = this.scheduledRingtones[index];
      
      // Delete old Windows task
      await this.deleteWindowsTask(oldSchedule.id);
      
      let ringtoneFilePath: string;
      
      // Check if this is a backend ringtone (already has a file path)
      if (ringtone.url.startsWith('http://localhost:5000/api/ringtones/')) {
        console.log('📁 This is a backend ringtone, using file path from backend...');
        
        if (ringtone.filePath) {
          // Use the file path provided by the backend
          ringtoneFilePath = ringtone.filePath;
          console.log('✅ Using file path from backend:', ringtoneFilePath);
        } else {
          // Fallback: extract the file path from the URL
          console.log('⚠️ No file path provided, extracting from URL...');
          const urlParts = ringtone.url.split('/');
          const folder = urlParts[urlParts.length - 2]; // e.g., 'wav_ringtones' or 'mp3_ringtones'
          const filename = urlParts[urlParts.length - 1]; // e.g., 'ringtone_20231201_120000_song.wav'
          
          // Prefer WAV format for scheduling (more reliable for Windows Task Scheduler)
          let preferredFolder = folder;
          let preferredFilename = filename;
          
          if (folder === 'mp3_ringtones') {
            // Try to find the corresponding WAV file
            const wavFilename = filename.replace('.mp3', '.wav');
            preferredFolder = 'wav_ringtones';
            preferredFilename = wavFilename;
            console.log('🔄 Preferring WAV format for scheduling:', preferredFilename);
          }
          
          // Construct the file path using the preferred format
          ringtoneFilePath = `portable_app/backend/ringtones/${preferredFolder}/${preferredFilename}`;
          console.log('✅ Extracted file path from backend URL (preferred format):', ringtoneFilePath);
        }
      } else {
        // This is a local ringtone, save it to get the file path
        console.log('💾 Saving updated ringtone to get file path...');
        const saveResult = await ringtoneService.saveRingtone(ringtone);
        
        if (!saveResult.success) {
          throw new Error(`Failed to save updated ringtone: ${saveResult.error || 'Unknown error'}`);
        }
        
        ringtoneFilePath = saveResult.file_path;
        console.log('✅ Updated ringtone saved successfully:', ringtoneFilePath);
      }
      
      const updates: Partial<ScheduledRingtone> = {
        ringtoneId: ringtone.id,
        ringtoneName: ringtone.name,
        ringtoneUrl: ringtone.url,
        ringtoneFilePath: ringtoneFilePath, // Store the actual file path
        time: formData.time,
        days: formData.days,
        scheduleSource: formData.scheduleSource // Update the scheduling method
      };

      const updatedSchedule = { ...this.scheduledRingtones[index], ...updates };
      
      // Create new Windows task only if schedule source is 'device'
      if (formData.scheduleSource === 'device') {
        await this.createWindowsTask(updatedSchedule);
      }

      this.scheduledRingtones[index] = updatedSchedule;
      await this.saveToStorage();
      
      console.log('✅ Updated schedule with form data and Windows Task:', id);
      return true;
    } catch (error) {
      console.error('❌ Error updating schedule with form data:', error);
      return false;
    }
  }

  // Delete a scheduled ringtone
  public async deleteSchedule(id: string): Promise<boolean> {
    try {
      const index = this.scheduledRingtones.findIndex(schedule => schedule.id === id);
      if (index === -1) {
        console.warn('⚠️ Schedule not found for deletion:', id);
        return false;
      }

      const scheduleToDelete = this.scheduledRingtones[index];

      // Try to delete Windows Task Scheduler task only for device-based schedules
      if (scheduleToDelete.scheduleSource === 'device') {
        try {
          await this.deleteWindowsTask(id);
          console.log('✅ Deleted Windows Task Scheduler task:', id);
        } catch (taskError) {
          console.warn('⚠️ Failed to delete Windows Task Scheduler task, but continuing with local deletion:', taskError);
          // Continue with local deletion even if Windows task deletion fails
        }
      } else {
        console.log('ℹ️ Web-based schedule, no Windows Task Scheduler task to delete');
      }

      // Always delete from local storage
      this.scheduledRingtones.splice(index, 1);
      await this.saveToStorage();
      
      console.log('✅ Deleted schedule:', id);
      return true;
    } catch (error) {
      console.error('❌ Error deleting schedule:', error);
      return false;
    }
  }

  // Toggle schedule active status
  public async toggleSchedule(id: string): Promise<boolean> {
    try {
      const schedule = this.scheduledRingtones.find(s => s.id === id);
      if (!schedule) {
        console.warn('⚠️ Schedule not found for toggle:', id);
        return false;
      }

      schedule.isActive = !schedule.isActive;
      
      // Update Windows Task Scheduler task status only for device-based schedules
      if (schedule.scheduleSource === 'device') {
        const taskSchedulerAvailable = await this.isTaskSchedulerAvailable();
        if (taskSchedulerAvailable) {
          try {
            if (schedule.isActive) {
              await this.enableWindowsTask(id);
            } else {
              await this.disableWindowsTask(id);
            }
          } catch (taskError) {
            console.warn('⚠️ Failed to update Windows Task Scheduler task, but continuing with local update:', taskError);
          }
        } else {
          console.log('ℹ️ Windows Task Scheduler not available, updating local schedule only');
        }
      } else {
        console.log('ℹ️ Web-based schedule, no Windows Task Scheduler interaction needed');
      }
      
      await this.saveToStorage();
      
      console.log('✅ Toggled schedule and Windows Task:', id, 'Active:', schedule.isActive);
      return true;
    } catch (error) {
      console.error('❌ Error toggling schedule:', error);
      return false;
    }
  }

  // Start the schedule checker
  private startScheduleChecker(): void {
    // Check every minute
    this.checkInterval = setInterval(() => {
      this.checkSchedules();
    }, 60000); // 60 seconds

    console.log('⏰ Started schedule checker');
  }

  // Stop the schedule checker
  public stopScheduleChecker(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
      console.log('⏹️ Stopped schedule checker');
    }
  }

  // Check if any schedules should be triggered
  private checkSchedules(): void {
    try {
      const now = new Date();
      const currentTime = now.toTimeString().slice(0, 5); // "HH:MM" format
      const currentDay = now.getDay(); // 0 = Sunday, 1 = Monday, etc.

      const activeSchedules = this.getActiveSchedules();
      
      for (const schedule of activeSchedules) {
        // Check if it's the right time and day
        if (schedule.time === currentTime && schedule.days.includes(currentDay)) {
          // Check if we haven't played this schedule today
          const today = now.toDateString();
          const lastPlayed = schedule.lastPlayed ? new Date(schedule.lastPlayed).toDateString() : null;
          
          if (lastPlayed !== today) {
            this.playScheduledRingtone(schedule);
          }
        }
      }
    } catch (error) {
      console.error('❌ Error checking schedules:', error);
    }
  }

  // Play a scheduled ringtone
  private async playScheduledRingtone(schedule: ScheduledRingtone): Promise<void> {
    try {
      console.log('🔔 Playing scheduled ringtone:', schedule.ringtoneName);
      
      // Create audio element if it doesn't exist
      if (!this.audioElement) {
        this.audioElement = new Audio();
      }

      // Set the audio source
      this.audioElement.src = schedule.ringtoneUrl;
      this.audioElement.volume = 1.0; // Full volume for scheduled ringtones
      
      // Play the audio
      await this.audioElement.play();
      
      // Update last played time
      this.updateSchedule(schedule.id, { lastPlayed: new Date().toISOString() });
      
      console.log('✅ Scheduled ringtone played successfully');
    } catch (error) {
      console.error('❌ Error playing scheduled ringtone:', error);
    }
  }


  // Stop current audio
  public stopAudio(): void {
    try {
      if (this.audioElement) {
        this.audioElement.pause();
        this.audioElement.currentTime = 0;
        console.log('⏹️ Audio stopped');
      }
    } catch (error) {
      console.error('❌ Error stopping audio:', error);
    }
  }

  // Check if Windows Task Scheduler service is available
  private async isTaskSchedulerAvailable(): Promise<boolean> {
    try {
      console.log('🔍 Checking Windows Task Scheduler availability...');
      const response = await fetch(`${API_BASE_URL}/api/task-scheduler/status`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      console.log('📡 Task Scheduler status response:', response.status, response.statusText);

      if (!response.ok) {
        console.warn('❌ Task Scheduler status endpoint returned error:', response.status, response.statusText);
        return false;
      }

      const result = await response.json();
      console.log('📋 Task Scheduler status result:', result);
      
      const isAvailable = result.success && result.available;
      console.log('✅ Task Scheduler available:', isAvailable);
      return isAvailable;
    } catch (error) {
      console.error('❌ Error checking Windows Task Scheduler service:', error);
      return false;
    }
  }

  // Windows Task Scheduler integration methods
  private async createWindowsTask(schedule: ScheduledRingtone): Promise<void> {
    try {
      // Use the file path if available, otherwise fall back to URL
      const ringtonePath = schedule.ringtoneFilePath || schedule.ringtoneUrl;
      
      if (!schedule.ringtoneFilePath) {
        console.warn('⚠️ No file path available for ringtone, using URL (may not work with Windows Task Scheduler)');
      }
      
      console.log('🔧 Creating Windows Task with ringtone path:', ringtonePath);
      console.log('🔧 Schedule object:', schedule);
      
      const response = await fetch(`${API_BASE_URL}/api/task-scheduler/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_name: schedule.id,
          ringtone_path: ringtonePath,
          time: schedule.time,
          days: schedule.days
        })
      });

      const result = await response.json();
      if (!result.success) {
        console.error('❌ Windows Task Scheduler API error:', result);
        throw new Error(result.error || 'Failed to create Windows task');
      }

      console.log('✅ Created Windows Task Scheduler task:', schedule.id);
    } catch (error) {
      console.error('❌ Error creating Windows task:', error);
      throw error;
    }
  }

  private async deleteWindowsTask(taskId: string): Promise<void> {
    try {
      console.log('🔄 Attempting to delete Windows Task Scheduler task:', taskId);
      
      const response = await fetch(`${API_BASE_URL}/api/task-scheduler/delete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_name: taskId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.error || 'Failed to delete Windows task');
      }

      console.log('✅ Deleted Windows Task Scheduler task:', taskId);
    } catch (error) {
      console.error('❌ Error deleting Windows task:', error);
      throw error;
    }
  }

  private async enableWindowsTask(taskId: string): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/task-scheduler/enable`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_name: taskId
        })
      });

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.error || 'Failed to enable Windows task');
      }

      console.log('✅ Enabled Windows Task Scheduler task:', taskId);
    } catch (error) {
      console.error('❌ Error enabling Windows task:', error);
      throw error;
    }
  }

  private async disableWindowsTask(taskId: string): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/task-scheduler/disable`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task_name: taskId
        })
      });

      const result = await response.json();
      if (!result.success) {
        throw new Error(result.error || 'Failed to disable Windows task');
      }

      console.log('✅ Disabled Windows Task Scheduler task:', taskId);
    } catch (error) {
      console.error('❌ Error disabling Windows task:', error);
      throw error;
    }
  }

  // Test ringtone playback using Windows Task Scheduler service or fallback
  public async testPlayRingtone(ringtone: AudioFile): Promise<void> {
    try {
      // Try Windows Task Scheduler service first
      const taskSchedulerAvailable = await this.isTaskSchedulerAvailable();
      if (taskSchedulerAvailable) {
        try {
          let ringtoneFilePath: string;
          
          // Check if this is a backend ringtone (already has a file path)
          if (ringtone.url.startsWith('http://localhost:5000/api/ringtones/')) {
            console.log('📁 This is a backend ringtone, using file path from backend...');
            
            if (ringtone.filePath) {
              // Use the file path provided by the backend
              ringtoneFilePath = ringtone.filePath;
              console.log('✅ Using file path from backend:', ringtoneFilePath);
            } else {
              // Fallback: extract the file path from the URL
              console.log('⚠️ No file path provided, extracting from URL...');
              const urlParts = ringtone.url.split('/');
              const folder = urlParts[urlParts.length - 2]; // e.g., 'wav_ringtones' or 'mp3_ringtones'
              const filename = urlParts[urlParts.length - 1]; // e.g., 'ringtone_20231201_120000_song.wav'
              
              // Construct the file path
              ringtoneFilePath = `portable_app/backend/ringtones/${folder}/${filename}`;
              console.log('✅ Extracted file path from backend URL:', ringtoneFilePath);
            }
          } else {
            // This is a local ringtone, save it to get the file path
            console.log('💾 Saving ringtone for testing...');
            const saveResult = await ringtoneService.saveRingtone(ringtone);
            
            if (!saveResult.success) {
              throw new Error(`Failed to save ringtone for testing: ${saveResult.error || 'Unknown error'}`);
            }
            
            ringtoneFilePath = saveResult.file_path;
            console.log('✅ Ringtone saved for testing:', ringtoneFilePath);
          }
          
          const response = await fetch(`${API_BASE_URL}/api/task-scheduler/test`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              ringtone_path: ringtoneFilePath
            })
          });

          const result = await response.json();
          if (!result.success) {
            throw new Error(result.error || 'Failed to test ringtone');
          }

          console.log('✅ Tested ringtone via Windows Task Scheduler:', ringtone.name);
          return;
        } catch (taskError) {
          console.warn('⚠️ Windows Task Scheduler test failed, falling back to browser audio:', taskError);
        }
      }

      // Fallback to browser audio
      console.log('🔄 Using browser audio fallback for testing:', ringtone.name);
      if (!this.audioElement) {
        this.audioElement = new Audio();
      }

      this.audioElement.src = ringtone.url;
      this.audioElement.volume = 0.5; // Lower volume for testing
      
      await this.audioElement.play();
      console.log('✅ Test ringtone played successfully via browser audio');
    } catch (error) {
      console.error('❌ Error testing ringtone:', error);
      throw error;
    }
  }

  // Cleanup method
  public destroy(): void {
    this.stopScheduleChecker();
    this.stopAudio();
    this.audioElement = null;
  }
}

// Export singleton instance
export const scheduleService = ScheduleService.getInstance();
