#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用混合批量格式转换脚本
同时支持照片和视频的真正格式转换
内部分别调用 Pillow（图像）和 ffmpeg（视频）
"""

import os
from typing import Dict, Any, Optional, List

from batch_processors.mixed.mixed_processor import MixedBatchProcessor
from batch_processors.photo.batch_extension_renamer import BatchPhotoExtensionRenamer
from batch_processors.video.batch_extension_renamer import BatchVideoExtensionRenamer


class BatchMixedExtensionRenamer(MixedBatchProcessor):
    """
    通用混合格式批量转换器
    可同时处理照片和视频两种媒体类型的真正格式转换
    """

    def __init__(self,
                 photo_input_ext: str = "",
                 photo_output_ext: str = "",
                 video_input_ext: str = "",
                 video_output_ext: str = "",
                 photo_case: str = "as_is",
                 video_case: str = "as_is",
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.photo_input_ext = photo_input_ext.lstrip('.').lower()
        self.photo_output_ext = photo_output_ext.lstrip('.')
        self.video_input_ext = video_input_ext.lstrip('.').lower()
        self.video_output_ext = video_output_ext.lstrip('.')
        self.photo_case = photo_case
        self.video_case = video_case

    def rename(self, folder_path: str, recursive: bool = True) -> Dict[str, Any]:
        """
        执行批量转换：先处理照片，再处理视频
        """
        if not os.path.isdir(folder_path):
            return {"success": 0, "failed": 0, "skipped": 0, "details": [f"无效目录: {folder_path}"]}

        results = {"success": 0, "failed": 0, "skipped": 0, "details": []}

        # 照片转换
        if self.photo_input_ext and self.photo_output_ext:
            photo_renamer = BatchPhotoExtensionRenamer(
                self.photo_input_ext,
                self.photo_output_ext,
                self.photo_case
            )
            photo_res = photo_renamer.rename(folder_path, recursive)
            results["success"] += photo_res["success"]
            results["failed"] += photo_res["failed"]
            results["skipped"] += photo_res["skipped"]
            if photo_res["details"]:
                results["details"].append("【照片转换】")
                results["details"].extend(photo_res["details"])

        # 视频转换
        if self.video_input_ext and self.video_output_ext:
            video_renamer = BatchVideoExtensionRenamer(
                self.video_input_ext,
                self.video_output_ext,
                self.video_case
            )
            video_res = video_renamer.rename(folder_path, recursive)
            results["success"] += video_res["success"]
            results["failed"] += video_res["failed"]
            results["skipped"] += video_res["skipped"]
            if video_res["details"]:
                results["details"].append("【视频转换】")
                results["details"].extend(video_res["details"])

        return results

    def preview(self, folder_path: str, recursive: bool = True) -> List[str]:
        """生成预览列表"""
        preview_lines: List[str] = []
        if not os.path.isdir(folder_path):
            return [f"无效目录: {folder_path}"]

        # 照片预览
        if self.photo_input_ext and self.photo_output_ext:
            photo_renamer = BatchPhotoExtensionRenamer(
                self.photo_input_ext,
                self.photo_output_ext,
                self.photo_case
            )
            photo_lines = photo_renamer.preview(folder_path, recursive)
            if photo_lines:
                preview_lines.append("【照片】")
                preview_lines.extend(photo_lines)

        # 视频预览
        if self.video_input_ext and self.video_output_ext:
            video_renamer = BatchVideoExtensionRenamer(
                self.video_input_ext,
                self.video_output_ext,
                self.video_case
            )
            video_lines = video_renamer.preview(folder_path, recursive)
            if video_lines:
                preview_lines.append("【视频】")
                preview_lines.extend(video_lines)

        return preview_lines


def batch_rename_mixed_extensions(folder_path: str,
                                  photo_input_ext: str = "",
                                  photo_output_ext: str = "",
                                  video_input_ext: str = "",
                                  video_output_ext: str = "",
                                  photo_case: str = "as_is",
                                  video_case: str = "as_is",
                                  recursive: bool = True) -> Dict[str, Any]:
    """便捷函数：一键调用 BatchMixedExtensionRenamer"""
    renamer = BatchMixedExtensionRenamer(
        photo_input_ext, photo_output_ext,
        video_input_ext, video_output_ext,
        photo_case, video_case
    )
    return renamer.rename(folder_path, recursive)
