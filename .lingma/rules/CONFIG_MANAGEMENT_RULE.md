---
trigger: always_on
---
# Configuration Management Rule

## Description
This rule enforces type-safe and centralized configuration management throughout the application. All configuration settings must be defined using typed data classes with proper validation and serialization capabilities. This ensures consistency, prevents configuration-related errors, and provides clear interfaces for accessing application settings.

## Requirements
- Use dataclasses for strongly-typed configuration definitions
- Implement proper validation and type conversion for configuration values
- Support loading configuration from JSON files with default value fallbacks
- Provide methods for serializing configuration back to storage
- Use pathlib.Path for file path operations
- Include appropriate type hints for all configuration properties

## Implementation Guidelines
- Define configuration as dataclasses with default values
- Implement from_file class method for loading configuration
- Include to_dict method for serialization
- Handle missing configuration files gracefully by providing defaults
- Validate configuration values during loading
- Use appropriate data types (int, bool, str) for configuration properties

## Examples

### ✅ Correct Implementation
# ✅ Type-safe configuration management
from dataclasses import dataclass
from typing import Optional
import json
from pathlib import Path

@dataclass
class AppConfig:
    """Application configuration data class"""
    max_concurrent_tasks: int = 4
    gpu_acceleration: bool = True
    cache_size_mb: int = 1024
    theme: str = "dark"
    language: str = "zh_CN"
    
    @classmethod
    def from_file(cls, config_path: Path) -> 'AppConfig':
        """Load from configuration file"""
        if not config_path.exists():
            return cls()  # Return default config
            
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Validate and convert types
        return cls(
            max_concurrent_tasks=int(data.get('max_concurrent_tasks', 4)),
            gpu_acceleration=bool(data.get('gpu_acceleration', True)),
            cache_size_mb=int(data.get('cache_size_mb', 1024)),
            theme=str(data.get('theme', 'dark')),
            language=str(data.get('language', 'zh_CN'))
        )
        
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'gpu_acceleration': self.gpu_acceleration,
            'cache_size_mb': self.cache_size_mb,
            'theme': self.theme,
            'language': self.language
        }

### ❌ Forbidden: Untyped or unstructured configuration
# ❌ Using dictionaries without type safety
class ConfigManager:
    def __init__(self):
        # Wrong: No type safety, difficult to maintain
        self.config = {
            "max_concurrent_tasks": 4,
            "gpu_acceleration": True,
            "cache_size_mb": 1024,
            "theme": "dark"
        }
    
    def get_max_tasks(self):
        # No type guarantee, could cause runtime errors
        return self.config["max_concurrent_tasks"]

## Enforcement
- All configuration must be defined using typed dataclasses
- Configuration loading must handle missing files gracefully
- Type conversion and validation must occur during loading
- Violations will cause the linter to raise an error
