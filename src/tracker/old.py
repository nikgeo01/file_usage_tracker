import os
import csv
import time
import psutil
import win32gui
import win32process
import win32com.client
import ctypes
from datetime import datetime
import glob

def get_last_input_time():
    """Get the time (in seconds) since the last user input event."""
    
    class LASTINPUTINFO(ctypes.Structure):
        _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_ulong)]
    
    lastInputInfo = LASTINPUTINFO()
    lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
    
    # Get last input info using ctypes
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo)):
        millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
        return millis / 1000.0  # Convert to seconds
    else:
        return 0  # If it fails, assume no idle time (0 seconds)

def get_active_window_info():
    window_handle = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(window_handle)
    try:
        process = psutil.Process(pid)
        app_name = process.name()
        user_name = os.getlogin()
        file_path = None
        window_title = win32gui.GetWindowText(window_handle)

        # Application-specific handling
        app_name_lower = app_name.lower()
        if app_name_lower == 'acad.exe':
            file_path = get_autocad_active_document()
        elif app_name_lower == 'archicad.exe':
            file_path = get_archicad_active_document()
        else:
            # For other applications, record as "others"
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

def get_archicad_active_document():
    # ArchiCAD may not have a COM API accessible via win32com.client
    # Placeholder function: implementation depends on ArchiCAD's API
    # For demonstration purposes, we'll attempt to get the window title
    window_handle = win32gui.GetForegroundWindow()
    window_title = win32gui.GetWindowText(window_handle)
    if 'ArchiCAD' in window_title:
        return window_title  # Using window title as a placeholder
    return None

def get_csv_filename():
    now = datetime.now()
    rounded_hour = now.replace(minute=0, second=0, microsecond=0)
    filename = rounded_hour.strftime('%H-%M_%d_%m_%Y.csv')
    return filename

def get_daily_csv_filename():
    now = datetime.now()
    user_name = os.getlogin()
    filename = f"{user_name}_{now.strftime('%d_%m_%Y')}.csv"
    return filename

def process_hourly_csv(filename):
    try:
        data = []
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                app_name = row['App Used']
                file_path = row['File Path'] or row['File in App Used']
                time_used = float(row['Time Used (seconds)'])
                data.append({
                    'app_name': app_name,
                    'file_path': file_path,
                    'time_used': time_used
                })

        # Aggregate time used per file per application
        aggregated_data = {}
        for item in data:
            key = (item['app_name'], item['file_path'])
            if key in aggregated_data:
                aggregated_data[key] += item['time_used']
            else:
                aggregated_data[key] = item['time_used']

        # Prepare data for writing
        aggregated_list = []
        hour_of_day = datetime.strptime(filename, '%H-%M_%d_%m_%Y.csv').strftime('%H:%M')
        for key, total_time in aggregated_data.items():
            app_name, file_path = key
            aggregated_list.append({
                'app_name': app_name,
                'file_path': file_path,
                'time_used': total_time,
                'hour_of_day': hour_of_day
            })

        # Sort the data by application name
        aggregated_list.sort(key=lambda x: x['app_name'])

        # Append aggregated data to the daily CSV file
        daily_csv_filename = get_daily_csv_filename()
        file_exists = os.path.isfile(daily_csv_filename)
        with open(daily_csv_filename, 'a', newline='', encoding='utf-8') as daily_csv:
            fieldnames = ['App Used', 'File', 'Time Spent on File (seconds)', 'Hour of Day']
            csv_writer = csv.DictWriter(daily_csv, fieldnames=fieldnames)
            if not file_exists:
                csv_writer.writeheader()
            for item in aggregated_list:
                csv_writer.writerow({
                    'App Used': item['app_name'],
                    'File': item['file_path'],
                    'Time Spent on File (seconds)': item['time_used'],
                    'Hour of Day': item['hour_of_day']
                })

        # Delete the hourly CSV file after processing
        os.remove(filename)
        print(f"Processed and deleted hourly file: {filename}")

    except Exception as e:
        print(f"Error processing hourly CSV {filename}: {e}")

def process_unprocessed_hourly_files(current_csv_filename):
    # Get a list of all hourly CSV files in the directory
    hourly_files = glob.glob('??-??_??_??_????.csv')

    # Process files that are not the current hourly file
    for filename in hourly_files:
        if filename != current_csv_filename:
            process_hourly_csv(filename)

def main():
    current_window_info = None
    start_time = None
    current_csv_filename = get_csv_filename()

    # At startup, process any unprocessed hourly CSV files
    process_unprocessed_hourly_files(current_csv_filename)

    csv_file = open(current_csv_filename, 'a', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)
    # Write headers if the file is new
    if csv_file.tell() == 0:
        csv_writer.writerow(['User Name', 'App Used', 'File in App Used', 'Time Used (seconds)', 'File Path'])

    activity_paused = False

    while True:
        # Check for user activity
        idle_time = get_last_input_time()
        if idle_time >= 60:
            if not activity_paused:
                # Pause time detection
                activity_paused = True
                print("User inactive for 60 seconds. Pausing time tracking.")
                # Calculate duration up to this point
                if current_window_info and start_time:
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    # Log the time up to this point
                    csv_writer.writerow([
                        current_window_info['user_name'],
                        current_window_info['app_name'],
                        current_window_info['window_title'],
                        duration,
                        current_window_info['file_path'] or ''
                    ])
                    csv_file.flush()
                    # Reset current_window_info and start_time
                    current_window_info = None
                    start_time = None
            time.sleep(1)  # Wait before checking again
            continue
        else:
            if activity_paused:
                # Resume time detection
                activity_paused = False
                print("User activity detected. Resuming time tracking.")

        active_window_info = get_active_window_info()
        if active_window_info:
            if current_window_info is None:
                # First run or resuming after pause
                current_window_info = active_window_info
                start_time = active_window_info['time']
            elif (active_window_info['app_name'] != current_window_info['app_name'] or
                  active_window_info['file_path'] != current_window_info['file_path']):
                # App or file has changed
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
                # Process the current CSV file before switching
                csv_file.close()
                process_hourly_csv(current_csv_filename)
                # Open new CSV file
                current_csv_filename = new_csv_filename
                csv_file = open(current_csv_filename, 'a', newline='', encoding='utf-8')
                csv_writer = csv.writer(csv_file)
                # Write headers if the file is new
                if csv_file.tell() == 0:
                    csv_writer.writerow(['User Name', 'App Used', 'File in App Used', 'Time Used (seconds)', 'File Path'])
                # Also, process any other unprocessed hourly files
                process_unprocessed_hourly_files(current_csv_filename)
        else:
            # If active_window_info is None, wait and try again
            time.sleep(0.1)
            continue
        time.sleep(0.1)  # Polling interval reduced for better accuracy

    # Close the CSV file when done (this will never be reached in this loop)
    csv_file.close()

if __name__ == '__main__':
    main()
