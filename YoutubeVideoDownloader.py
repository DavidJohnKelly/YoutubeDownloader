import os
import shutil
import zipfile
from datetime import date
from datetime import datetime
from pathlib import Path
from threading import Thread

import requests
from pytube import Playlist
from pytube import YouTube
from pytube.cli import on_progress


def validURL(url):
    pattern = '"playabilityStatus":{"status":"ERROR","reason":"Video unavailable"'
    request = requests.get(url)
    if pattern in request.text or "youtube.com/" not in url:
        return False
    return True


def getURL():
    url = ""
    urlValid = False
    while not urlValid:
        url = input("Enter the playlist or video URL: ")
        if (validURL(url)):
            urlValid = True
        else:
            print("Please enter a valid URL")
    return url


def getFileType():
    fileType = ""
    intType = 0
    typeValid = False
    while not typeValid:
        fileType = input("Enter 1 for video and 2 for only audio: ")
        try:
            intType = int(fileType)
            if intType == 1 or intType == 2:
                typeValid = True
            else:
                print("Enter a valid file type")
        except:
            print("Enter a valid file type")
    return intType


def getVideoFileExtension():
    fileExtension = ""
    extensionValid = False
    while not extensionValid:
        fileExtension = input("Enter required file extension: ")
        if fileExtension == "mp4" or fileExtension == "mov" or fileExtension == "avi" or fileExtension == "mkv" or fileExtension == "wmv" or fileExtension == "webm":
            extensionValid = True
        else:
            print("Enter a valid file extension")
    return fileExtension


def getAudioFileExtension():
    fileExtension = ""
    extensionValid = False
    while not extensionValid:
        fileExtension = input("Enter required file extension: ")
        if fileExtension == "mp3" or fileExtension == "wav" or fileExtension == "aac" or fileExtension == "ogg" or fileExtension == "wma" or fileExtension == "flac" or fileExtension == "m4a":
            extensionValid = True
        else:
            print("Enter a valid file extension")
    return fileExtension


def getFileExtension(fileType):
    fileExtension = ""
    if fileType == 1:
        fileExtension = getVideoFileExtension()
    elif fileType == 2:
        fileExtension = getAudioFileExtension()
    return fileExtension.lower()


def getDownloadFolder():
    basePath = os.path.dirname(os.path.realpath('YoutubeVideoDownloader.py'))
    downloadPath = basePath + "\\Download\\"
    if not os.path.exists(downloadPath):
        os.mkdir(downloadPath)
    return downloadPath


def makeCurrentDownloadFolder(downloadPath):
    # Getting the location of the py file and creating the initial directory to store the downloads
    directoryTime = str(date.today()) + "_" + str(datetime.now().strftime("%H-%M-%S"))
    dir_path = downloadPath + directoryTime
    os.mkdir(dir_path)
    return dir_path


def filezip(dir_path):
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


def getZipBool():
    zipbool = input("Enter 1 to zip the files, anything else to leave files in a folder: ")
    if zipbool == "1":
        return True
    return False


def getPlaylistBool(url):
    if "/playlist?" in url:
        return True
    return False


def getValidPlaylistStart(playlistLength):
    start = ""
    intStart = 0
    startValid = False
    while not startValid:
        start = input("Enter a playlist lower bound (Leave empty for no lower bound, or enter a negative number to count backwards from the end): ")
        if start == "":
            return 1  
        try:
            intStart = int(start)
            if intStart < 0 and (intStart * -1) <= playlistLength:
                return playlistLength + intStart
            elif intStart <= playlistLength and intStart > 0:
                startValid = True
            else:
                print("Enter a valid playlist lower bound")
        except:
            print("Enter a valid playlist lower bound")
    return intStart


def getValidPlaylistEnd(playlistLength, playlistStart):
    end = ""
    intEnd = 0
    endValid = False
    while not endValid:
        end = input("Enter a playlist upper bound (Leave empty for no upper bound): ")
        if end == "":
            return playlistLength
        try:
            intEnd = int(end)
            if intEnd <= playlistLength and intEnd >= playlistStart:
                endValid = True
            else:
                print("Enter a valid playlist upper bound")
        except:
            print("Enter a valid playlist upper bound")
    return intEnd


def getPlaylistRange(playlist):
    playlistLength = len(playlist)
    playlistStart = getValidPlaylistStart(playlistLength)
    playlistEnd = getValidPlaylistEnd(playlistLength, playlistStart)
    return [playlistStart, playlistEnd]


def fileTypeChange(filepath, file_extension):
    p = Path(filepath)
    p.rename(p.with_suffix(f".{file_extension}"))


def printDownloading(video, youtube):
    try:
        print(f"Downloading {youtube.title}")
    except:
        print(f"Downloading {video.title().lower()}")


def downloadVideoFormat(video, extension, downloadPath):
    youtube = YouTube(video, on_progress_callback=on_progress)
    printDownloading(video, youtube)
    try:
        stream = youtube.streams.filter(file_extension=extension)
        filePath = stream.get_highest_resolution().download(downloadPath)
    except:
        print("Couldn't download the requested format")
        print("Attempting automated conversion")
        stream = youtube.streams.get_highest_resolution()
        filePath = stream.download(downloadPath)
        fileTypeChange(filePath, extension)


def downloadAudioFormat(video, extension, downloadPath):
    youtube = YouTube(video, on_progress_callback=on_progress)
    printDownloading(video, youtube)
    try:
        stream = youtube.streams.get_audio_only(extension)
        filePath = stream.download(downloadPath)
    except:
        print("Couldn't download the requested format")
        print("Attempting automated conversion")
        stream = youtube.streams.get_audio_only()
        filePath = stream.download(downloadPath)
        fileTypeChange(filePath, extension)


def downloadPlaylist(playlist, downloadPath):
    playlistRange = getPlaylistRange(playlist)
    playlistStart = playlistRange[0] - 1
    playlistEnd = playlistRange[1] - 1
    fileType = getFileType()
    fileExtension = getFileExtension(fileType)
    threads = []
    if fileType == 1:
        if playlistStart == playlistEnd:
            video = playlist[playlistStart]
            downloadVideoFormat(video, fileExtension, downloadPath)
        for x in range(playlistStart, playlistEnd + 1):
            video = playlist[x]
            thread = Thread(target=downloadVideoFormat, args=(video, fileExtension, downloadPath))
            thread.start()
            threads.append(thread)
    elif fileType == 2:
        if playlistStart == playlistEnd:
            video = playlist[playlistStart]
            downloadAudioFormat(video, fileExtension, downloadPath)

        for x in range(playlistStart, playlistEnd + 1):
            video = playlist[x]
            thread = Thread(target=downloadAudioFormat, args=(video, fileExtension, downloadPath))
            thread.start()
            threads.append(thread)

    for thread in threads:
        thread.join()



def downloadVideo(video, downloadPath):
    fileType = getFileType()
    fileExtension = getFileExtension(fileType)
    if fileType == 1:
        downloadVideoFormat(video, fileExtension, downloadPath)
    elif fileType == 2:
        downloadAudioFormat(video, fileExtension, downloadPath)


def main():
    downloadPath = getDownloadFolder()
    currentDownloadPath = makeCurrentDownloadFolder(downloadPath)
    url = getURL()
    playlistBool = getPlaylistBool(url)
    zipBool = getZipBool()
    if playlistBool:
        playlist = Playlist(url)
        downloadPlaylist(playlist, currentDownloadPath)
    else:
        downloadVideo(url, currentDownloadPath)

    if zipBool:
        filezip(currentDownloadPath)


if __name__ == "__main__":
    main()
