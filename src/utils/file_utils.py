import csv
import os
from datetime import datetime
from utils.path_utils import get_current_hour_filename, get_daily_filename

def save_data_to_csv(filename, data, write_header=False):
    """Save data to a CSV file."""
    fieldnames = ['User Name', 'App Used', 'File in App Used', 'Time Used (seconds)', 'File Path']
    file_exists = os.path.isfile(filename)

    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if write_header and not file_exists:
            writer.writerow(fieldnames)
        writer.writerows(data)

def process_hourly_csv(filename):
    """Processes an hourly CSV file and appends data to the daily file."""
    data = []
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            app_name = row['App Used']
            file_path = row['File Path'] or row['File in App Used']
            time_used = float(row['Time Used (seconds)'])
            data.append((app_name, file_path, time_used))

    daily_filename = get_daily_filename()
    save_data_to_csv(daily_filename, data, write_header=True)
    os.remove(filename)
