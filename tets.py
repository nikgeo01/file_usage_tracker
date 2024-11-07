import psutil

# Replace 'process_name' with the name of the 3rd party app's process
process_id = "123"
for proc in psutil.process_iter(['pid', 'name']):
    if proc.info['pid'] == process_id:
        # Access all open files
        open_files = proc.open_files()
        print(f"Open files for {proc.info['name']} (PID {proc.info['pid']}):")
        for file in open_files:
            print(file.path)
