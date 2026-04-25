# -*- coding: utf-8 -*-
"""
Mixed Batch Processor Base Class

Provides base functionality for batch processing operations that handle both video and photo files.
Extends the BaseBatchProcessor with mixed media utilities.
"""

import os
from typing import Optional, List, Dict, Any

from ..base.base_processor import BaseBatchProcessor


class MixedBatchProcessor(BaseBatchProcessor):
    """
    Base class for mixed media batch processing operations.
    """

    # All supported media extensions
    MEDIA_EXTENSIONS = [
        # Video
        '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm',
        '.m4v', '.mpg', '.mpeg', '.3gp', '.3g2', '.ts',
        # Photo
        '.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif',
        '.webp', '.heic', '.heif',
        # RAW
        '.arw', '.nef', '.dng', '.raf', '.raw', '.rw2', '.orf',
        '.cr2', '.cr3', '.nrw',
        # Metadata
        '.xmp'
    ]

    VIDEO_EXTENSIONS = ['.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.m4v', '.mpg', '.mpeg']
    PHOTO_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.heic']
    RAW_EXTENSIONS = ['.arw', '.nef', '.dng', '.raf', '.raw', '.rw2', '.orf', '.cr2', '.cr3']
    METADATA_EXTENSIONS = ['.xmp']

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the mixed batch processor.

        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)

    def scan_all_media(self,
                   folder_path: str,
                   extensions: Optional[List[str]] = None,
                   recursive: bool = True) -> List[str]:
        """
        Scan folder for all media files (video and photo).

        Args:
            folder_path: Folder to scan
            extensions: Specific extensions to filter. If None, uses MEDIA_EXTENSIONS
            recursive: Whether to scan recursively

        Returns:
            List of media file paths
        """
        if extensions is None:
            extensions = self.MEDIA_EXTENSIONS

        return self.scan_files(folder_path, extensions, recursive)

    def separate_video_photo(self, folder_path: str) -> Dict[str, List[str]]:
        """
        Separate video and photo files in folder.

        Args:
            folder_path: Folder to scan

        Returns:
            Dictionary with 'videos' and 'photos' lists
        """
        if not self.validate_path(folder_path):
            return {'videos': [], 'photos': []}

        videos = self.scan_files(folder_path, self.VIDEO_EXTENSIONS, recursive=True)
        photos = self.scan_files(folder_path, self.PHOTO_EXTENSIONS, recursive=True)

        return {'videos': videos, 'photos': photos}

    def get_media_info(self, media_path: str) -> Optional[Dict[str, Any]]:
        """
        Get media file information.

        Args:
            media_path: Path to media file

        Returns:
            Dictionary with media info or None
        """
        if not os.path.exists(media_path):
            return None

        ext = os.path.splitext(media_path)[1].lower()

        if ext in self.VIDEO_EXTENSIONS:
            media_type = 'video'
        elif ext in self.PHOTO_EXTENSIONS or ext in self.RAW_EXTENSIONS:
            media_type = 'photo'
        else:
            media_type = 'unknown'

        try:
            return {
                'path': media_path,
                'name': os.path.basename(media_path),
                'size': os.path.getsize(media_path),
                'ext': ext,
                'type': media_type,
                'modified': os.path.getmtime(media_path)
            }
        except Exception as e:
            self.logger.error(f"Failed to get media info: {e}")
            return None