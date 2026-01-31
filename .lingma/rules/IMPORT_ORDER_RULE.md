---
trigger: always_on
---
# Import Order Rule

## Description
This rule enforces a consistent import order throughout the application to improve code readability and maintainability. Imports should be organized in a layered approach following the dependency hierarchy from most general to most specific.

## Requirements
- Organize imports in three distinct layers: Standard Library, Third-party, Local Modules
- Within each layer, imports should be alphabetically sorted
- Use absolute imports for standard library and third-party packages
- Use relative imports for local module imports
- Avoid circular imports between modules

## Import Layers
1. **Standard Library**: Python built-in modules (os, sys, typing, etc.)
2. **Third-party**: External packages (PySide6, numpy, opencv, etc.)
3. **Local Modules**: Project-specific modules (using relative imports)

## Examples

### ✅ Correct Implementation
# ✅ Layered import order
# 1. Python standard library
import os
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass

# 2. Third-party libraries
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout
import numpy as np
import cv2

# 3. Local modules (relative imports)
from ..models.task import TaskModel
from ..services.task_queue import TaskQueue
from .base_processor import BaseProcessor

### ❌ Forbidden: Mixed import layers
# ❌ Mixing import layers
from PySide6.QtWidgets import QWidget
from ..models.task import TaskModel
import os
from typing import Dict
import numpy as np
from .base_processor import BaseProcessor

### ❌ Forbidden: Circular imports
# ❌ Forbidden: Circular imports
# module_a.py imports module_b.py, while module_b.py imports module_a.py

## Enforcement
- All modules must follow the layered import order
- Static analysis tools will check import organization
- Code review checklist includes verification of import ordering
- Violations will cause the linter to raise an error
