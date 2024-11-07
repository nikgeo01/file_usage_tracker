import os
import csv
import time
import psutil
import win32gui
import win32process
import win32com.client
from datetime import datetime

def get_active_window_info():
    window_handle = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(window_handle)
    try:
        process = psutil.Process(pid)
        app_name = process.name()
        window_title = win32gui.GetWindowText(window_handle)
        user_name = os.getlogin()
        file_path = None

        # Application-specific handling
        app_name_lower = app_name.lower()
        if app_name_lower == 'acad.exe':
            file_path = get_autocad_active_document()
        elif app_name_lower == 'archicad.exe':
            file_path = get_archicad_active_document()
        # Add more applications as needed

        # Fallback to process open files (may not always work)
        if not file_path:
            open_files = process.open_files()
            if open_files:
                file_path = open_files[0].path

        return {
            'user_name': user_name,
            'app_name': app_name,
            'window_title': window_title,
            'time': datetime.now(),
            'file_path': file_path
        }
    except Exception as e:
        # Handle exceptions to prevent the script from stopping
        print(f"Error in get_active_window_info: {e}")
        return None

def get_autocad_active_document():
    try:
        acad_app = win32com.client.GetActiveObject("AutoCAD.Application")
        active_doc = acad_app.ActiveDocument
        if active_doc:
            return active_doc.FullName
    except Exception as e:
        print(f"Error accessing AutoCAD document: {e}")
    return None

def save_autocad_document():
    try:
        acad_app = win32com.client.GetActiveObject("AutoCAD.Application")
        active_doc = acad_app.ActiveDocument
        if active_doc:
            active_doc.Save()
            print("AutoCAD document saved.")
    except Exception as e:
        print(f"Error saving AutoCAD document: {e}")

def get_archicad_active_document():
    # ArchiCAD does not have a COM API accessible via win32com by default.
    # You might need to use other methods or an API provided by Graphisoft.
    # Placeholder function:
    try:
        # Assuming there is a COM interface for ArchiCAD
        archicad_app = win32com.client.GetActiveObject("ArchiCAD.Application")
        active_doc = archicad_app.ActiveDocument
        if active_doc:
            return active_doc.FullName
    except Exception as e:
        print(f"Error accessing ArchiCAD document: {e}")
    return None

def save_archicad_document():
    try:
        # Assuming there is a COM interface for ArchiCAD
        archicad_app = win32com.client.GetActiveObject("ArchiCAD.Application")
        active_doc = archicad_app.ActiveDocument
        if active_doc:
            active_doc.Save()
            print("ArchiCAD document saved.")
    except Exception as e:
        print(f"Error saving ArchiCAD document: {e}")

def get_csv_filename():
    now = datetime.now()
    rounded_hour = now.replace(minute=0, second=0, microsecond=0)
    filename = rounded_hour.strftime('%H-%M_%d_%m_%Y.csv')
    return filename

def main():
    current_window_info = None
    start_time = None
    current_csv_filename = get_csv_filename()
    csv_file = open(current_csv_filename, 'a', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)
    # Write headers if the file is new
    if csv_file.tell() == 0:
        csv_writer.writerow(['User Name', 'App Used', 'File in App Used', 'Time Used (seconds)', 'File Path'])

    while True:
        active_window_info = get_active_window_info()
        if active_window_info:
            if current_window_info is None:
                # First run
                current_window_info = active_window_info
                start_time = active_window_info['time']
            elif active_window_info['window_title'] != current_window_info['window_title']:
                # Window has changed
                end_time = active_window_info['time']
                duration = (end_time - start_time).total_seconds()
                # Log the previous window info
                csv_writer.writerow([
                    current_window_info['user_name'],
                    current_window_info['app_name'],
                    current_window_info['window_title'],
                    duration,
                    current_window_info['file_path'] or ''
                ])
                csv_file.flush()
                # Update current window info and start time
                current_window_info = active_window_info
                start_time = end_time
                # Check if the hour has changed
                new_csv_filename = get_csv_filename()
                if new_csv_filename != current_csv_filename:
                    # Close current CSV file and open new one
                    csv_file.close()
                    current_csv_filename = new_csv_filename
                    csv_file = open(current_csv_filename, 'a', newline='', encoding='utf-8')
                    csv_writer = csv.writer(csv_file)
                    # Write headers if the file is new
                    if csv_file.tell() == 0:
                        csv_writer.writerow(['User Name', 'App Used', 'File in App Used', 'Time Used (seconds)', 'File Path'])
        else:
            # If active_window_info is None, wait and try again
            time.sleep(0.1)
            continue
        time.sleep(0.1)  # Polling interval reduced for better accuracy

    # Close the CSV file when done (this will never be reached in this loop)
    csv_file.close()

if __name__ == '__main__':
    main()
