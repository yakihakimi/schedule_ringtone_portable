// Rules applied
import React, { useState, useEffect } from 'react';
import { AudioFile } from '../types/audio';
import { ScheduledRingtone, ScheduleFormData, DAYS_OF_WEEK } from '../types/schedule';
import { scheduleService } from '../services/scheduleService';

interface ScheduleRingtoneProps {
  ringtones: AudioFile[];
}

const ScheduleRingtone: React.FC<ScheduleRingtoneProps> = ({ ringtones }) => {
  const [schedules, setSchedules] = useState<ScheduledRingtone[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<ScheduledRingtone | null>(null);
  const [formData, setFormData] = useState<ScheduleFormData>({
    ringtoneId: '',
    time: '',
    days: [],
    scheduleSource: 'web' // Default to web-based scheduling
  });
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Load schedules on component mount
  useEffect(() => {
    loadSchedules();
  }, []);

  const loadSchedules = () => {
    try {
      const allSchedules = scheduleService.getAllSchedules();
      setSchedules(allSchedules);
      console.log('📅 Loaded schedules:', allSchedules.length);
    } catch (error) {
      console.error('❌ Error loading schedules:', error);
      setError(`Error loading schedules: ${error}`);
    }
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      setIsLoading(true);
      setError(null);
      setSuccess(null);

      // Validate form data
      if (!formData.ringtoneId || !formData.time || formData.days.length === 0 || !formData.scheduleSource) {
        setError('Please fill in all required fields');
        return;
      }

      // Find the selected ringtone
      const selectedRingtone = ringtones.find(r => r.id === formData.ringtoneId);
      if (!selectedRingtone) {
        setError('Selected ringtone not found');
        return;
      }

      if (editingSchedule) {
        // Update existing schedule
        const success = await scheduleService.updateScheduleWithFormData(editingSchedule.id, selectedRingtone, formData);
        if (success) {
          // Update local state
          setSchedules(prev => prev.map(s => 
            s.id === editingSchedule.id 
              ? { ...s, ringtoneId: formData.ringtoneId, ringtoneName: selectedRingtone.name, time: formData.time, days: formData.days }
              : s
          ));
          setSuccess(`Schedule updated successfully! Ringtone will play at ${formData.time} on selected days.`);
        } else {
          setError('Failed to update schedule');
          return;
        }
      } else {
        // Create new schedule
        const newSchedule = await scheduleService.createSchedule(selectedRingtone, formData);
        
        // Update local state
        setSchedules(prev => [...prev, newSchedule]);
        setSuccess(`Schedule created successfully! Ringtone will play at ${formData.time} on selected days.`);
      }
      
      // Reset form
      setFormData({
        ringtoneId: '',
        time: '',
        days: [],
        scheduleSource: 'web'
      });
      setEditingSchedule(null);
      setShowForm(false);
      
      console.log('✅ Schedule created successfully');
    } catch (error) {
      console.error('❌ Error creating schedule:', error);
      setError(`Error creating schedule: ${error}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDayToggle = (dayValue: number) => {
    try {
      setFormData(prev => ({
        ...prev,
        days: prev.days.includes(dayValue)
          ? prev.days.filter(d => d !== dayValue)
          : [...prev.days, dayValue]
      }));
    } catch (error) {
      console.error('❌ Error toggling day:', error);
      setError(`Error updating days: ${error}`);
    }
  };

  const handleDeleteSchedule = async (scheduleId: string) => {
    try {
      const success = await scheduleService.deleteSchedule(scheduleId);
      if (success) {
        setSchedules(prev => prev.filter(s => s.id !== scheduleId));
        setSuccess('Schedule deleted successfully');
        console.log('✅ Schedule deleted successfully');
      } else {
        setError('Failed to delete schedule');
      }
    } catch (error) {
      console.error('❌ Error deleting schedule:', error);
      setError(`Error deleting schedule: ${error}`);
    }
  };

  const handleToggleSchedule = async (scheduleId: string) => {
    try {
      const success = await scheduleService.toggleSchedule(scheduleId);
      if (success) {
        setSchedules(prev => prev.map(s => 
          s.id === scheduleId ? { ...s, isActive: !s.isActive } : s
        ));
        setSuccess('Schedule status updated');
        console.log('✅ Schedule status updated');
      } else {
        setError('Failed to update schedule');
      }
    } catch (error) {
      console.error('❌ Error toggling schedule:', error);
      setError(`Error updating schedule: ${error}`);
    }
  };

  const handleTestRingtone = async (ringtone: AudioFile) => {
    try {
      await scheduleService.testPlayRingtone(ringtone);
      setSuccess(`Testing ringtone: ${ringtone.name}`);
    } catch (error) {
      console.error('❌ Error testing ringtone:', error);
      setError(`Error testing ringtone: ${error}`);
    }
  };

  const handlePauseRingtone = () => {
    try {
      scheduleService.stopAudio();
      setSuccess('Audio paused');
    } catch (error) {
      console.error('❌ Error pausing ringtone:', error);
      setError(`Error pausing ringtone: ${error}`);
    }
  };

  const handleEditSchedule = (schedule: ScheduledRingtone) => {
    try {
      console.log('🔄 Editing schedule:', schedule.id);
      setEditingSchedule(schedule);
      setFormData({
        ringtoneId: schedule.ringtoneId,
        time: schedule.time,
        days: [...schedule.days],
        scheduleSource: schedule.scheduleSource
      });
      setShowForm(true);
      setError(null);
      setSuccess(null);
    } catch (error) {
      console.error('❌ Error starting edit:', error);
      setError(`Error starting edit: ${error}`);
    }
  };

  const formatDays = (days: number[]): string => {
    if (days.length === 0) return 'No days selected';
    if (days.length === 7) return 'Every day';
    
    const dayNames = days
      .sort()
      .map(day => DAYS_OF_WEEK.find(d => d.value === day)?.short)
      .filter(Boolean);
    
    return dayNames.join(', ');
  };

  const getScheduleStatus = (schedule: ScheduledRingtone): string => {
    if (!schedule.isActive) return 'Inactive';
    
    const now = new Date();
    const currentTime = now.toTimeString().slice(0, 5);
    const currentDay = now.getDay();
    
    if (schedule.time === currentTime && schedule.days.includes(currentDay)) {
      return 'Playing now';
    }
    
    return 'Active';
  };

  return (
    <div className="schedule-ringtone">
      <h2>⏰ Schedule Ringtone</h2>
      <p>Set up your ringtones to play automatically at specific times on selected days.</p>

      {/* Success/Error Messages */}
      {success && (
        <div className="success-message">
          <p>✅ {success}</p>
          <button onClick={() => setSuccess(null)}>Dismiss</button>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>❌ {error}</p>
          <button onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      {/* Create New Schedule Button */}
      <div className="schedule-actions">
        <button 
          className="create-schedule-button"
          onClick={() => {
            setShowForm(!showForm);
            if (showForm) {
              setEditingSchedule(null);
              setFormData({
                ringtoneId: '',
                time: '',
                days: [],
                scheduleSource: 'web'
              });
            }
          }}
        >
          {showForm ? '❌ Cancel' : '➕ Create New Schedule'}
        </button>
      </div>

      {/* Schedule Form */}
      {showForm && (
        <div className="schedule-form">
          <h3>{editingSchedule ? 'Edit Schedule' : 'Create New Schedule'}</h3>
          <form onSubmit={handleFormSubmit}>
            {/* Ringtone Selection */}
            <div className="form-group">
              <label htmlFor="ringtone-select">Select Ringtone:</label>
              <select
                id="ringtone-select"
                value={formData.ringtoneId}
                onChange={(e) => setFormData(prev => ({ ...prev, ringtoneId: e.target.value }))}
                required
              >
                <option value="">Choose a ringtone...</option>
                {ringtones.map(ringtone => (
                  <option key={ringtone.id} value={ringtone.id}>
                    {ringtone.name}
                  </option>
                ))}
              </select>
              {formData.ringtoneId && (
                <button
                  type="button"
                  className="test-button"
                  onClick={() => {
                    const ringtone = ringtones.find(r => r.id === formData.ringtoneId);
                    if (ringtone) handleTestRingtone(ringtone);
                  }}
                >
                  🔊 Test
                </button>
              )}
            </div>

            {/* Time Selection */}
            <div className="form-group">
              <label htmlFor="time-input">Time:</label>
              <input
                type="time"
                id="time-input"
                value={formData.time}
                onChange={(e) => setFormData(prev => ({ ...prev, time: e.target.value }))}
                required
              />
            </div>

            {/* Days Selection */}
            <div className="form-group">
              <label>Days of the week:</label>
              <div className="days-selection">
                {DAYS_OF_WEEK.map(day => (
                  <label key={day.value} className="day-checkbox">
                    <input
                      type="checkbox"
                      checked={formData.days.includes(day.value)}
                      onChange={() => handleDayToggle(day.value)}
                    />
                    <span>{day.short}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Schedule Source Selection */}
            <div className="form-group">
              <label>Schedule Method:</label>
              <div className="schedule-source-selection">
                <label className="source-radio">
                  <input
                    type="radio"
                    name="scheduleSource"
                    value="web"
                    checked={formData.scheduleSource === 'web'}
                    onChange={(e) => setFormData(prev => ({ ...prev, scheduleSource: e.target.value as 'web' | 'device' }))}
                  />
                  <span>🌐 Web-based (Browser only)</span>
                  <small>Ringtones play only when browser is open</small>
                </label>
                <label className="source-radio">
                  <input
                    type="radio"
                    name="scheduleSource"
                    value="device"
                    checked={formData.scheduleSource === 'device'}
                    onChange={(e) => setFormData(prev => ({ ...prev, scheduleSource: e.target.value as 'web' | 'device' }))}
                  />
                  <span>💻 Device-based (Windows Task Scheduler)</span>
                  <small>Ringtones play even when browser is closed</small>
                </label>
              </div>
            </div>

            {/* Submit Button */}
            <div className="form-actions">
              <button 
                type="submit" 
                className="submit-button"
                disabled={isLoading}
              >
                {isLoading ? (editingSchedule ? 'Updating...' : 'Creating...') : (editingSchedule ? 'Update Schedule' : 'Create Schedule')}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Schedules List */}
      <div className="schedules-list">
        <h3>📅 Your Schedules ({schedules.length})</h3>
        
        {schedules.length === 0 ? (
          <div className="no-schedules">
            <p>No schedules created yet. Create your first schedule above!</p>
          </div>
        ) : (
          <div className="schedules-grid">
            {schedules.map(schedule => (
              <div key={schedule.id} className={`schedule-item ${schedule.isActive ? 'active' : 'inactive'}`}>
                <div className="schedule-info">
                  <h4>{schedule.ringtoneName}</h4>
                  <p><strong>Time:</strong> {schedule.time}</p>
                  <p><strong>Days:</strong> {formatDays(schedule.days)}</p>
                  <p><strong>Method:</strong> {schedule.scheduleSource === 'web' ? '🌐 Web-based' : '💻 Device-based'}</p>
                  <p><strong>Status:</strong> {getScheduleStatus(schedule)}</p>
                  {schedule.lastPlayed && (
                    <p><strong>Last played:</strong> {new Date(schedule.lastPlayed).toLocaleString()}</p>
                  )}
                </div>
                
                <div className="schedule-controls">
                  <button
                    className={`toggle-button ${schedule.isActive ? 'deactivate' : 'activate'}`}
                    onClick={() => handleToggleSchedule(schedule.id)}
                    title={schedule.isActive ? 'Deactivate' : 'Activate'}
                  >
                    {schedule.isActive ? '⏸️ Deactivate' : '▶️ Activate'}
                  </button>
                  
                  <button
                    className="test-button"
                    onClick={() => {
                      const ringtone = ringtones.find(r => r.id === schedule.ringtoneId);
                      if (ringtone) handleTestRingtone(ringtone);
                    }}
                    title="Test ringtone"
                  >
                    🔊 Test
                  </button>
                  
                  <button
                    className="edit-button"
                    onClick={() => handleEditSchedule(schedule)}
                    title="Edit schedule"
                  >
                    ✏️ Edit
                  </button>
                  
                  <button
                    className="pause-button"
                    onClick={handlePauseRingtone}
                    title="Pause audio"
                  >
                    ⏸️ Pause
                  </button>
                  
                  <button
                    className="delete-button"
                    onClick={() => handleDeleteSchedule(schedule.id)}
                    title="Delete schedule"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="schedule-instructions">
        <h3>📋 How it works:</h3>
        <ul>
          <li>Select a ringtone from your existing ringtones</li>
          <li>Choose the time when you want it to play (24-hour format)</li>
          <li>Select which days of the week it should play</li>
          <li>The ringtone will automatically play at the specified time on selected days</li>
          <li>Each schedule can only play once per day</li>
          <li>Use the test button to preview ringtones before scheduling</li>
        </ul>
      </div>
    </div>
  );
};

export default ScheduleRingtone;
