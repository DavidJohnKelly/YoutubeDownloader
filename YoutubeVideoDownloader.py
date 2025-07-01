import shutil
import zipfile
from enum import Enum
from pathlib import Path
from datetime import date, datetime
from pytubefix import YouTube, Playlist, Channel
from tqdm import tqdm


VALID_VIDEO_FILE_TYPES = 'mp4', 'mov', 'avi', 'mkv', 'wmv', 'webm'
VALID_AUDIO_FILE_TYPES = 'mp3', 'wav', 'aac', 'ogg', 'wma', 'flac', 'm4a'

# Enum for different file types
class FileType(Enum):
    VIDEO = 1
    AUDIO = 2

progress_bar: tqdm | None = None

# Change all files of incorrect type to the specified type
def filetypechange(dir_path: Path, file_extension: str):
    for file in dir_path.iterdir():
        if file.is_file():
            new_file = file.with_suffix(f".{file_extension}")
            file.rename(new_file)

# zips up all files within the download folder, and deletes the original directory
def filezip(dir_path: Path):
    zip_path = dir_path.with_suffix('.zip')
    
    # Count total files for progress bar
    total_files = sum(1 for file in dir_path.rglob('*') if file.is_file())
    
    print_info(f"Creating ZIP archive: {zip_path.name}")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        with tqdm(total=total_files, desc="Archiving", unit="files") as pbar:
            for file in dir_path.rglob('*'):
                if file.is_file():
                    relative_path = file.relative_to(dir_path)
                    zip_file.write(file, arcname=relative_path)
                    pbar.update(1)
    
    print_success(f"Archive created: {zip_path}")
    print_info("Cleaning up temporary files...")
    shutil.rmtree(dir_path)
    print_success("Cleanup completed")

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
    print_section_header("SELECT FILE FORMAT")
    extension_str = ', '.join(extensions)
    print(f"Available formats: {extension_str}")

    while True:
        extension = input(f"\n📁 Enter desired file extension: ").lower().strip()
        if extension in extensions:
            print_success(f"Format '{extension}' selected")
            return extension
        else:
            print_error(f"Please enter a valid extension from: {extension_str}")


# Get a valid file type from the user
def get_file_type() -> FileType:
    print_section_header("SELECT DOWNLOAD TYPE")
    print("1️⃣  Video (with audio)")
    print("2️⃣  Audio only")
    
    while True:
        file_type = input("\n🎯 Enter your choice (1 or 2): ").strip()
        if file_type == '1':
            print_success("Video download selected")
            return FileType.VIDEO
        elif file_type == '2':
            print_success("Audio download selected")
            return FileType.AUDIO
        else:
            print_error("Please enter 1 or 2")

# Get whether the user wants the files to be zipped up
def get_zip_bool() -> bool:
    print_section_header("ARCHIVE OPTION")
    print("📦 Would you like to compress the downloaded files into a ZIP archive?")
    choice = input("Enter 1 for YES, anything else for NO: ").strip()
    
    if choice == '1':
        print_success("Files will be compressed into a ZIP archive")
        return True
    else:
        print_info("Files will be kept in a folder")
        return False

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
    global progress_bar
    try:
        yt = YouTube(url, on_progress_callback=progress_hook)
        
        # Display video info
        print(f"\n📹 Title: {yt.title}")
        print(f"👤 Author: {yt.author}")
        print(f"⏱️ Duration: {yt.length // 60}:{yt.length % 60:02d}")
        print(f"👀 Views: {yt.views:,}")
        
        stream = get_stream(yt, file_type, target_extension)
        if stream is not None:
            file_size = stream.filesize
            print(f"📦 File size: {file_size / (1024*1024):.1f} MB")
            print(f"🎯 Quality: {getattr(stream, 'resolution', 'Audio only')}")
            
            try:
                # Create progress bar
                progress_bar = tqdm(
                    total=file_size,
                    unit='B',
                    unit_scale=True,
                    desc="Downloading",
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
                )

                stream.download(output_path=str(dir_path))
                progress_bar.close()
                print_success(f"'{yt.title}' downloaded successfully!")
                return True
            except Exception as e:
                if progress_bar is not None:
                    progress_bar.close()

                print_error(f"Failed to download '{yt.title}': {str(e)}")
                return False
        else:
            print_error(f"No suitable stream found for '{yt.title}'. Skipping download.")
            return False
            
    except Exception as e:
        print_error(f"Error processing video: {str(e)}")
        return False

# Download all videos from a given playlist
def download_playlist(playlist_url, file_type, target_extension, dir_path: Path):
    try:
        playlist = Playlist(playlist_url)
        print_section_header(f"PLAYLIST: {playlist.title}")
        print_info(f"Total videos: {len(playlist.video_urls)}")
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, url in enumerate(playlist.video_urls, 1):
            print(f"\n[{i}/{len(playlist.video_urls)}] Processing video...")
            if download_single(url, file_type, target_extension, dir_path):
                successful_downloads += 1
            else:
                failed_downloads += 1
        
        # Summary
        print_section_header("PLAYLIST DOWNLOAD SUMMARY")
        print_success(f"Successfully downloaded: {successful_downloads} videos")
        if failed_downloads > 0:
            print_error(f"Failed downloads: {failed_downloads} videos")
            
    except Exception as e:
        print_error(f"Error processing playlist: {str(e)}")

# Download all videos from a given channel
def download_channel(url, file_type, target_extension, dir_path: Path):
    try:
        channel = Channel(url)
        print_section_header(f"CHANNEL: {channel.channel_name}")
        print_info(f"Subscriber count: {getattr(channel, 'subscriber_count', 'Unknown')}")
        
        video_urls = list(channel.video_urls)
        print_info(f"Total videos found: {len(video_urls)}")
        
        successful_downloads = 0
        failed_downloads = 0
        
        for i, video_url in enumerate(video_urls, 1):
            print(f"\n[{i}/{len(video_urls)}] Processing video...")
            if download_single(video_url, file_type, target_extension, dir_path):
                successful_downloads += 1
            else:
                failed_downloads += 1
        
        # Process playlists from channel home
        print_info("Checking for channel playlists...")
        for item in channel.home:
            if isinstance(item, Playlist):
                print_info(f"Found playlist: {item.title}")
                download_playlist(item.playlist_url, file_type, target_extension, dir_path)
        
        # Summary
        print_section_header("CHANNEL DOWNLOAD SUMMARY")
        print_success(f"Successfully downloaded: {successful_downloads} videos")
        if failed_downloads > 0:
            print_error(f"Failed downloads: {failed_downloads} videos")
            
    except Exception as e:
        print_error(f"Error processing channel: {str(e)}")

def print_ascii_title():
    """Display ASCII art title banner"""
    title = r"""
/==============================================================================================================\
||██╗   ██╗████████╗    ██████╗  ██████╗ ██╗    ██╗███╗   ██╗██╗      ██████╗  █████╗ ██████╗ ███████╗██████╗ ||
||╚██╗ ██╔╝╚══██╔══╝    ██╔══██╗██╔═══██╗██║    ██║████╗  ██║██║     ██╔═══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗||
|| ╚████╔╝    ██║       ██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║██║     ██║   ██║███████║██║  ██║█████╗  ██████╔╝||
||  ╚██╔╝     ██║       ██║  ██║██║   ██║██║███╗██║██║╚██╗██║██║     ██║   ██║██╔══██║██║  ██║██╔══╝  ██╔══██╗||
||   ██║      ██║       ██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║███████╗╚██████╔╝██║  ██║██████╔╝███████╗██║  ██║||
||   ╚═╝      ╚═╝       ╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝||
||                                           YouTube Video Downloader                                         ||
||                                                 Version 1.4                                                ||
\==============================================================================================================/
    """
    print(title)

def print_section_header(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_success(message: str):
    """Print success message with green color and checkmark"""
    print(f"✅ {message}")

def print_error(message: str):
    """Print error message with red color and X mark"""
    print(f"❌ {message}")

def print_info(message: str):
    """Print info message with blue color and info icon"""
    print(f"ℹ️  {message}")

def progress_hook(stream, chunk, bytes_remaining):
    """Progress hook for download progress bar"""
    if progress_bar is not None:
        # Update progress bar
        progress_bar.update(len(chunk))

def main():
    # Display ASCII title
    print_ascii_title()
    
    base_path = Path(__file__).resolve().parent
    dir_path = get_download_folder(base_path)

    print_section_header("ENTER DOWNLOAD URL")
    url = input("🔗 Enter the playlist, channel, or video URL: ").strip()
    
    file_type = get_file_type()

    if file_type == FileType.VIDEO:
        file_extension = get_valid_file_extension(*VALID_VIDEO_FILE_TYPES)
    else:
        file_extension = get_valid_file_extension(*VALID_AUDIO_FILE_TYPES)

    zip_bool = get_zip_bool()

    print_section_header("STARTING DOWNLOAD")
    
    # Determine download type and start
    if '/playlist?' in url:
        print_info("Playlist URL detected")
        download_playlist(url, file_type, file_extension, dir_path)
    elif '/channel/' in url or '/@' in url:
        print_info("Channel URL detected")
        download_channel(url, file_type, file_extension, dir_path)
    else:
        print_info("Single video URL detected")
        download_single(url, file_type, file_extension, dir_path)

    print_section_header("POST-PROCESSING")
    print_info("Converting file extensions...")
    filetypechange(dir_path, file_extension)
    print_success("File extension conversion completed")

    if zip_bool:
        filezip(dir_path)

    print_section_header("DOWNLOAD COMPLETE")
    print_success("All operations completed!")
    print(f"📁 Files location: {dir_path if not zip_bool else dir_path.with_suffix('.zip')}")

if __name__ == '__main__':
    main()