"""
质量分析引擎 (PSNR, SSIM, VMAF)
"""
import cv2
import numpy as np
import os
from typing import Dict, Any, Optional
import logging
from core.models.video_task import QualityMetrics


class QualityAnalyzer:
    """质量分析引擎"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def compare_videos(self, original_path: str, processed_path: str) -> QualityMetrics:
        """对比视频质量，返回PSNR、SSIM等指标"""
        try:
            # 读取视频文件并逐帧比较
            cap_orig = cv2.VideoCapture(original_path)
            cap_proc = cv2.VideoCapture(processed_path)
            
            psnr_values = []
            ssim_values = []
            
            while True:
                ret_orig, frame_orig = cap_orig.read()
                ret_proc, frame_proc = cap_proc.read()
                
                if not ret_orig or not ret_proc:
                    break
                
                # 计算PSNR
                psnr = self._calculate_psnr(frame_orig, frame_proc)
                if psnr is not None:
                    psnr_values.append(psnr)
                
                # 计算SSIM
                ssim = self._calculate_ssim(frame_orig, frame_proc)
                if ssim is not None:
                    ssim_values.append(ssim)
            
            cap_orig.release()
            cap_proc.release()
            
            # 计算平均值
            avg_psnr = np.mean(psnr_values) if psnr_values else None
            avg_ssim = np.mean(ssim_values) if ssim_values else None
            
            # 获取原始和处理后视频的比特率
            bitrate_orig = self._get_video_bitrate(original_path)
            bitrate_proc = self._get_video_bitrate(processed_path)
            
            return QualityMetrics(
                psnr=avg_psnr,
                ssim=avg_ssim,
                bitrate_original=bitrate_orig,
                bitrate_compressed=bitrate_proc,
                compression_ratio=bitrate_orig/bitrate_proc if bitrate_proc and bitrate_orig else None
            )
            
        except Exception as e:
            self.logger.error(f"视频质量对比失败: {str(e)}")
            return QualityMetrics()
    
    def generate_quality_report(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """生成质量分析报告"""
        report = {
            'psnr': metrics.psnr,
            'ssim': metrics.ssim,
            'bitrate_original': metrics.bitrate_original,
            'bitrate_compressed': metrics.bitrate_compressed,
            'compression_ratio': metrics.compression_ratio,
            'quality_score': self._calculate_quality_score(metrics),
            'recommendation': self._generate_recommendation(metrics)
        }
        
        return report
    
    def _calculate_psnr(self, img1: np.ndarray, img2: np.ndarray) -> Optional[float]:
        """计算两幅图像的PSNR值"""
        try:
            # 确保图像尺寸相同
            if img1.shape != img2.shape:
                # 调整图像大小使其一致
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            mse = np.mean((img1.astype(float) - img2.astype(float)) ** 2)
            if mse == 0:
                return float('inf')
            
            max_pixel = 255.0
            psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
            return psnr
        except Exception:
            return None
    
    def _calculate_ssim(self, img1: np.ndarray, img2: np.ndarray) -> Optional[float]:
        """计算两幅图像的SSIM值"""
        try:
            # 确保图像尺寸相同
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # 转换为灰度图计算SSIM
            gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            
            # 使用OpenCV的SSIM计算
            ssim = cv2.quality.QualitySSIM_compute(gray1, gray2)
            return ssim[0]  # 返回第一个通道的SSIM值
        except Exception:
            # 如果OpenCV不支持，使用sklearn的实现
            try:
                from skimage.metrics import structural_similarity as ssim_sk
                gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                score = ssim_sk(gray1, gray2)
                return score
            except ImportError:
                return None
            except Exception:
                return None
    
    def _get_video_bitrate(self, video_path: str) -> Optional[float]:
        """获取视频比特率"""
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # 获取文件大小
            file_size = os.path.getsize(video_path)
            bitrate = (file_size * 8) / duration if duration > 0 else 0
            
            cap.release()
            return bitrate
        except Exception:
            return None
    
    def _calculate_quality_score(self, metrics: QualityMetrics) -> Optional[float]:
        """根据各项指标计算综合质量评分"""
        try:
            score = 0.0
            weight_psnr = 0.4
            weight_ssim = 0.4
            weight_compression = 0.2
            
            if metrics.psnr is not None:
                # PSNR分数：假设PSNR>30为高质量
                psnr_score = min(metrics.psnr / 50.0, 1.0)  # 归一化到0-1
                score += psnr_score * weight_psnr
            
            if metrics.ssim is not None:
                # SSIM分数：本身就是0-1之间的值
                score += metrics.ssim * weight_ssim
            
            if metrics.compression_ratio is not None:
                # 压缩比分数：平衡质量和文件大小
                compression_score = 1.0 / (1.0 + abs(metrics.compression_ratio - 2.0))
                score += compression_score * weight_compression
            
            return min(score, 1.0)  # 限制在0-1之间
        except Exception:
            return None
    
    def _generate_recommendation(self, metrics: QualityMetrics) -> str:
        """根据质量指标生成建议"""
        if metrics.psnr and metrics.psnr < 30:
            return "视频质量较低，建议调整编码参数提高质量"
        elif metrics.ssim and metrics.ssim < 0.8:
            return "视频相似度较低，建议优化编码设置"
        elif metrics.compression_ratio and metrics.compression_ratio > 10:
            return "压缩比较高，可能导致质量损失"
        else:
            return "视频质量良好"