# playlist_downloader.py
from pytubefix import Playlist, Channel
from pathlib import Path
from config import FileType
from video_downloader import VideoDownloader
from ui_handler import UIHandler

class PlaylistDownloader:
    def __init__(self):
        self.video_downloader = VideoDownloader()

    def download_playlist(self, playlist_url: str, file_type: FileType, target_extension: str, 
                         resolution: str, dir_path: Path):
        """Download all videos from a playlist"""
        try:
            playlist = Playlist(playlist_url)
            UIHandler.print_section_header(f"PLAYLIST: {playlist.title}")
            UIHandler.print_info(f"Total videos: {len(playlist.video_urls)}")
            
            successful_downloads = 0
            failed_downloads = 0
            
            for i, url in enumerate(playlist.video_urls, 1):
                print(f"\n[{i}/{len(playlist.video_urls)}] Processing video...")
                if self.video_downloader.download_single(url, file_type, target_extension, resolution, dir_path):
                    successful_downloads += 1
                else:
                    failed_downloads += 1
            
            # Summary
            UIHandler.print_section_header("PLAYLIST DOWNLOAD SUMMARY")
            UIHandler.print_success(f"Successfully downloaded: {successful_downloads} videos")
            if failed_downloads > 0:
                UIHandler.print_error(f"Failed downloads: {failed_downloads} videos")
                
        except Exception as e:
            UIHandler.print_error(f"Error processing playlist: {str(e)}")

    def download_channel(self, url: str, file_type: FileType, target_extension: str, 
                        resolution: str, dir_path: Path):
        """Download all videos from a channel"""
        try:
            channel = Channel(url)
            UIHandler.print_section_header(f"CHANNEL: {channel.channel_name}")
            UIHandler.print_info(f"Subscriber count: {getattr(channel, 'subscriber_count', 'Unknown')}")
            
            video_urls = list(channel.video_urls)
            UIHandler.print_info(f"Total videos found: {len(video_urls)}")
            
            successful_downloads = 0
            failed_downloads = 0
            
            for i, video_url in enumerate(video_urls, 1):
                print(f"\n[{i}/{len(video_urls)}] Processing video...")
                if self.video_downloader.download_single(video_url, file_type, target_extension, resolution, dir_path):
                    successful_downloads += 1
                else:
                    failed_downloads += 1
            
            # Process playlists from channel home
            UIHandler.print_info("Checking for channel playlists...")
            for item in channel.home:
                if isinstance(item, Playlist):
                    UIHandler.print_info(f"Found playlist: {item.title}")
                    self.download_playlist(item.playlist_url, file_type, target_extension, resolution, dir_path)
            
            # Summary
            UIHandler.print_section_header("CHANNEL DOWNLOAD SUMMARY")
            UIHandler.print_success(f"Successfully downloaded: {successful_downloads} videos")
            if failed_downloads > 0:
                UIHandler.print_error(f"Failed downloads: {failed_downloads} videos")
                
        except Exception as e:
            UIHandler.print_error(f"Error processing channel: {str(e)}")