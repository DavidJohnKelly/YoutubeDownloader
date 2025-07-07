# config.py
from enum import Enum
from pathlib import Path

# Valid file extensions
VALID_VIDEO_FILE_TYPES = ('mp4', 'mov', 'avi', 'mkv', 'wmv', 'webm')
VALID_AUDIO_FILE_TYPES = ('mp3', 'wav', 'aac', 'ogg', 'wma', 'flac', 'm4a')

# Available video resolutions
AVAILABLE_RESOLUTIONS = ('144p', '240p', '360p', '480p', '720p', '1080p', '1440p', '2160p')

class FileType(Enum):
    VIDEO = 1
    AUDIO = 2

class DownloadConfig:
    def __init__(self):
        self.file_type: FileType = FileType.VIDEO
        self.file_extension: str = 'mp4'
        self.resolution: str = '720p'
        self.create_zip: bool = False
        self.download_path: Path = None