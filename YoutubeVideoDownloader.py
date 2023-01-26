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

VIDEO_TYPE = 0
AUDIO_TYPE = 1
ZIP_BOOL = "1"
FILE_EXTENSIONS = [["mp4", "mov", "avi", "mkv", "wmv", "webm"], ["mp3", "wav", "aac", "ogg", "wma", "flac", "m4a"]]


def valid_url(url):
    try:
        request = requests.get(url)
        pattern = '"playabilityStatus":{"status":"ERROR","reason":"Video unavailable"'
        if "youtube.com/" in url and pattern not in request.text:
            return True
    except Exception as e:
        print(e)
    return False


def get_url():
    url = ""
    url_valid = False
    while not url_valid:
        url = input("Enter the playlist or video URL: ")
        if valid_url(url):
            url_valid = True
        else:
            print("Please enter a valid URL")
    return url


def get_file_type():
    int_type = 0
    type_valid = False
    while not type_valid:
        file_type = input(f"Enter {VIDEO_TYPE} for video and {AUDIO_TYPE} for only audio: ")
        try:
            int_type = int(file_type)
            if int_type == VIDEO_TYPE or int_type == AUDIO_TYPE:
                type_valid = True
            else:
                print("Enter a valid file type")
        except ValueError:
            print("Enter a valid file type")
    return int_type


def get_file_extension(file_type):
    file_extension = ""
    extension_valid = False
    while not extension_valid:
        file_extension = input("Enter required file extension: ")
        if file_type == VIDEO_TYPE and file_extension in FILE_EXTENSIONS[VIDEO_TYPE]:
            extension_valid = True
        elif file_type == AUDIO_TYPE and file_extension in FILE_EXTENSIONS[AUDIO_TYPE]:
            extension_valid = True
        else:
            print("Enter a valid file extension")
    return file_extension.lower()


def get_download_folder():
    base_path = os.path.dirname(os.path.realpath('YoutubeVideoDownloader.py'))
    download_path = base_path + "\\Download\\"
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    return download_path


def make_current_download_folder(download_path):
    # Getting the location of the py file and creating the initial directory to store the downloads
    directory_time = str(date.today()) + "_" + str(datetime.now().strftime("%H-%M-%S"))
    dir_path = download_path + directory_time
    os.mkdir(dir_path)
    return dir_path


def zip_folder(directory_path):
    # Zips up the directory and deletes the original directory
    zip_path = directory_path + ".zip"
    contents = os.walk(directory_path)
    zip_file = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    for root, folders, files in contents:
        for file_name in files:
            absolute_path = os.path.join(root, file_name)
            relative_path = absolute_path.replace(directory_path + '\\', '')
            print(f"Adding {absolute_path} to archive.")
            zip_file.write(absolute_path, relative_path)
    print(f"{zip_path} created successfully.")
    zip_file.close()
    # Deletes the original folder
    shutil.rmtree(directory_path)


def get_zip_bool():
    zip_bool = input("Enter 1 to zip the files, anything else to leave files in a folder: ")
    if zip_bool == ZIP_BOOL:
        return True
    return False


def get_playlist_bool(url):
    if "/playlist?" in url:
        return True
    return False


def get_playlist_start(playlist_length):
    int_start = 0
    start_valid = False
    while not start_valid:
        start = input(
            "Enter a playlist lower bound (Leave empty for no lower bound, or enter a negative number to count "
            "backwards from the end): "
        )
        if start == "":
            return 0
        try:
            int_start = int(start)
            if int_start < 0 and abs(int_start) <= playlist_length:
                return playlist_length + int_start + 1
            elif playlist_length >= int_start > 0:
                start_valid = True
            else:
                print("Enter a valid playlist lower bound")
        except ValueError:
            print("Enter a valid playlist lower bound")
    return int_start - 1


def get_playlist_end(playlist_length, playlist_start):
    int_end = 0
    end_valid = False
    while not end_valid:
        end = input("Enter a playlist upper bound (Leave empty for no upper bound): ")
        if end == "":
            return playlist_length
        try:
            int_end = int(end)
            if playlist_length >= int_end >= playlist_start:
                end_valid = True
            else:
                print("Enter a valid playlist upper bound")
        except ValueError:
            print("Enter a valid playlist upper bound")
    return int_end


def change_file_type(file_path, file_extension):
    p = Path(file_path)
    p.rename(p.with_suffix(f".{file_extension}"))


def print_downloading(video, youtube):
    try:
        print(f"Downloading {youtube.title}")
    except Exception as e:
        print(e)
        print(f"Downloading {video.title().lower()}")


def download_with_extension(youtube, file_type, extension, download_path):
    if file_type == VIDEO_TYPE:
        stream = youtube.streams.filter(file_extension=extension)
        stream.get_highest_resolution().download(download_path)
    elif file_type == AUDIO_TYPE:
        stream = youtube.streams.get_audio_only(extension)
        stream.download(download_path)


def download_without_extension(youtube, file_type, download_path):
    print("Couldn't download the requested format")
    print("Attempting automated conversion")
    file_path = ""
    if file_type == VIDEO_TYPE:
        stream = youtube.streams.get_highest_resolution()
        file_path = stream.download(download_path)
    elif file_type == AUDIO_TYPE:
        stream = youtube.streams.get_audio_only()
        file_path = stream.download(download_path)
    return file_path


def download(video, extension, download_path, file_type):
    youtube = YouTube(video, on_progress_callback=on_progress)
    print_downloading(video, youtube)
    try:
        download_with_extension(youtube, file_type, extension, download_path)
    except AttributeError:
        file_path = download_without_extension(youtube, file_type, download_path)
        change_file_type(file_path, extension)


def download_playlist(playlist, download_path):
    playlist_length = len(playlist)
    playlist_start = get_playlist_start(playlist_length)
    playlist_end = get_playlist_end(playlist_length, playlist_start)
    file_type = get_file_type()
    file_extension = get_file_extension(file_type)
    threads = []
    for x in range(playlist_start, playlist_end):
        video = playlist[x]
        thread = Thread(target=download, args=(video, file_extension, download_path, file_type))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


def download_single(video, download_path):
    file_type = get_file_type()
    file_extension = get_file_extension(file_type)
    download(video, file_extension, download_path, file_type)


def main():
    download_path = get_download_folder()
    current_download_path = make_current_download_folder(download_path)
    url = get_url()
    playlist_bool = get_playlist_bool(url)
    zip_bool = get_zip_bool()
    if playlist_bool:
        playlist = Playlist(url)
        download_playlist(playlist, current_download_path)
    else:
        download_single(url, current_download_path)

    if zip_bool:
        zip_folder(current_download_path)


if __name__ == "__main__":
    main()
