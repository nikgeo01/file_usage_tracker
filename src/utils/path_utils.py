# src/utils/path_utils.py

import os
from datetime import datetime
import re

# Configuration variable for yearly files path
YEARLY_FILES_PATH = None  # Default is None, can be set manually

def set_yearly_files_path(path):
    """Allows manual setting of the yearly files path."""
    global YEARLY_FILES_PATH
    YEARLY_FILES_PATH = path

def get_current_hour_filename():
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    return now.strftime('%H-00_%d_%m_%Y.csv')

def get_daily_filename(hourly_file_name):
    user_name = os.getlogin()
    #19-00_20_11_2024
    return f"{user_name}_{hourly_file_name[6:]}"

def get_yearly_project_filename(current_year):
    """Returns the filename for the yearly project CSV file."""
    if YEARLY_FILES_PATH:
        yearly_directory = YEARLY_FILES_PATH
    else:
        yearly_directory = os.path.join(os.getcwd(), 'yearly_reports')
    os.makedirs(yearly_directory, exist_ok=True)
    return os.path.join(yearly_directory, f"{current_year}-projects.csv")

def get_yearly_user_filename(current_year, user_name):
    """Returns the filename for the yearly user CSV file."""
    if YEARLY_FILES_PATH:
        yearly_directory = YEARLY_FILES_PATH
    else:
        yearly_directory = os.path.join(os.getcwd(), 'yearly_reports')
    os.makedirs(yearly_directory, exist_ok=True)
    return os.path.join(yearly_directory, f"{current_year}-{user_name}.csv")

def get_project_name(file_path):
    import logging
    logging.basicConfig(level=logging.DEBUG)

    file_path = file_path.strip()
    logging.debug(f"File Path after stripping: {repr(file_path)}")

    normalized_path = os.path.normpath(file_path)
    logging.debug(f"Normalized file path: {repr(normalized_path)}")
    directories = normalized_path.split(os.sep)
    logging.debug(f"Directories: {directories}")
    
    for directory in directories:
        directory = directory.strip()
        logging.debug(f"Processing directory: '{directory}'")
        match = re.match(r'^(\d{3,})-', directory)
        if match:
            project_name = match.group(1)
            logging.debug(f"Matched project name: {project_name}")
            return project_name
    logging.debug("No project name matched.")
    return '-'
