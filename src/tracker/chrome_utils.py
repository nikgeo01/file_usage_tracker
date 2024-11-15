# src/tracker/chrome_utils.py

import win32gui

def get_chrome_active_tab():
    """Get the active tab's title from Chrome."""
    try:
        window_handle = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(window_handle)
        if " - Google Chrome" in window_title:
            title = window_title.replace(" - Google Chrome", "")
            return None, title  # URL retrieval is complex; returning title only
    except Exception as e:
        print(f"Error accessing Chrome active tab: {e}")
    return None, None
