---
trigger: always_on
---
# Input Validation Rule

## Description
This rule enforces strict input validation across all user inputs and file operations in the application. All inputs must be validated for type, format, security, and business constraints before being processed by the system to prevent injection attacks, buffer overflows, and invalid data processing.

## Requirements
- All user inputs must be validated against predefined schemas
- File paths must be sanitized to prevent directory traversal attacks
- Input length limits must be enforced to prevent buffer overflow
- Type validation must be performed using type hints and runtime checks
- Security validation must prevent access to sensitive system directories

## Validation Standards
- Use Path.resolve() to normalize file paths and check for traversal attempts
- Implement allowlists for file extensions and content types
- Validate input ranges for numeric values
- Sanitize string inputs for special characters when needed
- Check permissions before attempting file operations

## Examples

### ✅ Correct Implementation
# ✅ All inputs must be validated
import os
from pathlib import Path
from typing import Union

class FileValidator:
    """File validator"""
    
    @staticmethod
    def validate_file_path(file_path: Union[str, Path]) -> bool:
        """
        Validate if file path is safe and valid.
        
        Args:
            file_path: File path to validate
            
        Returns:
            bool: Whether path is valid
            
        Raises:
            SecurityError: When path attempts to access sensitive directories
        """
        path = Path(file_path).resolve()
        
        # Prevent directory traversal attacks
        if ".." in str(path):
            raise SecurityError("Path contains illegal characters")
            
        # Check file existence
        if not path.exists():
            raise FileNotFoundError(f"File doesn't exist: {file_path}")
            
        # Check file type
        allowed_extensions = {'.jpg', '.png', '.mp4', '.mov', '.raw'}
        if path.suffix.lower() not in allowed_extensions:
            raise ValueError(f"Unsupported file type: {path.suffix}")
            
        return True

### ❌ Forbidden: Insufficient input validation
# ❌ No validation of user inputs
def process_file(file_path: str):
    # Wrong: No validation of file path
    with open(file_path, 'r') as f:  # Security risk: path traversal possible
        content = f.read()
    return content

# ❌ Weak validation
def weak_validate(file_path: str) -> bool:
    # Wrong: Only checking extension without path normalization
    if file_path.endswith('.jpg'):
        return True
    return False

## Enforcement
- All inputs must pass validation before processing
- Static analysis tools will check for validation requirements
- Security testing will verify protection against injection attacks
- Violations will cause the linter to raise an error
