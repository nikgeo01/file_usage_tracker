# src/tracker/activity_tracker.py

import time
from tracker.idle_tracker import get_idle_time
from tracker.file_tracker import get_active_window_info
from utils.file_utils import save_data_to_csv, process_hourly_csv, process_daily_csv
from utils.path_utils import get_current_hour_filename, get_daily_filename
from datetime import datetime
import os

class ActivityTracker:
    def __init__(self):
        # Manually set the path to the yearly files
        from utils.path_utils import set_yearly_files_path
        set_yearly_files_path('D:/path/to/your/yearly/files')  # Replace with your desired path

        self.current_window_info = None
        self.start_time = None
        self.current_csv_filename = get_current_hour_filename()
        self.activity_paused = False
        self.last_date = datetime.now().date()
        self.last_known_file_path = None
        self.last_known_app_name = ''
        self.last_known_user_name = os.getlogin()
        # Initialize CSV file with headers
        save_data_to_csv(self.current_csv_filename, [], write_header=True)

        # Process existing hourly and daily files upon startup
        self._process_existing_hourly_files()
        self._process_existing_daily_files()

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
            else:
                # If active_window_info is None, log time under 'others' for the last known user
                self._log_unknown_window()
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
        if self.current_window_info is None:
            return True
        # Treat 'others' app as the same app to continue logging time
        if new_window_info['app_name'] == 'others' and self.current_window_info['app_name'] == 'others':
            return False
        return (
            new_window_info['app_name'] != self.current_window_info['app_name'] or
            new_window_info['file_path'] != self.current_window_info['file_path']
        )

    def _log_and_update_current_window(self, new_window_info):
        """Logs the current window info and updates to the new window."""
        self._log_current_window()
        # Only update if the file path is present or app has changed
        if new_window_info['file_path'] or \
        (self.current_window_info is None) or \
        new_window_info['app_name'].lower() != self.current_window_info['app_name'].lower():
            self.current_window_info = new_window_info
        # Update the start time regardless
        self.start_time = new_window_info['time']


    def _log_current_window(self):
        """Logs the time spent on the current window to the hourly CSV."""
        if self.current_window_info and self.start_time:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()

            current_app_name = self.current_window_info['app_name'] or 'others'
            current_user_name = self.current_window_info['user_name'] or (self.last_known_user_name or os.getlogin())

            file_path = self.current_window_info['file_path'] or ''
            file_name = self.current_window_info['file_name'] or '-'

            data = [
                current_user_name,
                current_app_name,
                file_name,
                duration,
                file_path,
                self.start_time.strftime('%Y-%m-%d %H:00')
            ]
            save_data_to_csv(self.current_csv_filename, [data])

            # Update last known user and app
            self.last_known_user_name = current_user_name
            self.last_known_app_name = current_app_name

            # Update the last known file path if current one is available
            if self.current_window_info['file_path']:
                self.last_known_file_path = self.current_window_info['file_path']


    def _log_unknown_window(self):
        """Logs time when the active window information is unknown."""
        # Create a dummy window info with last known user and 'others' as app
        unknown_window_info = {
            'user_name': self.current_window_info['user_name'] if self.current_window_info else os.getlogin(),
            'app_name': 'others',
            'file_name': '-',
            'time': datetime.now(),
            'file_path': None
        }
        # Check if window has changed
        if self._has_window_changed(unknown_window_info):
            self._log_and_update_current_window(unknown_window_info)



    def _check_for_hour_change(self):
        """Processes the hourly CSV if the hour has changed."""
        new_csv_filename = get_current_hour_filename()
        if new_csv_filename != self.current_csv_filename:
            process_hourly_csv(self.current_csv_filename)
            self.current_csv_filename = new_csv_filename
            # Initialize new hourly CSV with headers
            save_data_to_csv(self.current_csv_filename, [], write_header=True)
            # Check if the day has changed
            if self._has_day_changed():
                daily_filename = get_daily_filename()
                process_daily_csv(daily_filename)  # Call the new function

    def _has_day_changed(self):
        """Checks if the day has changed."""
        current_date = datetime.now().date()
        if self.last_date != current_date:
            self.last_date = current_date
            return True
        else:
            return False

    def _process_existing_hourly_files(self):
        """Processes any existing hourly CSV files upon startup."""
        import glob
        # Get all hourly CSV files matching the pattern
        hourly_files = glob.glob('??-??_??_??_????.csv')
        for hourly_file in hourly_files:
            if hourly_file != self.current_csv_filename:
                print(f"Processing existing hourly file: {hourly_file}")
                process_hourly_csv(hourly_file)

    def _process_existing_daily_files(self):
        """Processes any existing daily CSV files upon startup."""
        import glob
        from datetime import datetime

        today_date = datetime.now().date()
        daily_files = glob.glob(f"{os.getlogin()}_??_??_????.csv")
        for daily_file in daily_files:
            # Extract the date from the filename
            date_str = daily_file.replace(f"{os.getlogin()}_", "").replace(".csv", "")
            try:
                file_date = datetime.strptime(date_str, '%d_%m_%Y').date()
                if file_date < today_date:
                    print(f"Processing existing daily file: {daily_file}")
                    process_daily_csv(daily_file)
            except ValueError:
                print(f"Skipping file with invalid date format: {daily_file}")
