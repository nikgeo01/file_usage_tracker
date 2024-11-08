import os
import psutil
import win32gui
import win32process
from tracker.autocad_utils import get_autocad_active_document
from tracker.archicad_utils import get_archicad_active_document
from datetime import datetime

def get_active_window_info():
    window_handle = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(window_handle)
    try:
        process = psutil.Process(pid)
        app_name = process.name()
        user_name = os.getlogin()
        window_title = win32gui.GetWindowText(window_handle)
        file_path = None

        if app_name.lower() == 'acad.exe':
            file_path = get_autocad_active_document()
        elif app_name.lower() == 'archicad.exe':
            file_path = get_archicad_active_document()
        else:
            app_name = "others"
            window_title = "-"
            file_path = "-"

        return {
            'user_name': user_name,
            'app_name': app_name,
            'window_title': window_title,
            'time': datetime.now(),
            'file_path': file_path
        }
    except Exception as e:
        print(f"Error in get_active_window_info: {e}")
        return None
