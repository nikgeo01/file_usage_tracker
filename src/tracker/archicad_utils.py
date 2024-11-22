def get_archicad_active_document():
    """
    Retrieve the file name of the active document in ArchiCAD.
    """
    import win32gui
    import win32process
    import psutil

    archicad_exe_name = 'ArchiCAD.exe'  # Update if necessary

    # Find ArchiCAD's main window
    def enum_windows_callback(hwnd, window_titles):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            if process.name().lower() == archicad_exe_name.lower():
                title = win32gui.GetWindowText(hwnd)
                if title:
                    window_titles.append(title)

    window_titles = []
    win32gui.EnumWindows(enum_windows_callback, window_titles)

    if window_titles:
        # Assume the first title is the active document's name
        # Remove any additional text or parse as needed
        return window_titles[0]
    else:
        return None
