
def save_last_data(data):
    #append the data to the file
    with open("files_time.txt", "a") as file:
        file.write(data)
        file.write("\n")
    