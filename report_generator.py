import os
import csv
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from datetime import datetime

def generate_project_report(yearly_reports_path, project_name, output_file):
    """
    Generates a CSV report showing the total time each user spent on a specified project,
    along with the total time spent on the project by all users.
    """
    user_time_spent = {}

    # Iterate over all yearly user files
    for filename in os.listdir(yearly_reports_path):
        if filename.endswith('.csv') and '-' in filename and not filename.endswith('-projects.csv'):
            # Extract the username from the filename
            parts = filename.split('-')
            if len(parts) >= 2:
                user_name_with_extension = parts[1]
                user_name = user_name_with_extension.replace('.csv', '')
                user_file = os.path.join(yearly_reports_path, filename)
                try:
                    with open(user_file, 'r', newline='', encoding='utf-8') as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            if row.get('Project Name') == project_name:
                                time_spent_str = row.get('Time Spent on File (seconds)', '0')
                                try:
                                    time_spent = float(time_spent_str)
                                except ValueError:
                                    time_spent = 0.0
                                if user_name in user_time_spent:
                                    user_time_spent[user_name] += time_spent
                                else:
                                    user_time_spent[user_name] = time_spent
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to read {user_file}.\nError: {e}")

    if not user_time_spent:
        messagebox.showinfo("No Data", f"No data found for project '{project_name}'.")
        return

    # Calculate the total time spent on the project by all users
    total_time_spent = sum(user_time_spent.values())

    # Write the report to a CSV file
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'User Name',
                'Total Time Spent on Project (seconds)',
                'Total Time Spent by All Users (seconds)'
            ]
            writer = csv.writer(csvfile)
            writer.writerow(fieldnames)
            for user_name, user_time in user_time_spent.items():
                writer.writerow([user_name, user_time, total_time_spent])

            # Add a total row at the end
            writer.writerow(['Total', total_time_spent, total_time_spent])
        messagebox.showinfo("Success", f"Project report generated successfully at:\n{output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write the project report.\nError: {e}")

def generate_user_activity_report(yearly_reports_path, user_name, start_date, end_date, output_file):
    """
    Generates a CSV report listing all files a user has worked on within a specified time period,
    aggregating data from all years.
    """
    activity_data = []

    # Find all yearly user files for the specified user
    for filename in os.listdir(yearly_reports_path):
        if filename.endswith(f'-{user_name}.csv'):
            user_file = os.path.join(yearly_reports_path, filename)
            try:
                with open(user_file, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        date_and_hour = row.get('Date and Hour')
                        if date_and_hour:
                            try:
                                entry_date = datetime.strptime(date_and_hour, '%Y-%m-%d %H:%M')
                                if start_date <= entry_date <= end_date:
                                    activity_data.append({
                                        'Date and Hour': date_and_hour,
                                        'File Worked On': row.get('File Worked On', '-'),
                                        'Time Spent on File (seconds)': row.get('Time Spent on File (seconds)', '0'),
                                        'App Used': row.get('App Used', 'Unknown'),
                                        'Project Name': row.get('Project Name', '-')
                                    })
                            except ValueError:
                                # Skip rows with invalid date formats
                                print(f"Skipping row with invalid date format: {date_and_hour}")
                                continue
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read {user_file}.\nError: {e}")

    # Write the report to a CSV file
    if activity_data:
        # Sort the activity data by date
        activity_data.sort(key=lambda x: datetime.strptime(x['Date and Hour'], '%Y-%m-%d %H:%M'))
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Date and Hour', 'File Worked On', 'Time Spent on File (seconds)', 'App Used', 'Project Name']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(activity_data)
            messagebox.showinfo("Success", f"User activity report generated successfully at:\n{output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to write the user activity report.\nError: {e}")
    else:
        messagebox.showinfo("No Data", f"No activity found for user '{user_name}' in the specified time period.")

def create_gui():
    root = tk.Tk()
    root.title("Report Generator")
    root.geometry("600x500")
    root.resizable(False, False)

    # Set the theme
    style = ttk.Style(root)
    style.theme_use('clam')  # You can choose 'default', 'clam', 'alt', 'classic'

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both', padx=10, pady=10)

    # Project Report Tab
    project_tab = ttk.Frame(notebook)
    notebook.add(project_tab, text='Project Report')

    # Project Report Frame
    project_frame = ttk.Frame(project_tab, padding="10 10 10 10")
    project_frame.pack(fill='both', expand=True)

    # Layout for Project Report
    project_grid = [
        ("Project Name:", "project_name_entry"),
        ("Yearly Reports Folder:", "project_folder_entry", "Browse", "browse_project_folder"),
        ("Output CSV File:", "project_output_entry", "Browse", "browse_project_output")
    ]

    for idx, item in enumerate(project_grid):
        ttk.Label(project_frame, text=item[0]).grid(row=idx, column=0, sticky='W', pady=5)
        entry = ttk.Entry(project_frame, width=50)
        entry.grid(row=idx, column=1, pady=5, padx=5)
        if len(item) > 2:
            button = ttk.Button(project_frame, text=item[2], command=lambda e=entry, cmd=item[3]: globals()[cmd](e))
            button.grid(row=idx, column=2, pady=5)
        globals()[item[1]] = entry

    ttk.Button(project_frame, text="Generate Report", command=lambda: run_project_report(
        project_folder_entry.get(),
        project_name_entry.get(),
        project_output_entry.get()
    )).grid(row=len(project_grid), column=1, pady=20)

    # User Activity Report Tab
    user_tab = ttk.Frame(notebook)
    notebook.add(user_tab, text='User Activity Report')

    # User Activity Frame
    user_frame = ttk.Frame(user_tab, padding="10 10 10 10")
    user_frame.pack(fill='both', expand=True)

    # Layout for User Activity Report
    user_grid = [
        ("User Name:", "user_name_entry"),
        ("Start Date (YYYY-MM-DD):", "start_date_entry"),
        ("End Date (YYYY-MM-DD):", "end_date_entry"),
        ("Yearly Reports Folder:", "user_folder_entry", "Browse", "browse_user_folder"),
        ("Output CSV File:", "user_output_entry", "Browse", "browse_user_output")
    ]

    for idx, item in enumerate(user_grid):
        ttk.Label(user_frame, text=item[0]).grid(row=idx, column=0, sticky='W', pady=5)
        entry = ttk.Entry(user_frame, width=50)
        entry.grid(row=idx, column=1, pady=5, padx=5)
        if len(item) > 2:
            button = ttk.Button(user_frame, text=item[2], command=lambda e=entry, cmd=item[3]: globals()[cmd](e))
            button.grid(row=idx, column=2, pady=5)
        globals()[item[1]] = entry

    ttk.Button(user_frame, text="Generate Report", command=lambda: run_user_activity_report(
        user_folder_entry.get(),
        user_name_entry.get(),
        start_date_entry.get(),
        end_date_entry.get(),
        user_output_entry.get()
    )).grid(row=len(user_grid), column=1, pady=20)

    root.mainloop()

def browse_project_folder(entry_widget):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder_selected)

def browse_project_output(entry_widget):
    file_selected = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
    if file_selected:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_selected)

def browse_user_folder(entry_widget):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, folder_selected)

def browse_user_output(entry_widget):
    file_selected = filedialog.asksaveasfilename(defaultextension=".csv",
                                                 filetypes=[("CSV files", "*.csv")])
    if file_selected:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, file_selected)

def run_project_report(yearly_reports_path, project_name, output_file):
    if not yearly_reports_path or not project_name or not output_file:
        tk.messagebox.showwarning("Input Error", "Please fill in all fields for the Project Report.")
        return

    if not os.path.isdir(yearly_reports_path):
        tk.messagebox.showerror("Invalid Folder", f"The specified yearly reports folder does not exist:\n{yearly_reports_path}")
        return

    # Confirm overwriting if file exists
    if os.path.exists(output_file):
        overwrite = tk.messagebox.askyesno("Overwrite File", f"The file '{output_file}' already exists. Do you want to overwrite it?")
        if not overwrite:
            return

    generate_project_report(yearly_reports_path, project_name, output_file)

def run_user_activity_report(yearly_reports_path, user_name, start_date_str, end_date_str, output_file):
    if not yearly_reports_path or not user_name or not start_date_str or not end_date_str or not output_file:
        tk.messagebox.showwarning("Input Error", "Please fill in all fields for the User Activity Report.")
        return

    if not os.path.isdir(yearly_reports_path):
        tk.messagebox.showerror("Invalid Folder", f"The specified yearly reports folder does not exist:\n{yearly_reports_path}")
        return

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        # Adjust end_date to include the entire day
        end_date = end_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        tk.messagebox.showerror("Date Format Error", "Invalid date format. Please use YYYY-MM-DD.")
        return

    if start_date > end_date:
        tk.messagebox.showerror("Date Range Error", "Start date must be before or equal to end date.")
        return

    # Confirm overwriting if file exists
    if os.path.exists(output_file):
        overwrite = tk.messagebox.askyesno("Overwrite File", f"The file '{output_file}' already exists. Do you want to overwrite it?")
        if not overwrite:
            return

    generate_user_activity_report(yearly_reports_path, user_name, start_date, end_date, output_file)

if __name__ == "__main__":
    create_gui()
