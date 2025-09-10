// Rules applied
export interface ScheduledRingtone {
  id: string;
  ringtoneId: string;
  ringtoneName: string;
  ringtoneUrl: string;
  ringtoneFilePath?: string; // Actual file path on the filesystem for Windows Task Scheduler
  time: string; // Format: "HH:MM" (24-hour format)
  days: number[]; // Array of day numbers (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
  isActive: boolean;
  scheduleSource: 'web' | 'device'; // How the schedule is managed
  createdAt: string;
  lastPlayed?: string;
}

export interface ScheduleFormData {
  ringtoneId: string;
  time: string;
  days: number[];
  scheduleSource: 'web' | 'device'; // 'web' for browser-based, 'device' for Windows Task Scheduler
}

export const DAYS_OF_WEEK = [
  { value: 0, label: 'Sunday', short: 'Sun' },
  { value: 1, label: 'Monday', short: 'Mon' },
  { value: 2, label: 'Tuesday', short: 'Tue' },
  { value: 3, label: 'Wednesday', short: 'Wed' },
  { value: 4, label: 'Thursday', short: 'Thu' },
  { value: 5, label: 'Friday', short: 'Fri' },
  { value: 6, label: 'Saturday', short: 'Sat' }
] as const;
