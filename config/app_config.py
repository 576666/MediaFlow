"""
应用配置管理
"""
import json
import os
from typing import Dict, Any


class AppConfig:
    """应用配置管理类"""
    
    def __init__(self, config_file: str = "mediaflow_config.json"):
        self.config_file = config_file
        self.default_config = {
            "system": {
                "hardware_acceleration": "auto",
                "max_concurrent_tasks": 4,
                "cache_size_mb": 1024
            },
            "ui": {
                "theme": "dark",
                "default_layout": "advanced",
                "frame_cache_size": 50
            },
            "paths": {
                "default_input": "",
                "default_output": "{input}/processed",
                "temp_directory": ""
            },
            "encoding": {
                "default_preset": "medium",
                "default_crf": 23,
                "preview_duration_sec": 5
            }
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并默认配置，确保所有必需的键都存在
                    return self._merge_configs(self.default_config, loaded_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        
        # 如果配置文件不存在或加载失败，返回默认配置
        return self.default_config.copy()
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key: str, default=None):
        """获取配置值，支持嵌套键（用.分隔）"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value):
        """设置配置值，支持嵌套键（用.分隔）"""
        keys = key.split('.')
        config_ref = self.config
        
        # 导航到嵌套字典的适当层级
        for k in keys[:-1]:
            if k not in config_ref or not isinstance(config_ref[k], dict):
                config_ref[k] = {}
            config_ref = config_ref[k]
        
        # 设置最终值
        config_ref[keys[-1]] = value
    
    def _merge_configs(self, default: Dict, override: Dict) -> Dict:
        """合并默认配置和覆盖配置"""
        result = default.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result


# 全局配置实例
app_config = AppConfig()