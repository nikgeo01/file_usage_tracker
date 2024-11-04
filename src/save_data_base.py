
#for each line in files_time.txt, split the line by ":" and add the time to the files_open_times dictionary
#example of files_time.txt:
#Task Switching:0:00:00.820582
#get_active_file.py - file_usage_tracker - Visual Studio Code:0:00:04.075647
#Task Switching:0:00:07.607162
#files_time.txt - file_usage_tracker - Visual Studio Code:0:00:02.937231
#AutoCAD Civil 3D 2010:0:00:03.732702
#Search:0:00:01.892151
#Search:0:00:00.894992
#Search:0:00:02.403592
#AutoCAD 2010:0:00:00.688210
#AutoCAD 2010:0:00:00.699990
#AutoCAD 2010:0:00:00.679117
#AutoCAD 2010 - [Drawing1.dwg]:0:00:00.771824
#AutoCAD 2010 - [Drawing1.dwg]:0:00:00.753460
#AutoCAD 2010 - [Drawing1.dwg]:0:00:01.642322
#AutoCAD Civil 3D 2010 - [Drawing1.dwg]:0:00:00.832593
#AutoCAD Civil 3D 2010 - [Drawing1.dwg]:0:00:00.899663
#AutoCAD Civil 3D 2010 - [Drawing1.dwg]:0:00:01.040921
#AutoCAD Civil 3D 2010 - [Drawing1.dwg]:0:00:08.833273
#AutoCAD Civil 3D 2010 - [Drawing1.dwg]:0:00:02.027376

#open the file files_time.txt
#read the file
#split the line by ":"
#add the time to the files_open_times dictionary
#close the file
#return the files_open_times dictionary

def read_new_data_file():
    files_open_times = {}
    with open("files_time.txt", "r") as file:
        for line in file:
            line = line.split(":")
            if line[0] in files_open_times:
                files_open_times[line[0]] += line[1]
            else:
                files_open_times[line[0]] = line[1]
    file.close
    print(files_open_times)
    return files_open_times

def save_new_data_to_base():
    new_data = read_new_data_file()
    
    with open("data_base.txt"