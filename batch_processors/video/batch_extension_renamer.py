#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频批量格式转换脚本
支持 MP4/MOV/TS/AVI/MKV 之间的真正格式转换（通过 ffmpeg）
优先尝试无损封装复制，失败则使用高质量重新编码
"""

import os
import subprocess
from typing import Dict, Any, Optional, List

from batch_processors.video.video_processor import VideoBatchProcessor


class BatchVideoExtensionRenamer(VideoBatchProcessor):
    """
    通用视频格式批量转换器
    使用 ffmpeg 进行真正的容器/编码格式转换
    """

    SUPPORTED_EXTS = {"mp4", "mov", "ts", "avi", "mkv"}

    def __init__(self,
                 input_ext: str = "",
                 output_ext: str = "",
                 case_option: str = "as_is",
                 config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.input_ext = input_ext.lstrip('.').lower()
        self.output_ext = output_ext.lstrip('.')
        self.case_option = case_option

    def _apply_case(self, ext: str) -> str:
        if self.case_option == "upper":
            return ext.upper()
        elif self.case_option == "lower":
            return ext.lower()
        return ext

    def _ffmpeg_available(self) -> bool:
        """检测系统是否安装了 ffmpeg"""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def _convert_video(self, src_path: str, dst_path: str) -> bool:
        """
        使用 ffmpeg 执行视频格式转换
        1. 先尝试无损流复制（-c copy）
        2. 若失败则使用高质量重新编码（H.264 + AAC）
        """
        if not self._ffmpeg_available():
            return False

        out_ext = os.path.splitext(dst_path)[1].lower()

        # 第一步：尝试无损流复制（速度最快、画质无损）
        copy_cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", src_path,
            "-c", "copy",
            "-movflags", "+faststart",
            dst_path
        ]
        try:
            result = subprocess.run(
                copy_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                return True
        except Exception:
            pass

        # 第二步：无损复制失败，使用高质量重新编码
        encode_cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", src_path,
            "-c:v", "libx264", "-crf", "18", "-preset", "slow",
            "-c:a", "aac", "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            dst_path
        ]
        try:
            subprocess.run(
                encode_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                timeout=3600
            )
            return True
        except Exception:
            return False

    def rename(self, folder_path: str, recursive: bool = True) -> Dict[str, Any]:
        if not os.path.isdir(folder_path):
            return {"success": 0, "failed": 0, "skipped": 0, "details": [f"无效目录: {folder_path}"]}

        if not self._ffmpeg_available():
            return {"success": 0, "failed": 0, "skipped": 0, "details": ["错误: 未检测到 ffmpeg，请先安装并添加到系统 PATH" ]}

        results = {"success": 0, "failed": 0, "skipped": 0, "details": []}
        output_ext_final = self._apply_case(self.output_ext)

        for root, dirs, files in os.walk(folder_path):
            if not recursive and root != folder_path:
                break

            for f in sorted(files):
                name, ext = os.path.splitext(f)
                current_ext = ext.lstrip('.').lower()
                if current_ext != self.input_ext:
                    continue

                new_name = f"{name}.{output_ext_final}"
                old_path = os.path.join(root, f)
                new_path = os.path.join(root, new_name)

                try:
                    if os.path.exists(new_path):
                        results["skipped"] += 1
                        results["details"].append(f"跳过: {f}  ➡️  {new_name}  (目标已存在)")
                        continue

                    if self._convert_video(old_path, new_path):
                        os.remove(old_path)
                        results["success"] += 1
                        results["details"].append(f"格式转换: {f}  ➡️  {new_name}")
                    else:
                        results["failed"] += 1
                        results["details"].append(f"失败: {f}  ➡️  {new_name}  (ffmpeg 转换失败)")
                except Exception as e:
                    results["failed"] += 1
                    results["details"].append(f"失败: {f}  ➡️  {new_name}  ({str(e)})")

            if not recursive:
                break

        return results

    def preview(self, folder_path: str, recursive: bool = True) -> List[str]:
        preview_lines: List[str] = []
        if not os.path.isdir(folder_path):
            return [f"无效目录: {folder_path}"]

        output_ext_final = self._apply_case(self.output_ext)

        for root, dirs, files in os.walk(folder_path):
            if not recursive and root != folder_path:
                break

            for f in sorted(files):
                name, ext = os.path.splitext(f)
                current_ext = ext.lstrip('.').lower()
                if current_ext != self.input_ext:
                    continue

                new_name = f"{name}.{output_ext_final}"
                rel_dir = os.path.relpath(root, folder_path)
                if rel_dir == '.':
                    preview_lines.append(f"📄 {f}  ➡️  {new_name}  (格式转换)")
                else:
                    preview_lines.append(f"📄 {rel_dir}/{f}  ➡️  {new_name}  (格式转换)")

            if not recursive:
                break

        return preview_lines


def batch_rename_video_extensions(folder_path: str,
                                  input_ext: str,
                                  output_ext: str,
                                  case_option: str = "as_is",
                                  recursive: bool = True) -> Dict[str, Any]:
    """便捷函数：一键调用 BatchVideoExtensionRenamer"""
    renamer = BatchVideoExtensionRenamer(input_ext, output_ext, case_option)
    return renamer.rename(folder_path, recursive)
