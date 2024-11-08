from datetime import datetime
import os

def get_current_hour_filename():
    """Returns the filename for the current hour's CSV, rounded to the hour."""
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    return now.strftime('%H-00_%d_%m_%Y.csv')

def get_daily_filename():
    """Returns the filename for the daily CSV file."""
    user_name = os.getlogin()
    now = datetime.now()
    return f"{user_name}_{now.strftime('%d_%m_%Y')}.csv"
