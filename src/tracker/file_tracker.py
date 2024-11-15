# src/tracker/file_tracker.py

import os
import psutil
import win32gui
import win32process
from tracker.autocad_utils import get_autocad_active_document
from tracker.archicad_utils import get_archicad_active_document
from tracker.excel_utils import get_excel_active_workbook
from tracker.word_utils import get_word_active_document
from tracker.chrome_utils import get_chrome_active_tab
from tracker.opera_utils import get_opera_active_tab
from datetime import datetime

def get_active_window_info():
    try:
        window_handle = win32gui.GetForegroundWindow()
        if not window_handle:
            raise Exception("No active window.")

        _, pid = win32process.GetWindowThreadProcessId(window_handle)
        if pid <= 0:
            raise Exception(f"Invalid PID retrieved: {pid}")

        process = psutil.Process(pid)
        app_name = process.name()
        user_name = os.getlogin()
        window_title = win32gui.GetWindowText(window_handle)
        file_path = None
        file_name = None

        if app_name.lower() == 'acad.exe':
            file_path = get_autocad_active_document()
            file_name = os.path.basename(file_path) if file_path else None
        elif app_name.lower() == 'archicad.exe':
            file_path = get_archicad_active_document()
            file_name = os.path.basename(file_path) if file_path else None
        elif app_name.lower() == 'excel.exe':
            file_path = get_excel_active_workbook()
            file_name = os.path.basename(file_path) if file_path else None
        elif app_name.lower() == 'winword.exe':
            file_path = get_word_active_document()
            file_name = os.path.basename(file_path) if file_path else None
        elif app_name.lower() == 'chrome.exe':
            file_path, file_name = get_chrome_active_tab()
        elif app_name.lower() == 'opera.exe':
            file_path, file_name = get_opera_active_tab()
        else:
            # For other applications, record as "others"
            app_name = "others"
            window_title = "-"
            file_path = None
            file_name = '-'

        return {
            'user_name': user_name or 'Unknown',
            'app_name': app_name or 'Unknown',
            'window_title': window_title or '-',
            'time': datetime.now(),
            'file_path': file_path,
            'file_name': file_name
        }
    except Exception as e:
        print(f"Error in get_active_window_info: {e}")
        return {
            'user_name': 'Unknown',
            'app_name': 'Unknown',
            'window_title': '-',
            'time': datetime.now(),
            'file_path': None,
            'file_name': '-'
        }


def extract_project_name(file_path):
    """Extracts the project name as a sequence of three or more digits before the first dash."""
    import re
    match = re.search(r'(\d{3,})-', file_path)
    if match:
        return match.group(1)
    return "Unknown"
