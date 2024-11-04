import psutil
import win32gui
import win32process
import time
from datetime import datetime
from save_last_data import save_last_data

# Dictionary to keep track of open files with their timestamps
file_open_times = {}

def get_active_window():
    window_handle = win32gui.GetForegroundWindow()
    _, process_id = win32process.GetWindowThreadProcessId(window_handle)
    
    try:
        process = psutil.Process(process_id)
        return {
            "app_name": process.name(),
            "app_path": process.exe(),
            "window_title": win32gui.GetWindowText(window_handle),
            "pid": process_id,
            "open_files": process.open_files()
        }
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None

def track_active_files():
    current_app = None
    current_file = None
    current_file_open_time = None

    while True:
        active_app = get_active_window()
        
        if active_app and active_app != current_app:
            # Calculate time spent on the previous file if one was open
            if current_file:
                duration = datetime.now() - current_file_open_time
                if current_file in file_open_times:
                    file_open_times[current_file] += duration
                else:
                    file_open_times[current_file] = duration

                print(f"File {current_file} was open for {duration}")
                save_last_data(f"{current_file}:{duration}")

            # Update current application and file
            current_app = active_app
            print(f"Switched to Application: {current_app['app_name']} (PID: {current_app['pid']})")
            print(f"Window Title: {current_app['window_title']}")

            # Track files likely to be actively edited based on app name
            #note pad; code; word; excel; powerpoint; archicad; autocad; twinmotion; sketchup; revit; outlook; chrome; firefox; edge; opera; brave; vivaldi; tor;
            
            current_file = current_app['window_title']

            # Start timer for the new file
            current_file_open_time = datetime.now()
        
        time.sleep(0.5)  # Poll every second

