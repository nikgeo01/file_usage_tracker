# src/tracker/file_tracker.py

import os
import psutil
import win32gui
import win32process
from tracker.autocad_utils import get_autocad_active_document
from tracker.archicad_utils import get_archicad_active_document
from datetime import datetime

def get_active_window_info():
    window_handle = win32gui.GetForegroundWindow()
    if not window_handle:
        return None  # No active window

    try:
        _, pid = win32process.GetWindowThreadProcessId(window_handle)
        if pid <= 0:
            # Invalid PID
            print(f"Invalid PID retrieved: {pid}")
            return None

        process = psutil.Process(pid)
        app_name = process.name()
        user_name = os.getlogin()
        window_title = win32gui.GetWindowText(window_handle)
        file_path = None
        file_name = None

        if app_name.lower() == 'acad.exe':
            file_path = get_autocad_active_document()
            file_name = os.path.basename(file_path) if file_path else "-"
        elif app_name.lower() == 'archicad.exe':
            file_path = get_archicad_active_document()
            file_name = os.path.basename(file_path) if file_path else "-"
        else:
            app_name = "others"
            window_title = "-"
            file_path = "-"
            file_name = "-"

        return {
            'user_name': user_name,
            'app_name': app_name,
            'window_title': window_title,
            'time': datetime.now(),
            'file_path': file_path,
            'file_name': file_name
        }
    except psutil.NoSuchProcess:
        print(f"No such process with PID: {pid}")
        return None
    except Exception as e:
        print(f"Error in get_active_window_info: {e}")
        return None


def extract_project_name(file_path):
    """Extracts the project name as a sequence of three or more digits before the first dash."""
    import re
    match = re.search(r'(\d{3,})-', file_path)
    if match:
        return match.group(1)
    return "Unknown"
