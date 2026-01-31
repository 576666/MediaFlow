---
trigger: always_on
---
# Caching Mechanism Rule

## Description
This rule enforces the implementation of smart caching mechanisms to improve application performance by reducing redundant computations and I/O operations. Proper caching strategies should be applied to expensive operations, especially those involving file I/O, network requests, and computational processing.

## Requirements
- Implement intelligent caching for expensive operations
- Use appropriate cache eviction policies (LRU, TTL, etc.)
- Cache should consider file modification times to invalidate stale entries
- Use memory-efficient cache keys and limit cache size to prevent memory exhaustion
- Thread-safe caching implementations where necessary

## Implementation Guidelines
- Apply `functools.lru_cache` decorator for simple function-level caching
- For more complex caching needs, implement custom cache classes
- Consider file modification time when caching file-based operations
- Implement cache warming strategies for frequently accessed data
- Use immutable cache keys to prevent corruption
- Monitor cache hit rates and performance metrics

## Examples

### ✅ Correct Implementation
# ✅ Smart caching implementation
import os
import time
from functools import lru_cache, wraps
from typing import Callable, TypeVar
from dataclasses import dataclass

T = TypeVar('T')

def cached_property_with_ttl(ttl: int = 300):
    """Property decorator with TTL caching"""
    def decorator(func: Callable) -> property:
        attr_name = f"_cached_{func.__name__}"
        time_attr_name = f"_cached_{func.__name__}_time"
        
        @wraps(func)
        def wrapper(self):
            current_time = time.time()
            cached_time = getattr(self, time_attr_name, 0)
            
            if current_time - cached_time > ttl:
                value = func(self)
                setattr(self, attr_name, value)
                setattr(self, time_attr_name, current_time)
            
            return getattr(self, attr_name)
        
        return property(wrapper)
    return decorator

class ThumbnailGenerator:
    def __init__(self, cache_size: int = 128) -> None:
        self._thumbnail_cache = {}
        self._cache_size = cache_size
        
    @lru_cache(maxsize=128)
    def generate_thumbnail_cached(self, file_path: str, size: tuple[int, int]) -> bytes:
        """Generate thumbnail with LRU caching"""
        # Check if file has changed since last cache
        mod_time = os.path.getmtime(file_path)
        cache_key = f"{file_path}_{size}_{mod_time}"
        
        # Actual thumbnail generation would go here
        return self._generate_thumbnail_impl(file_path, size)
        
    def _generate_thumbnail_impl(self, file_path: str, size: tuple[int, int]) -> bytes:
        # Implementation for generating thumbnail
        pass

### ❌ Forbidden: No caching for expensive operations
# ❌ Expensive operations without caching
class ThumbnailGenerator:
    def generate_thumbnail(self, file_path: str, size: tuple[int, int]) -> bytes:
        # Wrong: Performing expensive operation without any caching
        # This could involve decoding entire video or processing large image
        return self._expensive_thumbnail_generation(file_path, size)

## Enforcement
- All I/O bound and computationally expensive operations must implement appropriate caching
- Cache hit rate should be monitored and optimized
- Violations will cause the linter to raise an error
