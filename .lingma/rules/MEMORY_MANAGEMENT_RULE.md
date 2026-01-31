---
trigger: always_on
---
# Memory Management Rule

## Description
This rule enforces proper memory management practices throughout the application. It requires the use of context managers for resource management, proper cleanup of memory-intensive objects, and efficient handling of large data structures to prevent memory leaks and excessive memory consumption.

## Requirements
- Use context managers (`with` statements) for managing resources like file handles, database connections, and external library objects
- Implement `__enter__` and `__exit__` methods in classes that hold resources requiring cleanup
- Properly release memory-intensive objects when no longer needed
- Use generators instead of lists when processing large datasets
- Follow RAII (Resource Acquisition Is Initialization) principles

## Implementation Guidelines
- Always use context managers for resources that require explicit cleanup
- Implement proper exception handling in `__exit__` methods
- Close file handles, database connections, and other resources immediately after use
- Use weak references when appropriate to avoid circular references
- Monitor memory usage during processing of large files

## Examples

### ✅ Correct Implementation
# ✅ Must use context managers for resource management
import cv2
import numpy as np
from typing import Optional
from core.exceptions import ProcessingError

class VideoDecoder:
    def __init__(self, video_path: str) -> None:
        self._video_path = video_path
        self._cap: Optional[cv2.VideoCapture] = None
        
    def __enter__(self) -> 'VideoDecoder':
        self._cap = cv2.VideoCapture(self._video_path)
        if not self._cap.isOpened():
            raise ProcessingError(f"Cannot open video: {self._video_path}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._cap:
            self._cap.release()
            
    def get_frame(self, frame_num: int) -> np.ndarray:
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self._cap.read()
        if not ret:
            raise ProcessingError("Failed to read frame")
        return frame

# Usage example
with VideoDecoder("video.mp4") as decoder:
    frame = decoder.get_frame(100)
    # Process frame...

### ❌ Forbidden: Improper resource management
# ❌ Resource not properly managed
class VideoDecoder:
    def __init__(self, video_path: str) -> None:
        self._cap = cv2.VideoCapture(video_path)  # Resource opened in constructor
        
    def get_frame(self, frame_num: int) -> np.ndarray:
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = self._cap.read()
        return frame
    # No cleanup method called!

# Usage - resource might never be released
decoder = VideoDecoder("video.mp4")
frame = decoder.get_frame(100)
# _cap never gets closed if there's an exception or developer forgets to close

## Enforcement
- All resource-holding classes must implement proper context management
- Static analysis tools will check for proper resource cleanup
- Code review checklist includes verification of context manager usage
- Violations will cause the linter to raise an error
