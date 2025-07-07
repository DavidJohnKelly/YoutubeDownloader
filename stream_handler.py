# stream_handler.py
from pytubefix import YouTube
from config import FileType
import os
import subprocess
from pathlib import Path

class StreamHandler:
    @staticmethod
    def get_audio_stream(yt: YouTube, target_extension: str):
        """Get the highest quality audio stream available"""
        stream = yt.streams.get_audio_only(target_extension)
        if stream:
            return stream
        else:
            print(f"No {target_extension} audio streams available. Choosing the next best option.")
            return yt.streams.get_audio_only()

    @staticmethod
    def get_video_stream(yt: YouTube, target_extension: str, resolution: str):
        """Get video stream for specified resolution and extension"""
        # First try to get progressive stream (video + audio combined)
        progressive_stream = yt.streams.filter(
            file_extension=target_extension, 
            progressive=True, 
            resolution=resolution
        ).first()
        
        if progressive_stream:
            return progressive_stream, None
        
        # If no progressive stream, get adaptive streams (video only + audio only)
        video_stream = yt.streams.filter(
            adaptive=True,
            file_extension=target_extension,
            resolution=resolution,
            only_video=True
        ).first()
        
        if not video_stream:
            # Try without file extension restriction
            video_stream = yt.streams.filter(
                adaptive=True,
                resolution=resolution,
                only_video=True
            ).first()
        
        if not video_stream:
            # Fall back to highest available resolution
            print(f"Resolution {resolution} not available. Getting highest quality available.")
            video_stream = yt.streams.filter(adaptive=True, only_video=True).order_by('resolution').desc().first()
        
        # Get audio stream
        audio_stream = yt.streams.filter(adaptive=True, only_audio=True).order_by('abr').desc().first()
        
        return video_stream, audio_stream

    @staticmethod
    def get_stream(yt: YouTube, file_type: FileType, target_extension: str, resolution: str = None):
        """Get appropriate stream based on file type"""
        if file_type == FileType.VIDEO:
            return StreamHandler.get_video_stream(yt, target_extension, resolution)
        elif file_type == FileType.AUDIO:
            return StreamHandler.get_audio_stream(yt, target_extension), None

    @staticmethod
    def merge_video_audio(video_path: Path, audio_path: Path, output_path: Path) -> bool:
        """Merge video and audio files using ffmpeg"""
        try:
            cmd = [
                'ffmpeg', '-i', str(video_path), '-i', str(audio_path),
                '-c:v', 'copy', '-c:a', 'aac', '-y', str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Clean up temporary files
                video_path.unlink()
                audio_path.unlink()
                return True
            else:
                print(f"FFmpeg error: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("❌ FFmpeg not found. Please install FFmpeg to merge high-quality video streams.")
            print("   Keeping separate video and audio files.")
            return False
        except Exception as e:
            print(f"❌ Error merging files: {str(e)}")
            return False