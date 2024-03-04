import os
import shutil
import zipfile
from datetime import date
from datetime import datetime

from pytubefix import YouTube
from pytubefix import Playlist
from pytubefix import Channel


def filetypechange(dir_path, file_extension):
    for count, filename in enumerate(os.listdir(dir_path)):
        # Gets the original file path
        src = dir_path + "\\" + filename
        # Gets the name of the file without the old extension and appends the new extension
        dst = os.path.splitext(src)[0] + "." + file_extension
        os.rename(src, dst)


# zips up all files within the download folder, and deletes the original directory
def filezip(dir_path):
    zip_path = dir_path + ".zip"
    contents = os.walk(dir_path)
    zip_file = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    # Simply looping through all files in the folder and adding it to the zip file
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


# Getting the location of the py file and getting, or creating, the initial directory to store the downloads
def get_download_folder(path) -> str:
    try:
        if not os.path.exists(path + "\\Download\\"):
            os.mkdir(path + "\\Download\\")
        dir_path = path + "\\Download\\" + str(date.today()) + "_" + str(datetime.now().strftime("%H-%M-%S"))
        os.mkdir(dir_path)
        return dir_path
    except:
        print("ERROR! Couldn't make download folder. Aborting.")
        exit(-1)


def get_valid_file_extension(*extensions) -> str:
    extension_str = ', '.join(extensions)
    while True:
        extension = input(f"Enter the required file extension: ({extension_str}): ").lower()
        if extension in extensions:
            return extension
        else:
            print(f"Enter a valid extension from: ({extension_str})")


class FileType:
    Video = 1
    Audio = 2

def get_file_type() -> FileType:
    while True:
        file_type = input("Enter 1 for video and 2 for only audio: ")
        if file_type == '1':
            return FileType.Video
        elif file_type == '2':
            return FileType.Audio
        else:
            print("Enter a valid type")


def get_zip_bool() -> bool:
    zip_str = input("Enter 1 to zip the files, anything else to leave files in a folder: ")
    if zip_str == '1':
        return True
    else:
        return False


def get_audio_stream(yt, target_extension):
    stream = yt.streams.get_audio_only(target_extension)
    if stream:
        return stream
    else:
        print(f"No {target_extension} streams available. Choosing the next best option.")
        return yt.streams.get_audio_only()


def get_video_stream(yt, target_extension):
    streams = yt.streams.filter(file_extension=target_extension, progressive=True)
    if streams:
        return streams.get_highest_resolution()
    else:
        print(f"No {target_extension} streams available. Choosing the next best option.")
        streams = yt.streams.filter(progressive=True)
        return streams.get_highest_resolution()


def download_single(url, file_type, target_extension, dir_path):
    yt = YouTube(url)
    print(f"Downloading: {yt.title}")

    stream = None
    if file_type == FileType.Video:
        stream = get_video_stream(yt, target_extension)
    elif file_type == FileType.Audio:
        stream = get_audio_stream(yt, target_extension)

    try:
        stream.download(output_path=dir_path)
        print(f"{yt.title} downloaded successfully")
    except Exception as e:
        print(f"{yt.title} was not downloaded")
        print(e)


def download_channel(url, file_type, target_extension, dir_path):
    channel = Channel(url)
    print(f'Downloading videos by: {channel.channel_name}')
    for url in channel.video_urls:
        print(url)
        download_single(url, file_type, target_extension, dir_path)


def download_playlist(playlist_url, file_type, target_extension, dir_path):
    playlist = Playlist(playlist_url)
    print(f"Downloading videos from {playlist.title}")
    for url in playlist.video_urls:
        download_single(url, file_type, target_extension, dir_path)


def main():
    path = os.path.dirname(os.path.realpath('YoutubeVideoDownloader.py'))
    dir_path = get_download_folder(path)

    url = input("Enter the playlist, channel, or video URL: ")
    file_type = get_file_type()
        
    file_extension = ""
    if file_type == FileType.Video:
            file_extension = get_valid_file_extension('mp4', 'mov', 'avi', 'mkv', 'wmv', 'webm')
    elif file_type == FileType.Audio:
            file_extension = get_valid_file_extension('mp3', 'wav', 'aac', 'ogg', 'wma', 'flac', 'm4a')

    zip_bool = get_zip_bool()

    # Checks for difference between playlist, channel and video url
    if '/playlist?' in url:
        download_playlist(url, file_type, file_extension, dir_path)
    elif '/channel/' in url or '/@' in url:
        download_channel(url, file_type, file_extension, dir_path)
    else:
        download_single(url, file_type, file_extension, dir_path)
        
    # Changes all other file types to the specified file type
    filetypechange(dir_path, file_extension)
    
    if zip_bool:
        filezip(dir_path)


if __name__ == '__main__':
    main()