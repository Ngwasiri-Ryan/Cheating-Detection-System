import os
import uuid
import logging
from typing import Optional, BinaryIO, Tuple
from pathlib import Path
from datetime import datetime  
from core.exceptions import FileSystemError

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self, upload_root: str, allowed_extensions: Optional[set] = None):
        """
        Initialize file service.
        
        Args:
            upload_root: Root upload directory
            allowed_extensions: Set of allowed file extensions
        """
        self.upload_root = upload_root
        self.allowed_extensions = allowed_extensions or {'.mp4', '.avi', '.mov', '.mkv'}
        self._ensure_upload_directory()

    def _ensure_upload_directory(self) -> None:
        """Create upload directory if needed."""
        try:
            Path(self.upload_root).mkdir(parents=True, exist_ok=True)
            logger.info(f"Upload directory ready at {self.upload_root}")
        except Exception as e:
            logger.critical(f"Failed to create upload directory: {str(e)}")
            raise FileSystemError(
                operation="directory_creation",
                path=self.upload_root,
                message=str(e),
                error_code=5004
            )

    def save_uploaded_file(self, file_obj: BinaryIO, original_filename: str = "") -> str:
        """
        Save uploaded file with unique filename.
        
        Args:
            file_obj: File-like object to save
            original_filename: Original filename for extension
            
        Returns:
            Path to saved file
            
        Raises:
            FileSystemError: If save fails
        """
        try:
            ext = self._get_file_extension(original_filename or getattr(file_obj, 'filename', ''))
            if not ext:
                raise FileSystemError(
                    operation="file_save",
                    path="unknown",
                    message="No file extension provided",
                    error_code=5001
                )
                
            if ext.lower() not in self.allowed_extensions:
                raise FileSystemError(
                    operation="file_save",
                    path=original_filename,
                    message=f"Extension {ext} not allowed",
                    error_code=5002
                )

            unique_id = uuid.uuid4().hex
            filename = f"{unique_id}{ext}"
            save_path = os.path.join(self.upload_root, filename)
            
            file_obj.seek(0)
            with open(save_path, 'wb') as f:
                f.write(file_obj.read())
            
            logger.info(f"Saved file to {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"File save failed: {str(e)}")
            raise FileSystemError(
                operation="file_save",
                path=original_filename,
                message=str(e),
                error_code=5001
            )

    def get_file_id(self, file_path: str) -> str:
        """Extract unique file ID from path."""
        return os.path.splitext(os.path.basename(file_path))[0]

    def delete_file(self, file_path: str) -> None:
        """
        Delete a file.
        
        Args:
            file_path: Path to file to delete
            
        Raises:
            FileSystemError: If deletion fails
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
        except Exception as e:
            logger.error(f"File deletion failed: {str(e)}")
            raise FileSystemError(
                operation="file_delete",
                path=file_path,
                message=str(e),
                error_code=5003
            )

    def cleanup_old_files(self, max_age_days: int = 7) -> Tuple[int, int]:
        """
        Clean up files older than specified days.
        
        Args:
            max_age_days: Maximum file age in days
            
        Returns:
            Tuple of (deleted_count, remaining_count)
        """
        deleted = 0
        remaining = 0
        
        try:
            for filename in os.listdir(self.upload_root):
                filepath = os.path.join(self.upload_root, filename)
                if os.path.isfile(filepath):
                    file_age = (datetime.now() - datetime.fromtimestamp(
                        os.path.getmtime(filepath))).days
                    
                    if file_age > max_age_days:
                        try:
                            os.remove(filepath)
                            deleted += 1
                            logger.debug(f"Deleted old file: {filename}")
                        except Exception as e:
                            remaining += 1
                            logger.warning(f"Could not delete {filename}: {str(e)}")
                    else:
                        remaining += 1
                        
            logger.info(f"Cleaned up {deleted} old files, {remaining} remain")
            return deleted, remaining
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            raise FileSystemError(
                operation="file_cleanup",
                path=self.upload_root,
                message=str(e),
                error_code=5005
            )

    def _get_file_extension(self, filename: str) -> str:
        """Extract lowercase file extension."""
        return os.path.splitext(filename)[1].lower()