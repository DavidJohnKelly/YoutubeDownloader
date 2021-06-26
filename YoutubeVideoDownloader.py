import os
import shutil
import zipfile
from datetime import date
from datetime import datetime

import pafy
from youtube_dl import YoutubeDL

# Getting the location of the py file and creating the initial directory to store the downloads
path = os.path.dirname(os.path.realpath('YoutubeVideoDownloader.py'))
try:
    os.mkdir(path + "\\Download\\")
except:
    print("")

dir_path = path + "\\Download\\" + str(date.today()) + "_" + str(datetime.now().strftime("%H-%M-%S"))
os.mkdir(dir_path)

url = input("Enter the playlist or video URL: ")
file_extension = ""
file_valid = False
while not file_valid:
    file_type = input("Enter 1 for video and 2 for only audio: ")
    if file_type == "1":

        valid = False
        while not valid:
            extension = input("Enter the required file extension (MP4, MOV, AVI, MKV, WMV, WEBM): ").lower()
            if extension == "mp4" or extension == "mov" or extension == "avi" or extension == "mkv" or extension == "wmv" or extension == "webm":
                file_extension = extension
                valid = True
            else:
                print("Enter a valid extension")
        file_valid = True

    elif file_type == "2":

        valid = False
        while not valid:
            extension = input("Enter the required file extension (MP3, WAV, AAC, OGG, WMA, FLAC, M4A): ").lower()
            if extension == "mp3" or extension == "wav" or extension == "aac" or extension == "ogg" or extension == "wma" or extension == "flac" or extension == "m4a":
                file_extension = extension
                valid = True
            else:
                print("Enter a valid extension")
        file_valid = True

    else:
        print("Enter a valid type")

zipbool = input("Enter 1 to zip the files, anything else to leave files in a folder: ")


def filetypechange():
    for count, filename in enumerate(os.listdir(dir_path)):
        # Gets the original file path
        src = dir_path + "\\" + filename
        # Gets the name of the file without the old extension and appends the new extension
        dst = os.path.splitext(src)[0] + "." + file_extension
        os.rename(src, dst)


# Checks for difference between playlist url and video url
if "/playlist?" in url:

    # Using YoutubeDL to get url of each video in playlist due to unfixed issues with pafy get_playlist and get_playlist2 methods
    playlist = YoutubeDL().extract_info(url, download=False)
    print(playlist["title"])
    print("")
    # Downloads each video with pafy
    for item in playlist["entries"]:
        print(item["title"])
        url_item = item["webpage_url"]
        print(url_item)
        try:
            src = pafy.new(url_item)
            if file_type == "1":
                video = src.getbest()
                video.download(filepath=dir_path)
            elif file_type == "2":
                audio = src.getbestaudio()
                audio.download(filepath=dir_path)
            else:
                print("Invalid input")
            print("")
        except Exception as e:
            print("Couldn't download " + item["title"])
            print(e)

else:

    # Downloads the video with pafy
    src = pafy.new(url)
    print(src.title)
    if file_type == "1":
        video = src.getbest()
        video.download(filepath=dir_path)
    elif file_type == "2":
        audio = src.getbestaudio()
        audio.download(filepath=dir_path)
    else:
        print("Invalid input")

# Changes all other file types to the specified file type
filetypechange()


def filezip():
    # Zips up the directory and deletes the original directory
    zip_path = dir_path + ".zip"
    contents = os.walk(dir_path)
    zip_file = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    for root, folders, files in contents:
        for file_name in files:
            absolute_path = os.path.join(root, file_name)
            relative_path = absolute_path.replace(dir_path + '\\', '')
            print("Adding '%s' to archive." % absolute_path)
            zip_file.write(absolute_path, relative_path)
    print("'%s' created successfully." % zip_path)
    zip_file.close()
    # Deletes the original folder
    shutil.rmtree(dir_path)


if zipbool == "1":
    filezip()
