# ui_handler.py
from config import FileType, VALID_VIDEO_FILE_TYPES, VALID_AUDIO_FILE_TYPES, AVAILABLE_RESOLUTIONS

class UIHandler:
    @staticmethod
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
||                                                 Version 2.0                                                ||
\==============================================================================================================/
        """
        print(title)

    @staticmethod
    def print_section_header(title: str):
        """Print a formatted section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")

    @staticmethod
    def print_success(message: str):
        """Print success message with checkmark"""
        print(f"✅ {message}")

    @staticmethod
    def print_error(message: str):
        """Print error message with X mark"""
        print(f"❌ {message}")

    @staticmethod
    def print_info(message: str):
        """Print info message with info icon"""
        print(f"ℹ️  {message}")

    @staticmethod
    def get_url_input() -> str:
        """Get URL input from user"""
        UIHandler.print_section_header("ENTER DOWNLOAD URL")
        return input("🔗 Enter the playlist, channel, or video URL: ").strip()

    @staticmethod
    def get_file_type() -> FileType:
        """Get file type selection from user"""
        UIHandler.print_section_header("SELECT DOWNLOAD TYPE")
        print("1️⃣  Video (with audio)")
        print("2️⃣  Audio only")
        
        while True:
            file_type = input("\n🎯 Enter your choice (1 or 2): ").strip()
            if file_type == '1':
                UIHandler.print_success("Video download selected")
                return FileType.VIDEO
            elif file_type == '2':
                UIHandler.print_success("Audio download selected")
                return FileType.AUDIO
            else:
                UIHandler.print_error("Please enter 1 or 2")

    @staticmethod
    def get_file_extension(file_type: FileType) -> str:
        """Get file extension from user based on file type"""
        UIHandler.print_section_header("SELECT FILE FORMAT")
        
        if file_type == FileType.VIDEO:
            extensions = VALID_VIDEO_FILE_TYPES
        else:
            extensions = VALID_AUDIO_FILE_TYPES
            
        extension_str = ', '.join(extensions)
        print(f"Available formats: {extension_str}")

        while True:
            extension = input(f"\n📁 Enter desired file extension: ").lower().strip()
            if extension in extensions:
                UIHandler.print_success(f"Format '{extension}' selected")
                return extension
            else:
                UIHandler.print_error(f"Please enter a valid extension from: {extension_str}")

    @staticmethod
    def get_resolution() -> str:
        """Get desired resolution from user"""
        UIHandler.print_section_header("SELECT VIDEO RESOLUTION")
        print("Available resolutions:")
        for i, res in enumerate(AVAILABLE_RESOLUTIONS, 1):
            print(f"{i}️⃣  {res}")
        
        while True:
            choice = input(f"\n🎯 Enter your choice (1-{len(AVAILABLE_RESOLUTIONS)}): ").strip()
            try:
                index = int(choice) - 1
                if 0 <= index < len(AVAILABLE_RESOLUTIONS):
                    resolution = AVAILABLE_RESOLUTIONS[index]
                    UIHandler.print_success(f"Resolution '{resolution}' selected")
                    return resolution
                else:
                    UIHandler.print_error(f"Please enter a number between 1 and {len(AVAILABLE_RESOLUTIONS)}")
            except ValueError:
                UIHandler.print_error(f"Please enter a valid number between 1 and {len(AVAILABLE_RESOLUTIONS)}")

    @staticmethod
    def get_zip_preference() -> bool:
        """Get user preference for ZIP compression"""
        UIHandler.print_section_header("ARCHIVE OPTION")
        print("📦 Would you like to compress the downloaded files into a ZIP archive?")
        choice = input("Enter 1 for YES, anything else for NO: ").strip()
        
        if choice == '1':
            UIHandler.print_success("Files will be compressed into a ZIP archive")
            return True
        else:
            UIHandler.print_info("Files will be kept in a folder")
            return False