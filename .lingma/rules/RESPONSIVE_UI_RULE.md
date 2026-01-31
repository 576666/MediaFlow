---
trigger: always_on
---
# Responsive UI Rule

## Description
This rule ensures that all time-consuming operations in the application run asynchronously to keep the UI responsive. Long-running tasks should not block the main UI thread, which would make the application appear frozen to users. Instead, these operations should be executed asynchronously with proper UI feedback mechanisms such as progress dialogs or status indicators.

## Requirements
- All long-running operations must be executed asynchronously
- UI thread should never be blocked by time-consuming operations
- Provide visual feedback to users during processing (progress bars, dialogs, etc.)
- Use asyncio for asynchronous operations
- Update UI elements only from the main thread

## Implementation Guidelines
- Use async/await pattern for long-running operations
- Show progress indicators during processing
- Delegate CPU-intensive work to background threads/processes when needed
- Ensure UI updates happen on the main thread using Qt's mechanisms if needed

## Examples

### ✅ Correct Implementation
# ✅ All time-consuming operations must not block UI thread
import asyncio
from PySide6.QtWidgets import QMainWindow, QMessageBox, QProgressDialog

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        self.progress_dialog = ProcessingProgressDialog()
        self.task_service = TaskService()
        
    def on_process_clicked(self) -> None:
        # Use async processing
        self.progress_dialog.show()
        
        # Start async task
        asyncio.create_task(self._process_async())
        
    async def _process_async(self) -> None:
        try:
            tasks = self.get_selected_tasks()
            results = await self.task_service.process_batch_async(tasks)
            
            # UI updates must be on main thread
            self._update_results_on_ui_thread(results)
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            QMessageBox.critical(self, "Error", f"Processing failed: {e}")
        finally:
            self.progress_dialog.close()

### ❌ Forbidden: Blocking UI with synchronous operations
class MainWindow(QMainWindow):
    def on_process_clicked(self) -> None:
        # Wrong: Synchronous processing blocks UI thread
        tasks = self.get_selected_tasks()
        results = self.task_service.process_batch(tasks)  # Blocks UI!
        self.display_results(results)  # Updates UI after long delay

## Enforcement
- All potentially long-running operations must be non-blocking
- Violations will cause the linter to raise an error
- Performance testing may be used to identify operations that should be made asynchronous
