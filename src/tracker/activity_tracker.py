import time
from tracker.idle_tracker import get_idle_time
from tracker.file_tracker import get_active_window_info
from utils.file_utils import save_data_to_csv, process_hourly_csv, get_current_hour_filename, get_daily_filename
from datetime import datetime

class ActivityTracker:
    def __init__(self):
        self.current_window_info = None
        self.start_time = None
        self.current_csv_filename = get_current_hour_filename()
        self.activity_paused = False
        save_data_to_csv(self.current_csv_filename, [], write_header=True)  # Initialize CSV file

    def run(self):
        """Main loop to track activity."""
        while True:
            idle_time = get_idle_time()
            if idle_time >= 60:
                if not self.activity_paused:
                    self.pause_tracking()
                time.sleep(1)
                continue
            else:
                if self.activity_paused:
                    self.resume_tracking()

            active_window_info = get_active_window_info()
            if active_window_info:
                if self._has_window_changed(active_window_info):
                    self._log_and_update_current_window(active_window_info)
                self._check_for_hour_change()
            time.sleep(0.1)  # Reduced polling interval for accuracy

    def pause_tracking(self):
        """Pauses tracking if the user is inactive."""
        self.activity_paused = True
        print("User inactive for 60 seconds. Pausing time tracking.")
        self._log_current_window()

    def resume_tracking(self):
        """Resumes tracking when user activity is detected."""
        self.activity_paused = False
        print("User activity detected. Resuming time tracking.")
        self.current_window_info = None
        self.start_time = None

    def _has_window_changed(self, new_window_info):
        return (self.current_window_info is None or 
                new_window_info['app_name'] != self.current_window_info['app_name'] or 
                new_window_info['file_path'] != self.current_window_info['file_path'])

    def _log_and_update_current_window(self, new_window_info):
        """Logs the current window info and updates to the new window."""
        self._log_current_window()
        self.current_window_info = new_window_info
        self.start_time = new_window_info['time']

    def _log_current_window(self):
        """Logs the time spent on the current window to the hourly CSV."""
        if self.current_window_info and self.start_time:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            data = [
                self.current_window_info['user_name'],
                self.current_window_info['app_name'],
                self.current_window_info['window_title'],
                duration,
                self.current_window_info['file_path']
            ]
            save_data_to_csv(self.current_csv_filename, [data])

    def _check_for_hour_change(self):
        """Processes the hourly CSV if the hour has changed."""
        new_csv_filename = get_current_hour_filename()
        if new_csv_filename != self.current_csv_filename:
            process_hourly_csv(self.current_csv_filename)
            self.current_csv_filename = new_csv_filename
            save_data_to_csv(self.current_csv_filename, [], write_header=True)
