from pytubefix import YouTube
from pathlib import Path
from tqdm import tqdm
from config import FileType
from stream_handler import StreamHandler
from ui_handler import UIHandler

class VideoDownloader:
    def __init__(self):
        self.progress_bar: tqdm | None = None

    def progress_hook(self, stream, chunk, bytes_remaining):
        """Progress hook for download progress bar"""
        if self.progress_bar is not None:
            self.progress_bar.update(len(chunk))

    def download_single(self, url: str, file_type: FileType, target_extension: str, 
                       resolution: str, dir_path: Path) -> bool:
        """Download a single video from URL"""
        try:
            yt = YouTube(url, on_progress_callback=self.progress_hook)
            
            # Display video info
            print(f"\n📹 Title: {yt.title}")
            print(f"👤 Author: {yt.author}")
            print(f"⏱️ Duration: {yt.length // 60}:{yt.length % 60:02d}")
            print(f"👀 Views: {yt.views:,}")
            
            if file_type == FileType.VIDEO:
                video_stream, audio_stream = StreamHandler.get_stream(yt, file_type, target_extension, resolution)
                
                if video_stream is None:
                    UIHandler.print_error(f"No suitable video stream found for '{yt.title}'. Skipping download.")
                    return False
                
                # Handle progressive stream (video + audio combined)
                if audio_stream is None:
                    return self._download_progressive(yt, video_stream, dir_path)
                else:
                    return self._download_adaptive(yt, video_stream, audio_stream, target_extension, dir_path)
            
            else:  # Audio only
                audio_stream, _ = StreamHandler.get_stream(yt, file_type, target_extension)
                if audio_stream is None:
                    UIHandler.print_error(f"No suitable audio stream found for '{yt.title}'. Skipping download.")
                    return False
                
                return self._download_audio(yt, audio_stream, dir_path)
                
        except Exception as e:
            UIHandler.print_error(f"Error processing video: {str(e)}")
            return False

    def _download_progressive(self, yt: YouTube, stream, dir_path: Path) -> bool:
        """Download progressive stream (video + audio combined)"""
        try:
            file_size = stream.filesize
            print(f"📦 File size: {file_size / (1024*1024):.1f} MB")
            print(f"🎯 Quality: {stream.resolution}")
            
            self.progress_bar = tqdm(
                total=file_size,
                unit='B',
                unit_scale=True,
                desc="Downloading",
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
            )

            stream.download(output_path=str(dir_path))
            self.progress_bar.close()
            UIHandler.print_success(f"'{yt.title}' downloaded successfully!")
            return True
            
        except Exception as e:
            if self.progress_bar is not None:
                self.progress_bar.close()
            UIHandler.print_error(f"Failed to download '{yt.title}': {str(e)}")
            return False

    def _download_adaptive(self, yt: YouTube, video_stream, audio_stream, target_extension: str, dir_path: Path) -> bool:
        """Download adaptive streams (separate video and audio)"""
        try:
            total_size = video_stream.filesize + audio_stream.filesize
            print(f"📦 Total file size: {total_size / (1024*1024):.1f} MB")
            print(f"🎯 Video quality: {video_stream.resolution}")
            print(f"🎵 Audio quality: {audio_stream.abr}")
            
            # Download video
            print("Downloading video stream...")
            self.progress_bar = tqdm(
                total=video_stream.filesize,
                unit='B',
                unit_scale=True,
                desc="Video",
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
            )
            
            video_filename = f"{yt.title}_video_temp.{video_stream.subtype}"
            video_path = dir_path / video_filename
            video_stream.download(output_path=str(dir_path), filename=video_filename)
            self.progress_bar.close()
            
            # Download audio
            print("Downloading audio stream...")
            self.progress_bar = tqdm(
                total=audio_stream.filesize,
                unit='B',
                unit_scale=True,
                desc="Audio",
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
            )
            
            audio_filename = f"{yt.title}_audio_temp.{audio_stream.subtype}"
            audio_path = dir_path / audio_filename
            audio_stream.download(output_path=str(dir_path), filename=audio_filename)
            self.progress_bar.close()
            
            # Merge video and audio
            print("Merging video and audio...")
            output_filename = f"{yt.title}.{target_extension}"
            output_path = dir_path / output_filename
            
            if StreamHandler.merge_video_audio(video_path, audio_path, output_path, yt.length):
                UIHandler.print_success(f"'{yt.title}' downloaded and merged successfully!")
                return True
            else:
                UIHandler.print_error(f"Failed to merge streams for '{yt.title}'")
                return False
                
        except Exception as e:
            if self.progress_bar is not None:
                self.progress_bar.close()
            UIHandler.print_error(f"Failed to download '{yt.title}': {str(e)}")
            return False

    def _download_audio(self, yt: YouTube, stream, dir_path: Path) -> bool:
        """Download audio-only stream"""
        try:
            file_size = stream.filesize
            print(f"📦 File size: {file_size / (1024*1024):.1f} MB")
            print(f"🎵 Audio quality: {stream.abr}")
            
            self.progress_bar = tqdm(
                total=file_size,
                unit='B',
                unit_scale=True,
                desc="Downloading",
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]'
            )

            stream.download(output_path=str(dir_path))
            self.progress_bar.close()
            UIHandler.print_success(f"'{yt.title}' downloaded successfully!")
            return True
            
        except Exception as e:
            if self.progress_bar is not None:
                self.progress_bar.close()
            UIHandler.print_error(f"Failed to download '{yt.title}': {str(e)}")
            return False