import shutil
import zipfile
from enum import Enum
from pathlib import Path
from datetime import date, datetime
from pytubefix import YouTube, Playlist, Channel


VALID_VIDEO_FILE_TYPES = 'mp4', 'mov', 'avi', 'mkv', 'wmv', 'webm'
VALID_AUDIO_FILE_TYPES = 'mp3', 'wav', 'aac', 'ogg', 'wma', 'flac', 'm4a'

# Enum for different file types
class FileType(Enum):
    VIDEO = 1
    AUDIO = 2
    

# Change all files of incorrect type to the specified type
def filetypechange(dir_path: Path, file_extension: str):
    for file in dir_path.iterdir():
        if file.is_file():
            new_file = file.with_suffix(f".{file_extension}")
            file.rename(new_file)

# zips up all files within the download folder, and deletes the original directory
def filezip(dir_path: Path):
    zip_path = dir_path.with_suffix('.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file in dir_path.rglob('*'):
            if file.is_file():
                relative_path = file.relative_to(dir_path)
                print(f"Adding {file} to archive.")
                zip_file.write(file, arcname=relative_path)
    print(f"{zip_path} created successfully.")
    # Deletes the original folder
    shutil.rmtree(dir_path)

# Getting the location of the py file and getting, or creating, the initial directory to store the downloads
def get_download_folder(base_path: Path) -> Path:
    try:
        download_dir = base_path / "Download"
        download_dir.mkdir(exist_ok=True)
        dir_path = download_dir / f"{date.today()}_{datetime.now().strftime('%H-%M-%S')}"
        dir_path.mkdir()
        return dir_path
    except Exception as e:
        print(f"ERROR! Couldn't make download folder. Aborting. {e}")
        exit(-1)

# Get a valid file extension from the user
def get_valid_file_extension(*extensions) -> str:
    extension_str = ', '.join(extensions)
    while True:
        extension = input(f"Enter the required file extension: ({extension_str}): ").lower()
        if extension in extensions:
            return extension
        else:
            print(f"Enter a valid extension from: ({extension_str})")

# Get a valid file type from the user
def get_file_type() -> FileType:
    while True:
        file_type = input("Enter 1 for video and 2 for only audio: ")
        if file_type == '1':
            return FileType.VIDEO
        elif file_type == '2':
            return FileType.AUDIO
        else:
            print("Enter a valid type")

# Get whether the user wants the files to be zipped up
def get_zip_bool() -> bool:
    return input("Enter 1 to zip the files, anything else to leave files in a folder: ") == '1'

# Get the highest quality audio stream available, of requested type if available
def get_audio_stream(yt, target_extension):
    stream = yt.streams.get_audio_only(target_extension)
    if stream:
        return stream
    else:
        print(f"No {target_extension} streams available. Choosing the next best option.")
        return yt.streams.get_audio_only()

# Get the highest quality video stream available that has embedded audio audio, of requested type if available
def get_video_stream(yt, target_extension):
    streams = yt.streams.filter(file_extension=target_extension, progressive=True)
    if streams:
        return streams.get_highest_resolution()
    else:
        print(f"No {target_extension} streams available. Choosing the next best option.")
        return yt.streams.filter(progressive=True).get_highest_resolution()

# Get the appropriate audio or video stream
def get_stream(yt, file_type, target_extension):
    stream = None
    if file_type == FileType.VIDEO:
        stream = get_video_stream(yt, target_extension)
    elif file_type == FileType.AUDIO:
        stream = get_audio_stream(yt, target_extension)
    return stream

# Download a single video from a specified url
def download_single(url, file_type, target_extension, dir_path: Path):
    yt = YouTube(url)
    print(f"Downloading: {yt.title}")
    stream = get_stream(yt, file_type, target_extension)
    if stream is not None:
        try:
            stream.download(output_path=str(dir_path))
            print(f"{yt.title} downloaded successfully")
        except Exception as e:
            print(f"{yt.title} was not downloaded")
            print(e)
    else:
        print(f"No suitable stream found for {yt.title}. Skipping download.")

# Download all videos from a given playlist
def download_playlist(playlist_url, file_type, target_extension, dir_path: Path):
    playlist = Playlist(playlist_url)
    print(f"Downloading videos from {playlist.title}")
    for url in playlist.video_urls:
        download_single(url, file_type, target_extension, dir_path)

# Download all videos from a given channel
def download_channel(url, file_type, target_extension, dir_path: Path):
    channel = Channel(url)
    print(f'Downloading videos by: {channel.channel_name}')
    # Check if all video urls available
    for url in channel.video_urls:
        print(url)
        download_single(url, file_type, target_extension, dir_path)
    for item in channel.home:
        if isinstance(item, Playlist):
            download_playlist(item.playlist_url, file_type, target_extension, dir_path)

def main():
    base_path = Path(__file__).resolve().parent
    dir_path = get_download_folder(base_path)

    url = input("Enter the playlist, channel, or video URL: ")
    file_type = get_file_type()

    if file_type == FileType.VIDEO:
        file_extension = get_valid_file_extension(*VALID_VIDEO_FILE_TYPES)
    else:
        file_extension = get_valid_file_extension(*VALID_AUDIO_FILE_TYPES)

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