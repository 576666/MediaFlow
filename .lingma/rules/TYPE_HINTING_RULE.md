---
trigger: always_on
---
# Type Hinting Rule

## Description
This rule enforces the use of complete type hints for all public APIs in the application. Proper type hinting improves code readability, maintainability, and enables better static analysis tools to detect potential bugs early in the development process.

## Requirements
- All function/method parameters must have type hints
- All function/method return values must have type hints using '->' syntax
- Class attributes must include type hints
- Import necessary types from typing module when needed (Optional, List, Dict, Tuple, etc.)
- Generic types should be properly parameterized (e.g., List[str], Dict[str, int])

## Examples

### ✅ Correct Implementation
# ✅ All public APIs must have complete type hints
from typing import Optional, List, Dict, Tuple
from PySide6.QtCore import QObject, Signal
from core.models.task import TaskModel

class PluginManager:
    def __init__(self, plugin_dir: str) -> None:
        self._plugins: Dict[str, BaseProcessor] = {}
        
    def load_plugins(self) -> List[str]:
        """Load all plugins and return plugin names"""
        pass
        
    def get_processor(self, name: str) -> Optional[BaseProcessor]:
        """Get processor by name"""
        pass

### ❌ Forbidden: Missing type hints
# ❌ Missing type hints in public API
class PluginManager:
    def __init__(self, plugin_dir):  # Wrong: no type hints
        self._plugins = {}  # Wrong: no type hint for attribute
        
    def load_plugins(self):  # Wrong: no return type hint
        pass
        
    def get_processor(self, name):  # Wrong: no param or return type hints
        pass

## Enforcement
- All public methods (not prefixed with '_') must have complete type hints
- Violations will cause the linter to raise an error
- Private methods should also have type hints when they are complex enough to benefit from them
