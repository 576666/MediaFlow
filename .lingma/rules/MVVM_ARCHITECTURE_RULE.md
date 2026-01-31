---
trigger: always_on
---
# MVVM Architecture Rule

## Description
This rule enforces the Model-View-ViewModel (MVVM) architectural pattern in the application. The MVVM pattern helps separate the development of graphical user interfaces from business logic.

## Components
- **Model**: Represents the data layer and business logic
- **View**: The UI layer that displays the data
- **ViewModel**: Acts as a binder between the View and Model, handles UI logic

## Guidelines
- ViewModels should inherit from QObject to support Qt's signal-slot mechanism
- ViewModels must contain the business logic, not the UI widgets
- Views should only handle UI-related operations and display logic
- Use Signals for communication between ViewModel and View

## Examples

### ✅ Correct Implementation
from PySide6.QtCore import QObject, Signal

class ImageProcessorViewModel(QObject):
    """ViewModel class inherits QObject for signals"""
    progress_changed = Signal(int)
    
    def __init__(self, processor_service):
        super().__init__()
        self._processor = processor_service
        
    def process_image(self, image_path: str) -> None:
        # Business logic goes here
        result = self._processor.process(image_path)
        return result

class ImageProcessorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.viewmodel = ImageProcessorViewModel(ImageProcessorService())
        self.viewmodel.progress_changed.connect(self.update_progress)
        
    def on_process_button_clicked(self):
        # Only UI logic, delegates to ViewModel
        self.viewmodel.process_image("path/to/image.jpg")

### ❌ Forbidden: UI contains business logic
class ImageProcessorWidget(QWidget):
    def process_image(self) -> None:  # Wrong: UI widget contains processing logic
        # Direct file system and CPU operations
        with open("image.jpg", "rb") as f:
            data = f.read()
        # Complex processing directly in UI
        processed_data = complex_algorithm(data)
        return processed_data

## Enforcement
- All business logic must be in ViewModel or Model classes
- UI components (Views) should only contain UI-related code
- Violations will cause the linter to raise an error
