---
trigger: always_on
---
# Exception Handling Rule

## Description
This rule enforces a consistent exception handling strategy throughout the application. All exceptions should inherit from a common base exception and be properly caught and handled to prevent application crashes and provide meaningful error messages to users.

## Requirements
- Define a hierarchy of custom exceptions inheriting from a base MediaFlowError
- Catch specific exceptions before general ones
- Log errors appropriately with context information
- Use 'raise ... from ...' to preserve exception chaining when re-raising
- Handle exceptions gracefully without exposing internal details to users

## Exception Hierarchy
- Create a base MediaFlowError exception class
- Derive specific exception types for different error scenarios
- Use appropriate exception types for different error conditions

## Examples

### ✅ Correct Implementation
import logging

logger = logging.getLogger(__name__)

# Define unified exception hierarchy
class MediaFlowError(Exception):
    """Base exception for all MediaFlow errors"""
    pass

class PluginLoadError(MediaFlowError):
    """Raised when plugin loading fails"""
    pass

class ProcessingError(MediaFlowError):
    """Raised when task processing fails"""
    pass

class ConfigurationError(MediaFlowError):
    """Raised when configuration is invalid"""
    pass

# Proper exception handling
def execute_processing_task(task):
    try:
        processor.process_task(task)
    except ProcessingError as e:
        logger.error(f"Task processing failed: {task.id}, error: {e}")
        # Emit failure signal to UI
        self.task_failed.emit(task.id, str(e))
    except OSError as e:
        logger.error(f"File system error during task {task.id}: {e}")
        # Wrap system exceptions in application-specific ones
        raise MediaFlowError(f"File access failed for task {task.id}: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error during task {task.id}: {e}")
        raise MediaFlowError(f"Unexpected error: {e}") from e

### ❌ Forbidden: Poor exception handling
def execute_processing_task(task):
    # Wrong: Catching generic Exception without re-raising
    try:
        processor.process_task(task)
    except Exception:
        print("Something went wrong")  # Wrong: No logging, no proper handling
        return False
    
    # Wrong: Not handling potential exceptions
    with open(task.file_path) as f:  # Could raise FileNotFoundError
        data = f.read()

## Enforcement
- All modules must use the standard exception hierarchy
- Exceptions must be logged with sufficient context
- System exceptions should be wrapped in application-specific ones
- Violations will cause the linter to raise an error
