# YoutubeVideoDownloader.py
from pathlib import Path
from config import DownloadConfig, FileType
from ui_handler import UIHandler
from video_downloader import VideoDownloader
from playlist_downloader import PlaylistDownloader
from file_manager import FileManager

class YouTubeDownloaderApp:
    def __init__(self):
        self.config = DownloadConfig()
        self.video_downloader = VideoDownloader()
        self.playlist_downloader = PlaylistDownloader()
        self.file_manager = FileManager()

    def setup_configuration(self):
        """Setup download configuration from user input"""
        # Get URL
        url = UIHandler.get_url_input()
        
        # Get file type
        self.config.file_type = UIHandler.get_file_type()
        
        # Get file extension
        self.config.file_extension = UIHandler.get_file_extension(self.config.file_type)
        
        # Get resolution for video downloads
        if self.config.file_type == FileType.VIDEO:
            self.config.resolution = UIHandler.get_resolution()
        
        # Get ZIP preference
        self.config.create_zip = UIHandler.get_zip_preference()
        
        return url

    def determine_download_type(self, url: str) -> str:
        """Determine the type of URL provided"""
        if '/playlist?' in url:
            return 'playlist'
        elif '/channel/' in url or '/@' in url:
            return 'channel'
        else:
            return 'single'

    def start_download(self, url: str, download_type: str):
        """Start the appropriate download based on URL type"""
        UIHandler.print_section_header("STARTING DOWNLOAD")
        
        if download_type == 'playlist':
            UIHandler.print_info("Playlist URL detected")
            self.playlist_downloader.download_playlist(
                url, self.config.file_type, self.config.file_extension, 
                self.config.resolution, self.config.download_path
            )
        elif download_type == 'channel':
            UIHandler.print_info("Channel URL detected")
            self.playlist_downloader.download_channel(
                url, self.config.file_type, self.config.file_extension, 
                self.config.resolution, self.config.download_path
            )
        else:
            UIHandler.print_info("Single video URL detected")
            self.video_downloader.download_single(
                url, self.config.file_type, self.config.file_extension, 
                self.config.resolution, self.config.download_path
            )

    def post_process_files(self):
        """Handle post-processing of downloaded files"""
        UIHandler.print_section_header("POST-PROCESSING")
        UIHandler.print_info("Converting file extensions...")
        self.file_manager.change_file_extensions(self.config.download_path, self.config.file_extension)
        UIHandler.print_success("File extension conversion completed")

        final_path = self.config.download_path
        if self.config.create_zip:
            final_path = self.file_manager.create_zip_archive(self.config.download_path)

        return final_path

    def run(self):
        """Main application entry point"""
        # Display title
        UIHandler.print_ascii_title()
        
        # Setup download folder
        base_path = Path(__file__).resolve().parent
        self.config.download_path = self.file_manager.get_download_folder(base_path)
        
        # Get configuration from user
        url = self.setup_configuration()
        
        # Determine download type and start
        download_type = self.determine_download_type(url)
        self.start_download(url, download_type)
        
        # Post-process files
        final_path = self.post_process_files()
        
        # Show completion message
        UIHandler.print_section_header("DOWNLOAD COMPLETE")
        UIHandler.print_success("All operations completed!")
        print(f"📁 Files location: {final_path}")

def main():
    app = YouTubeDownloaderApp()
    app.run()

if __name__ == '__main__':
    main()