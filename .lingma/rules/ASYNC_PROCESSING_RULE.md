---
trigger: always_on
---
---
trigger: always_on
---

# Async Processing Rule

## Description
This rule enforces the use of asynchronous patterns for handling I/O-bound and CPU-bound operations in the application. Using async/await patterns improves performance by preventing blocking operations from freezing the application.

## Requirements
- Use `async` and `await` keywords for asynchronous functions
- For CPU-intensive tasks, delegate to thread pools using `loop.run_in_executor()`
- For I/O-bound operations, use appropriate async libraries (aiohttp, aiopg, etc.)
- Always properly handle exceptions in async functions
- Avoid blocking calls in async functions (like time.sleep(), regular file operations, etc.)

## Examples

### ✅ Correct Implementation
import asyncio
from concurrent.futures import ThreadPoolExecutor

class TaskService:
    def __init__(self) -> None:
        self._executor = ThreadPoolExecutor(max_workers=4)
        
    async def process_task_async(self, task: TaskModel) -> ProcessingResult:
        # CPU-intensive tasks to thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self._executor, self._cpu_intensive_process, task
        )
        return result
        
    def _cpu_intensive_process(self, task: TaskModel) -> ProcessingResult:
        # Actual processing logic
        pass

### ❌ Forbidden: Synchronous processing in async context
class TaskService:
    async def process_task_async(self, task: TaskModel) -> ProcessingResult:
        # Wrong: Blocking operation in async function
        time.sleep(5)  # This blocks the event loop!
        
        # Wrong: CPU intensive operation without delegation
        result = self._intensive_computation(task)  # Blocks the event loop!
        return result

## Enforcement
- All I/O-bound operations must be performed asynchronously
- CPU-bound operations must be delegated to thread or process pools
- Violations will cause the linter to raise an error
