#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像批量格式转换脚本
支持 JPG/JPEG/PNG/TIF/TIFF 之间的真正格式转换（通过 Pillow）
"""

import os
from typing import Dict, Any, Optional, List

from batch_processors.photo.photo_processor import PhotoBatchProcessor


class BatchPhotoExtensionRenamer(PhotoBatchProcessor):
    """
    通用图像格式批量转换器
    不只是修改扩展名，而是使用 Pillow 进行真正的图像格式编码转换
    """

    SUPPORTED_EXTS = {"jpg", "jpeg", "png", "tif", "tiff"}

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

    def _convert_image(self, src_path: str, dst_path: str) -> bool:
        """使用 Pillow 执行真正的图像格式转换"""
        try:
            from PIL import Image
            with Image.open(src_path) as img:
                out_ext = os.path.splitext(dst_path)[1].lower()
                # JPEG 不支持透明通道，需要提前转换
                if out_ext in ('.jpg', '.jpeg') and img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ('RGBA', 'LA'):
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = img.convert('RGB')
                elif out_ext in ('.jpg', '.jpeg') and img.mode != 'RGB':
                    img = img.convert('RGB')
                img.save(dst_path)
            return True
        except Exception:
            return False

    def rename(self, folder_path: str, recursive: bool = True) -> Dict[str, Any]:
        if not os.path.isdir(folder_path):
            return {"success": 0, "failed": 0, "skipped": 0, "details": [f"无效目录: {folder_path}"]}

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

                    if self._convert_image(old_path, new_path):
                        os.remove(old_path)  # 转换成功后删除原文件
                        results["success"] += 1
                        results["details"].append(f"格式转换: {f}  ➡️  {new_name}")
                    else:
                        results["failed"] += 1
                        results["details"].append(f"失败: {f}  ➡️  {new_name}  (图像解码失败)")
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


def batch_rename_photo_extensions(folder_path: str,
                                  input_ext: str,
                                  output_ext: str,
                                  case_option: str = "as_is",
                                  recursive: bool = True) -> Dict[str, Any]:
    """便捷函数：一键调用 BatchPhotoExtensionRenamer"""
    renamer = BatchPhotoExtensionRenamer(input_ext, output_ext, case_option)
    return renamer.rename(folder_path, recursive)
