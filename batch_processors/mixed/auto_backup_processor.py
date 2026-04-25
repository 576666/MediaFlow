# -*- coding: utf-8 -*-
"""
自动备份处理器

处理自动备份，包含视频转码和照片优化。
基于Tool文件夹中的Auto_backup_mini.py脚本。
"""

import os
import shutil
import subprocess
import json
import time
import concurrent.futures
from typing import Optional, Dict, Any, List

from .mixed_processor import MixedBatchProcessor


class AutoBackupProcessor(MixedBatchProcessor):
    """
    带视频转码和照片处理的自动备份处理器。
    """
    
    # 文件类型常量
    RAW_EXTENSIONS = (".NEF", ".ARW", ".RAF", ".DNG", ".XMP")
    VIDEO_EXTENSIONS = (".MOV", ".MP4", ".MOV", ".MP4")
    PHOTO_EXTENSIONS = ('.JPG', '.JPEG', '.PNG', '.TIFF', '.TIF', '.BMP', '.WEBP')
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化自动备份处理器。
        
        参数:
            config: 可选的配置字典
        """
        super().__init__(config)
        self.max_workers = config.get('max_workers', 2) if config else 2
    
    def check_ffmpeg_available(self) -> bool:
        """检查FFmpeg是否可用。"""
        try:
            subprocess.run(['ffmpeg', '-version'], 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL, 
                       check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def get_available_encoders(self) -> Dict[str, bool]:
        """获取可用的视频编码器。"""
        encoders = {'nvidia': False, 'nvidia_av1': False, 'cpu_h265': False, 'cpu_av1': False}
        try:
            out = subprocess.run(['ffmpeg', '-encoders'], 
                            capture_output=True, 
                            text=True, 
                            encoding='utf-8').stdout
            encoders['nvidia'] = 'hevc_nvenc' in out
            encoders['nvidia_av1'] = 'av1_nvenc' in out
            encoders['cpu_h265'] = 'libx265' in out
            encoders['cpu_av1'] = 'libaom-av1' in out
        except Exception as e:
            self.logger.warning(f"无法检查编码器: {e}")
        return encoders
    
    def get_video_info(self, video_path: str) -> tuple:
        """获取视频信息（宽度、高度、帧率、编码器）。"""
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_streams', video_path]
            result = subprocess.run(cmd, capture_output=True, text=True, 
                             encoding='utf-8', errors='ignore', check=True)
            info = json.loads(result.stdout)
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    w, h = stream.get('width'), stream.get('height')
                    r = stream.get('r_frame_rate', '30/1')
                    try:
                        num, den = map(int, r.split('/'))
                        fps = round(num / den, 2)
                    except:
                        fps = 30
                    return int(w), int(h), fps, stream.get('codec_name', '')
        except Exception as e:
            self.logger.warning(f"无法获取视频信息: {e}")
        return None, None, None, None
    
    def is_8k_restore_folder(self, path: str) -> bool:
        """检查文件夹是否是8K修复文件夹。"""
        return "8K修复" in os.path.normpath(path).split(os.sep)
    
    def rename_extensions_to_uppercase(self, folder: str) -> int:
        """将所有扩展名改为大写。"""
        count = 0
        for root, _, files in os.walk(folder):
            if self.is_8k_restore_folder(root):
                continue
            for f in files:
                name, ext = os.path.splitext(f)
                if ext != ext.upper():
                    old = os.path.join(root, f)
                    new = os.path.join(root, name + ext.upper())
                    try:
                        os.rename(old, new)
                        count += 1
                    except Exception as e:
                        self.logger.warning(f"无法重命名 {f}: {e}")
        return count
    
    def backup(self,
              source_folder: str,
              dest_folder: str,
              strategy: str = 'speed',
              bitrate_option: str = 'low',
              copy_only: bool = False) -> Dict[str, Any]:
        """
        执行带转码的备份。
        
        参数:
            source_folder: 源文件夹
            dest_folder: 目标文件夹
            strategy: 编码策略（'speed', 'balance', 'ultra_compression'）
            bitrate_option: 码率选项（'low', 'medium', 'high'）
            copy_only: 如果为True，跳过转码直接复制
            
        返回:
            包含结果的字典
        """
        if not self.validate_path(source_folder):
            return {'success': [], 'failure': [], 'error': '无效源路径'}
        
        # 创建目标目录
        os.makedirs(dest_folder, exist_ok=True)
        
        # 检查FFmpeg
        ffmpeg_available = self.check_ffmpeg_available()
        encoders = {}
        
        if ffmpeg_available:
            encoders = self.get_available_encoders()
            self.logger.info("FFmpeg可用")
            for name, available in encoders.items():
                if available:
                    self.logger.info(f"  - {name}: 可用")
        else:
            self.logger.warning("FFmpeg不可用，将直接复制不转码")
            copy_only = True
        
        # 步骤1：扩展名大写
        self.logger.info("转换扩展名为大写...")
        self.rename_extensions_to_uppercase(source_folder)
        
        # 步骤2：创建目录结构
        self.logger.info("创建目录结构...")
        for root, dirs, _ in os.walk(source_folder):
            if self.is_8k_restore_folder(root):
                continue
            rel = os.path.relpath(root, source_folder)
            if rel != '.':
                os.makedirs(os.path.join(dest_folder, rel), exist_ok=True)
        
        # 步骤3：扫描文件
        skip_exts = {e.lower() for e in self.RAW_EXTENSIONS}
        video_tasks = []
        photo_copy_list = []
        
        self.logger.info("扫描文件...")
        for root, _, files in os.walk(source_folder):
            if self.is_8k_restore_folder(root):
                continue
            for name in files:
                src = os.path.join(root, name)
                ext_lower = os.path.splitext(name)[1].lower()
                
                if ext_lower in {e.lower() for e in self.VIDEO_EXTENSIONS}:
                    # 视频：转码
                    dst = os.path.join(dest_folder, os.path.relpath(src, source_folder))
                    dst = os.path.splitext(dst)[0] + '.MP4'
                    if not os.path.exists(dst):
                        video_tasks.append((src, dst))
                elif ext_lower in {e.lower() for e in self.PHOTO_EXTENSIONS} and ext_lower not in skip_exts:
                    # 照片：复制
                    dst = os.path.join(dest_folder, os.path.relpath(src, source_folder))
                    if not os.path.exists(dst):
                        photo_copy_list.append((src, dst))
        
        self.logger.info(f"找到 {len(video_tasks)} 个视频, {len(photo_copy_list)} 张照片")
        
        results = {'videos': [], 'photos': [], 'failed': []}
        
        # 步骤4：处理视频
        if video_tasks and not copy_only and ffmpeg_available:
            results['videos'] = self._transcode_videos(video_tasks, strategy, bitrate_option)
        elif video_tasks:
            # 直接复制视频
            for src, dst in video_tasks:
                try:
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
                    results['videos'].append(src)
                except Exception as e:
                    self.logger.error(f"复制失败 {src}: {e}")
                    results['failed'].append(src)
        
        # 步骤5：复制照片
        for src, dst in photo_copy_list:
            try:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                results['photos'].append(src)
            except Exception as e:
                self.logger.error(f"复制失败 {src}: {e}")
                results['failed'].append(src)
        
        return results
    
    def _transcode_videos(self, 
                        tasks: List[tuple],
                        strategy: str,
                        bitrate_option: str) -> List[str]:
        """转码视频。"""
        results = []
        
        max_bitrate = {'low': '5M', 'medium': '10M', 'high': '20M'}[bitrate_option]
        bufsize = {'low': '10M', 'medium': '20M', 'high': '40M'}[bitrate_option]
        
        def process_video(args):
            src, dst = args
            width, height, fps, _ = self.get_video_info(src)
            
            # 构建缩放滤镜
            scale_filter = None
            if width and height and (width > 1920 or height > 1080):
                ar = width / height
                tw = 1920 if ar >= 1 else int(1080 * ar)
                th = int(1920 / ar) if ar >= 1 else 1080
                tw -= tw % 2
                th -= th % 2
                scale_filter = f"scale={tw}:{th}"
            
            # 构建命令
            cmd = ['ffmpeg', '-i', src]
            
            if strategy == 'speed':
                cmd += ['-c:v', 'hevc_nvenc', '-b:v', max_bitrate, 
                       '-maxrate', max_bitrate, '-bufsize', bufsize,
                       '-preset', 'p6', '-spatial-aq', '1']
            elif strategy == 'balance':
                cmd += ['-c:v', 'libx265', '-b:v', max_bitrate,
                       '-maxrate', max_bitrate, '-bufsize', bufsize,
                       '-preset', 'medium']
            else:
                cmd += ['-c:v', 'libaom-av1', '-b:v', max_bitrate,
                       '-maxrate', max_bitrate, '-bufsize', bufsize,
                       '-cpu-used', '6']
            
            if scale_filter:
                cmd += ['-vf', scale_filter]
            
            cmd += ['-c:a', 'aac', '-b:a', '128k', '-y', dst]
            
            start = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            
            if result.returncode == 0 and os.path.exists(dst) and os.path.getsize(dst) > 1024:
                self.logger.info(f"已转码: {os.path.basename(src)} ({time.time()-start:.1f}秒)")
                return True, src
            return False, src
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as ex:
            futures = [ex.submit(process_video, t) for t in tasks]
            for f in concurrent.futures.as_completed(futures):
                ok, src = f.result()
                if ok:
                    results.append(src)
        
        return results


# 便利函数
def backup_to_folder(source: str, 
                   dest: str,
                   strategy: str = 'speed',
                   bitrate: str = 'low') -> Dict[str, Any]:
    """
    便利函数，执行备份。
    
    参数:
        source: 源文件夹
        dest: 目标文件夹  
        strategy: 编码策略
        bitrate: 码率选项
        
    返回:
        包含结果的字典
    """
    processor = AutoBackupProcessor()
    return processor.backup(source, dest, strategy, bitrate)