---
trigger: always_on
---
# GPU Acceleration Rule

## Description
This rule enforces the use of GPU acceleration for computationally intensive operations in the application. When GPU hardware is available, it should be preferred over CPU processing for supported operations to improve performance and efficiency.

## Requirements
- Check for GPU availability before performing intensive computations
- Implement fallback mechanisms to CPU processing when GPU is unavailable
- Use appropriate GPU computing frameworks (CUDA, OpenCL, etc.) when available
- Maintain compatibility with systems that lack GPU acceleration
- Properly manage GPU memory resources

## Implementation Guidelines
- Detect GPU availability at initialization
- Use established GPU computing libraries (CuPy, Numba CUDA, etc.)
- Implement both GPU and CPU versions of intensive algorithms
- Monitor GPU memory usage to prevent overflow
- Gracefully degrade to CPU when GPU operations fail

## Examples

### ✅ Correct Implementation
# ✅ Prefer hardware acceleration
import numpy as np
from typing import Optional

class GPUAcceleratedRenderer:
    def __init__(self) -> None:
        self._use_gpu = self._check_gpu_availability()
        
    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available"""
        try:
            # Check for NVIDIA GPU
            import cupy
            return True
        except ImportError:
            # Fallback to OpenGL
            return self._check_opengl_support()
            
    def render_image(self, image_data: np.ndarray) -> np.ndarray:
        if self._use_gpu:
            return self._render_with_gpu(image_data)
        else:
            return self._render_with_cpu(image_data)
            
    def _render_with_gpu(self, image_data: np.ndarray) -> np.ndarray:
        import cupy as cp
        gpu_array = cp.asarray(image_data)
        # Perform GPU-accelerated operations
        result = self._gpu_processing(gpu_array)
        return cp.asnumpy(result)
        
    def _render_with_cpu(self, image_data: np.ndarray) -> np.ndarray:
        # Fallback CPU implementation
        return self._cpu_processing(image_data)
        
    def _check_opengl_support(self) -> bool:
        # Check for OpenGL support as alternative
        try:
            import OpenGL.GL as gl
            return True
        except ImportError:
            return False
            
    def _gpu_processing(self, data):
        # GPU-specific processing implementation
        pass
        
    def _cpu_processing(self, data: np.ndarray) -> np.ndarray:
        # CPU-specific processing implementation
        pass

### ❌ Forbidden: Ignoring available GPU acceleration
# ❌ CPU-only implementation despite GPU availability
class CPURenderer:
    def render_image(self, image_data: np.ndarray) -> np.ndarray:
        # Processing only on CPU even when GPU is available
        return self._cpu_processing(image_data)

## Enforcement
- All compute-intensive operations must check for GPU availability first
- Applications must implement both GPU and CPU paths
- Violations will cause the linter to raise an error
