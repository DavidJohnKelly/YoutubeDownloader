import pafy
from youtube_dl import YoutubeDL
import os
import zipfile
import sys
from datetime import datetime
from datetime import date
import shutil


#Getting the location of the py file and creating the initial directory to store the downloads
path = os.path.dirname(os.path.realpath('YoutubeVideoDownloader.py'))
os.mkdir(path + "\\Download\\")
dir_path = path + "\\Download\\" + str(date.today()) +"_"+ str(datetime.now().strftime("%H-%M-%S"))
os.mkdir(dir_path)

url = input("Enter the playlist or video URL: ")
file_type = input("Enter 1 for video and 2 for only audio: ")

#Checks for difference between playlist url and video url
if "/playlist?" in url:

    #Using YoutubeDL to get url of each video in playlist due to unfixed issues with pafy get_playlist and get_playlist2 methods
    playlist = YoutubeDL().extract_info(url, download=False)
    print(playlist["title"])
    print("")
    #Downloads each video with pafy
    for item in playlist["entries"]:
        print(item["title"])
        src=pafy.new(item["webpage_url"])
        if file_type == "1":
            video = src.getbest()
            video.download(filepath = dir_path)
        elif file_type == "2":
            audio = src.getbestaudio()
            audio.download(filepath = dir_path)
        else:
            print("Invalid input")

        
else:
    #Downloads the video with pafy
    src=pafy.new(url)
    print(src.title)
    if file_type == "1":
        video = src.getbest()
        video.download(filepath = dir_path)
    elif file_type == "2":
        audio = src.getbestaudio()
        audio.download(filepath = dir_path)
    else:
        print("Invalid input")



#Zips up the directory and deletes the original directory
zip_path = dir_path + ".zip"
contents = os.walk(dir_path)
zip_file = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
for root, folders, files in contents:
    for file_name in files:
        absolute_path = os.path.join(root, file_name)
        relative_path = absolute_path.replace(dir_path + '\\','')
        print("Adding '%s' to archive." % absolute_path)
        zip_file.write(absolute_path, relative_path)
print("'%s' created successfully." % zip_path)
zip_file.close()
#Deletes the original folder
shutil.rmtree(dir_path)
