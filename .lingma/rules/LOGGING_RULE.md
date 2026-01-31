---
trigger: always_on
---
# Logging Rule

## Description
This rule enforces the use of structured, unified logging throughout the application. All logging must follow a consistent format and use appropriate log levels to ensure maintainability and debuggability of the application.

## Requirements
- Use Python's standard logging module
- Configure a centralized logging setup at application startup
- Use structured logging with contextual information when possible
- Follow appropriate log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Use rotating file handlers to manage log file sizes
- Include timestamps and component identifiers in log messages
- Use logger instances with named hierarchies (e.g., "MediaFlow.PluginManager")

## Implementation Guidelines
- Call setup_logging() at application startup
- Use logging.getLogger(__name__) to get logger instances
- Use appropriate log levels:
  * DEBUG: Detailed diagnostic information
  * INFO: General information about program execution
  * WARNING: Something unexpected happened but program continues
  * ERROR: Serious problem occurred
  * CRITICAL: Very serious error occurred
- Include relevant context in log messages using extra parameter
- Use consistent naming convention for logger names following package hierarchy

## Examples

### ✅ Correct Implementation
# ✅ Unified structured logging
import logging
from logging.handlers import RotatingFileHandler

def setup_logging() -> None:
    """Configure application-level logging"""
    logger = logging.getLogger("MediaFlow")
    logger.setLevel(logging.DEBUG)
    
    # File handler
    file_handler = RotatingFileHandler(
        "mediaflow.log", maxBytes=10*1024*1024, backupCount=5
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (debug mode only)
    if DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logger.addHandler(console_handler)

# Usage example
logger = logging.getLogger("MediaFlow.PluginManager")
logger.info("Plugins loaded", extra={"plugin_count": len(plugins)})

### ❌ Forbidden: Inconsistent logging
# ❌ No unified approach to logging
import logging

def some_function():
    # Wrong: Different formats in different places
    logging.info(f"Processing {task_id}")  # Inconsistent formatting
    
def another_function():
    # Wrong: Direct print statements instead of logging
    print(f"Error processing task {task_id}")  # Should use logger instead

## Enforcement
- All modules must use the unified logging setup
- Custom log formats are forbidden unless approved
- Direct print statements in production code are forbidden
- Violations will cause the linter to raise an error
