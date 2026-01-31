---
trigger: always_on
---
# Project Structure Rule

## Description
This rule enforces a clean, modular project structure following the MVVM architecture pattern. The project must be organized into distinct layers with clear separation of concerns: core logic, user interface, and assets/resources.

## Directory Structure
# ✅ Enforced directory structure
MediaFlow/
├── core/
│   ├── engine/          # Engines: algorithms and computation only
│   │   ├── video_engine.py
│   │   ├── codec_engine.py
│   │   └── quality_analyzer.py
│   ├── models/          # Data models: pure data classes
│   │   ├── task.py
│   │   ├── config.py
│   │   └── quality_metrics.py
│   └── services/        # Services: business logic layer
│       ├── task_queue.py
│       ├── plugin_manager.py
│       └── cache_service.py
├── ui/
│   ├── widgets/         # Reusable UI components
│   │   ├── video_player.py
│   │   ├── comparison_view.py
│   │   └── progress_indicator.py
│   ├── windows/         # Window classes
│   │   ├── main_window.py
│   │   └── preview_window.py
│   └── viewmodels/      # ViewModels
│       ├── main_vm.py
│       └── task_vm.py
├── plugins/             # Plugin system
│   ├── base_processor.py
│   ├── ffmpeg_processor.py
│   └── utils/
├── assets/              # Static assets
│   ├── icons/
│   ├── styles/
│   └── translations/
├── tests/               # Test files
│   ├── unit/
│   ├── integration/
│   └── conftest.py
└── docs/                # Documentation
    ├── api/
    └── user_guide.md

## Requirements
- Each directory must have a clear responsibility based on the MVVM pattern
- Core logic must be separated from UI code
- Models should only contain data definitions without business logic
- Engine components must contain only algorithmic implementations
- Services must handle business logic and coordinate between components
- UI components must follow MVVM pattern with ViewModels handling UI logic
- All modules must be importable and have proper `__init__.py` files

## Module Organization
- Core engines: Pure algorithms and computational functions
- Models: Data classes and structures only (no business logic)
- Services: Coordination and business logic layer
- Widgets: Reusable UI components
- Windows: Application windows and layouts
- ViewModels: UI state management and interaction logic

## Enforcement
- New features must be added in the appropriate directory
- Cross-layer dependencies must follow MVVM guidelines
- Violations will cause the linter to raise an error
- Regular audits will ensure adherence to the structure
