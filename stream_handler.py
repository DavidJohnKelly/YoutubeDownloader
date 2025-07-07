from pytubefix import YouTube
from config import FileType
from pathlib import Path
from ffmpeg import FFmpeg, Progress
from tqdm import tqdm

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
    def get_stream(yt: YouTube, file_type: FileType, target_extension: str, resolution: str = ""):
        """Get appropriate stream based on file type"""
        if file_type == FileType.VIDEO:
            return StreamHandler.get_video_stream(yt, target_extension, resolution)
        elif file_type == FileType.AUDIO:
            return StreamHandler.get_audio_stream(yt, target_extension), None

    @staticmethod
    def merge_video_audio(video_path: Path, audio_path: Path, output_path: Path, file_seconds: int) -> bool:
        """Merge video and audio files using ffmpeg-python"""
        try:
            # Initialize progress bar
            progress_bar = tqdm(
                total=100,  # Percentage scale (0-100)
                unit='%',
                bar_format='{l_bar}{bar}| {n:.0f}% [{elapsed}<{remaining}]'
            )
            
            last_progress = 0

            def on_progress(progress: Progress):
                """Update progress bar based on time progress"""
                nonlocal last_progress
                try:
                    # current progress (0-1)
                    current_progress = min(progress.time.total_seconds() / float(file_seconds), 1.0)
                    current_percent = current_progress * 100
                    progress_bar.update(current_percent - last_progress)
                    last_progress = current_percent
                except Exception as e:
                    print(f"Progress error: {str(e)}")

            ffmpeg = (
                FFmpeg()
                .input(str(video_path))
                .input(str(audio_path))
                .output(str(output_path), vcodec='copy', acodec='aac')
            )

            ffmpeg.on("progress", on_progress)
            ffmpeg.execute()

            if last_progress < 100:
                progress_bar.update(100 - last_progress)
            
            progress_bar.close()

            # Clean up temporary files
            video_path.unlink(missing_ok=True)
            audio_path.unlink(missing_ok=True)

            return True
        except FileNotFoundError:
            print("❌ FFmpeg not found. Please install FFmpeg to merge high-quality video streams.")
            print("   Keeping separate video and audio files.")
            return False
        except Exception as e:
            print(f"❌ Error merging files: {str(e)}")
            return False