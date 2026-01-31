---
trigger: always_on
---
# Plugin API Rule

## Description
This rule defines the standard API interface that all media processing plugins must implement. All plugins must inherit from BaseProcessor and implement the required properties and methods to ensure consistent behavior across the application.

## Requirements
- All plugins must inherit from BaseProcessor class
- Must implement all required abstract properties and methods
- Must provide proper type hints for all method signatures
- Should follow the Liskov Substitution Principle - plugin instances should be substitutable for BaseProcessor instances

## Required Properties
- `name: str` - Property returning plugin identifier
- `description: str` - Property returning plugin description  
- `version: str` - Property returning plugin version
- `supported_formats: List[str]` - Property returning list of supported file formats

## Required Methods
- `initialize() -> bool` - Initialize plugin resources
- `config_ui: QWidget` - Property returning configuration interface
- `get_default_config() -> Dict[str, Any]` - Return default configuration
- `process_task(task: TaskModel) -> ProcessingResult` - Main processing method
- `validate_config(config: Dict[str, Any]) -> bool` - Configuration validation method

## Plugin Template
# ✅ Plugin template - all plugins must follow this structure
from typing import Any, Dict
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from plugins.base_processor import BaseProcessor, ProcessingResult

class TemplateProcessor(BaseProcessor):
    """Plugin template - all plugins must follow this structure"""
    
    # Required properties
    @property
    def name(self) -> str:
        return "Template Processor"
        
    @property
    def description(self) -> str:
        return "Processor description"
        
    @property
    def version(self) -> str:
        return "1.0.0"
        
    @property
    def supported_formats(self) -> List[str]:
        return [".jpg", ".png", ".mp4"]
        
    # Required methods
    def initialize(self) -> bool:
        """Initialize plugin resources"""
        try:
            self._setup_resources()
            return True
        except Exception as e:
            logger.error(f"Plugin initialization failed: {e}")
            return False
            
    @property
    def config_ui(self) -> QWidget:
        """Generate configuration interface"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Configuration Options"))
        # Add configuration controls
        return widget
        
    def get_default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "quality": 85,
            "format": "jpg",
            "preserve_metadata": True
        }
        
    def process_task(self, task: TaskModel) -> ProcessingResult:
        """Process single task"""
        # Implement processing logic
        result = ProcessingResult()
        try:
            # Processing code...
            result.success = True
            result.message = "Processing completed"
        except Exception as e:
            result.success = False
            result.error = str(e)
        return result
        
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration"""
        required_keys = {"quality", "format"}
        return all(key in config for key in required_keys)

## Enforcement
- All plugins must adhere to the defined interface
- Type checking will verify proper implementation of properties and methods
- Plugins failing to implement required interface will be rejected during loading
- Violations will cause the linter to raise an error
