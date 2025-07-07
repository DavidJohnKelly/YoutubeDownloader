import shutil
import zipfile
from pathlib import Path
from datetime import date, datetime
from tqdm import tqdm
from ui_handler import UIHandler

class FileManager:
    @staticmethod
    def get_download_folder(base_path: Path) -> Path:
        """Create and return download folder path"""
        try:
            download_dir = base_path / "Download"
            download_dir.mkdir(exist_ok=True)
            dir_path = download_dir / f"{date.today()}_{datetime.now().strftime('%H-%M-%S')}"
            dir_path.mkdir()
            return dir_path
        except Exception as e:
            print(f"ERROR! Couldn't make download folder. Aborting. {e}")
            exit(-1)

    @staticmethod
    def change_file_extensions(dir_path: Path, file_extension: str):
        """Change all files to specified extension"""
        for file in dir_path.iterdir():
            if file.is_file() and not file.name.endswith(f".{file_extension}"):
                new_file = file.with_suffix(f".{file_extension}")
                file.rename(new_file)

    @staticmethod
    def create_zip_archive(dir_path: Path):
        """Create ZIP archive of all files and clean up original directory"""
        zip_path = dir_path.with_suffix('.zip')
        
        # Count total files for progress bar
        total_files = sum(1 for file in dir_path.rglob('*') if file.is_file())
        
        UIHandler.print_info(f"Creating ZIP archive: {zip_path.name}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            with tqdm(total=total_files, desc="Archiving", unit="files") as pbar:
                for file in dir_path.rglob('*'):
                    if file.is_file():
                        relative_path = file.relative_to(dir_path)
                        zip_file.write(file, arcname=relative_path)
                        pbar.update(1)
        
        UIHandler.print_success(f"Archive created: {zip_path}")
        UIHandler.print_info("Cleaning up temporary files...")
        shutil.rmtree(dir_path)
        UIHandler.print_success("Cleanup completed")
        
        return zip_path