# src/utils/file_utils.py

import csv
import os
import re
from utils.path_utils import (
    get_daily_filename,
    get_yearly_project_filename,
    get_yearly_user_filename,
)
from datetime import datetime

def extract_project_name(file_path):
    """
    Extracts the project name as a sequence of three or more digits before the first dash in the directory pattern.
    Example:
        - 'C:/Projects/446-IMD3-3d/file.dwg' -> '446'
        - 'C:/Projects/12-XYZ/file.dwg' -> 'Unknown' (since only two digits)
    """
    match = re.search(r'(\d{3,})-', file_path)
    if match:
        return match.group(1)
    return "Unknown"

def save_data_to_csv(filename, data, write_header=False):
    """
    Save data to a CSV file.

    Args:
        filename (str): The path to the CSV file.
        data (list of lists/tuples): The data rows to write.
        write_header (bool): Whether to write the header row.
    """
    fieldnames = ['User Name', 'App Used', 'File in App Used', 'Time Used (seconds)', 'File Path', 'Hour of Day']
    file_exists = os.path.isfile(filename)

    with open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if write_header and not file_exists:
            writer.writerow(fieldnames)
        writer.writerows(data)


def process_hourly_csv(filename):
    """
    Processes an hourly CSV file and appends data to the daily file,
    recording each file used within the hour.
    """
    try:
        data = []
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                app_name = row['App Used']
                file_name = row['File in App Used']
                time_used = float(row['Time Used (seconds)'])
                hour_of_day = row.get('Hour of Day')
                if not hour_of_day:
                    # Extract hour from the filename if not present
                    try:
                        hour_of_day = datetime.strptime(filename, '%H-00_%d_%m_%Y.csv').strftime('%Y-%m-%d %H:00')
                    except ValueError:
                        hour_of_day = 'Unknown'
                data.append((hour_of_day, file_name, time_used, app_name))

        # Prepare data for writing without aggregation
        data_to_write = data

        # Append data to the daily CSV file
        daily_csv_filename = get_daily_filename()
        file_exists = os.path.isfile(daily_csv_filename)
        with open(daily_csv_filename, 'a', newline='', encoding='utf-8') as daily_csv:
            fieldnames = ['Date and Hour', 'File', 'Time Spent on File (seconds)', 'App Used']
            csv_writer = csv.writer(daily_csv)
            if not file_exists:
                csv_writer.writerow(fieldnames)
            csv_writer.writerows(data_to_write)

        # Delete the hourly CSV file after processing
        os.remove(filename)
        print(f"Processed and deleted hourly file: {filename}")

    except Exception as e:
        print(f"Error processing hourly CSV {filename}: {e}")


def process_daily_csv(daily_filename):
    """
    Processes a daily CSV file to update yearly files, then deletes the daily file.
    """
    # Get the current year
    current_year = datetime.now().year

    # Get the yearly filenames
    yearly_project_file = get_yearly_project_filename(current_year)
    yearly_user_file = get_yearly_user_filename(current_year)

    # Process Yearly Project File
    update_yearly_project_file(daily_filename, yearly_project_file)

    # Process Yearly User File
    update_yearly_user_file(daily_filename, yearly_user_file)

    # Delete the daily file after processing
    try:
        os.remove(daily_filename)
        print(f"Deleted daily file after processing: {daily_filename}")
    except Exception as e:
        print(f"Error deleting daily file {daily_filename}: {e}")

def update_yearly_project_file(daily_filename, yearly_project_file):
    """
    Updates the yearly project file with data from the daily CSV.
    """
    # Read existing yearly project data
    project_data = {}
    if os.path.exists(yearly_project_file):
        with open(yearly_project_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader, None)  # Skip header
            for row in reader:
                if len(row) < 2:
                    continue  # Skip malformed rows
                project_name = row[0]
                try:
                    time_spent = float(row[1])
                except ValueError:
                    time_spent = 0.0
                project_data[project_name] = time_spent

    # Read daily CSV data and update project_data
    with open(daily_filename, 'r', newline='', encoding='utf-8') as daily_csv:
        reader = csv.DictReader(daily_csv)
        for row in reader:
            project_name = row.get('Project')
            try:
                time_spent = float(row.get('Time Spent on Project (seconds)', 0))
            except ValueError:
                time_spent = 0.0
            if project_name and project_name != "Unknown":
                if project_name in project_data:
                    project_data[project_name] += time_spent
                else:
                    project_data[project_name] = time_spent

    # Write updated data back to the yearly project file
    with open(yearly_project_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Project Name', 'Time Spent (seconds)'])
        for project_name, time_spent in sorted(project_data.items()):
            writer.writerow([project_name, time_spent])

def update_yearly_user_file(daily_filename, yearly_user_file):
    """
    Updates the yearly user file with data from the daily CSV,
    recording each file worked on within each hour.
    """
    # Check if the yearly user file exists
    file_exists = os.path.exists(yearly_user_file)
    with open(yearly_user_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header if file does not exist
        if not file_exists:
            writer.writerow(['Date and Hour', 'File Worked On', 'Time Spent on File (seconds)', 'App Used'])

        # Read daily CSV data and append to yearly user file
        with open(daily_filename, 'r', newline='', encoding='utf-8') as daily_csv:
            reader = csv.DictReader(daily_csv)
            for row in reader:
                date_and_hour = row.get('Date and Hour')
                file_worked_on = row.get('File')
                time_spent = row.get('Time Spent on File (seconds)')
                app_used = row.get('App Used')
                writer.writerow([date_and_hour, file_worked_on, time_spent, app_used])
