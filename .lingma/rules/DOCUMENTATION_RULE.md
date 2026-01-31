---
trigger: always_on
---
# Documentation Rule

## Description
This rule enforces comprehensive documentation standards throughout the application. All public APIs, classes, functions, and modules must include detailed docstrings following the Google Python Style Guide. Proper documentation ensures code maintainability, improves developer onboarding, and enables automated documentation generation.

## Requirements
- All public classes must have docstrings describing their purpose, attributes, and usage
- All public methods and functions must include detailed docstrings with Args, Returns, and Raises sections
- Use Google-style docstrings with proper type hints
- Include usage examples in docstrings where appropriate
- Document all class attributes, method parameters, and return values
- Use descriptive and clear language in all documentation

## Documentation Standards
- Use triple double quotes for docstrings
- Include Args section for all method parameters with type descriptions
- Include Returns section for all methods that return values
- Include Raises section for documented exceptions
- Use type hints in method signatures and reference them in docstrings
- Add Examples section for complex functionality showing usage patterns

## Examples
