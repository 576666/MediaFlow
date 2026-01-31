---
trigger: always_on
---
# Plugin Interface Rule

## Description
This rule enforces the implementation of a standardized plugin interface for all media processing plugins. All plugins must inherit from BaseProcessor and implement required abstract methods to ensure consistent behavior across the application.

## Requirements
- All plugins must inherit from BaseProcessor class
- Must implement all abstract methods defined in BaseProcessor
- Must provide proper type hints for all method signatures
- Should follow the Liskov Substitution Principle - plugin instances should be substitutable for BaseProcessor instances

## Required Abstract Methods
- `name: str` - Property returning plugin identifier
- `description: str` - Property returning plugin description
- `config_ui: QWidget` - Property returning configuration interface
- `process_task(task: TaskModel) -> ProcessingResult` - Main processing method
- `validate_config(config: dict) -> bool` - Configuration validation method

## Examples
