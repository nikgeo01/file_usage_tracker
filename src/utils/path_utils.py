# src/utils/path_utils.py

import os
from datetime import datetime

# Configuration variable for yearly files path
YEARLY_FILES_PATH = None  # Default is None, can be set manually

def set_yearly_files_path(path):
    """Allows manual setting of the yearly files path."""
    global YEARLY_FILES_PATH
    YEARLY_FILES_PATH = path

def get_current_hour_filename():
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    return now.strftime('%H-00_%d_%m_%Y.csv')

def get_daily_filename():
    user_name = os.getlogin()
    now = datetime.now()
    return f"{user_name}_{now.strftime('%d_%m_%Y')}.csv"

def get_yearly_project_filename(current_year):
    """Returns the filename for the yearly project CSV file."""
    if YEARLY_FILES_PATH:
        yearly_directory = YEARLY_FILES_PATH
    else:
        yearly_directory = os.path.join(os.getcwd(), 'yearly_reports')
    os.makedirs(yearly_directory, exist_ok=True)
    return os.path.join(yearly_directory, f"{current_year}-projects.csv")

def get_yearly_user_filename(current_year):
    """Returns the filename for the yearly user CSV file."""
    if YEARLY_FILES_PATH:
        yearly_directory = YEARLY_FILES_PATH
    else:
        yearly_directory = os.path.join(os.getcwd(), 'yearly_reports')
    os.makedirs(yearly_directory, exist_ok=True)
    user_name = os.getlogin()
    return os.path.join(yearly_directory, f"{current_year}-{user_name}.csv")
