import win32gui

def get_opera_active_tab():
    """Get the active tab's title from Opera."""
    try:
        window_title = win32gui.GetWindowText(win32gui.GetForegroundWindow())
        if window_title:
            # Opera window titles usually have the format "Page Title - Opera"
            title = window_title.replace(" - Opera", "")
            return None, title
    except Exception as e:
        print(f"Error accessing Opera active tab: {e}")
    return None, None
