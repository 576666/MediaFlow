---
trigger: always_on
---
# Testing Rule

## Description
This rule enforces comprehensive testing practices for all components in the application. All code must be accompanied by appropriate unit tests, integration tests, and end-to-end tests to ensure reliability, maintainability, and correctness of the software.

## Requirements
- All new features and bug fixes must include corresponding test cases
- Unit tests must cover at least 80% of code branches
- Integration tests must verify interactions between components
- Tests must follow the Arrange-Act-Assert pattern
- Use pytest framework with appropriate fixtures and parameterization
- Test edge cases, error conditions, and boundary values

## Testing Standards
- Write tests that are fast, isolated, and repeatable
- Use descriptive test names that explain expected behavior
- Apply the AAA (Arrange-Act-Assert) pattern consistently
- Use mocking appropriately to isolate units under test
- Maintain test independence - tests shouldn't depend on each other's state

## Test Organization
- Place unit tests in `tests/unit/` directory
- Place integration tests in `tests/integration/` directory
- Place end-to-end tests in `tests/e2e/` directory
- Mirror the source code structure in test directories
- Use conftest.py for shared fixtures and configurations

## Examples

### ✅ Correct Implementation
# ✅ Comprehensive testing implementation
import pytest
from unittest.mock import Mock, patch
from core.services.task_queue import TaskQueue
from core.models.task import TaskModel, TaskStatus

class TestTaskQueue:
    """Task queue test class"""
    
    def setup_method(self) -> None:
        """Setup before each test method"""
        self.queue = TaskQueue(max_workers=2)
        
    def teardown_method(self) -> None:
        """Cleanup after each test method"""
        self.queue.shutdown()
        
    def test_add_task(self) -> None:
        """Test adding task"""
        task = TaskModel(id="test", file_path="test.jpg")
        self.queue.add_task(task)
        assert self.queue.pending_count == 1
        
    @pytest.mark.asyncio
    async def test_process_task_async(self) -> None:
        """Test async task processing"""
        task = TaskModel(id="test", file_path="test.jpg")
        result = await self.queue.process_task_async(task)
        assert result.status == TaskStatus.COMPLETED
        
    def test_concurrent_processing(self) -> None:
        """Test concurrent processing"""
        tasks = [TaskModel(id=f"task{i}", file_path=f"test{i}.jpg") 
                 for i in range(5)]
        
        with patch.object(self.queue, '_process_single') as mock_process:
            mock_process.return_value = TaskStatus.COMPLETED
            results = self.queue.process_batch(tasks)
            
            assert len(results) == 5
            mock_process.assert_called()

### ❌ Forbidden: Insufficient testing
# ❌ Minimal or no tests
class TestTaskQueue:
    def test_basic(self):
        # Wrong: Vague test name, incomplete coverage
        queue = TaskQueue()
        assert queue.pending_count == 0

## Enforcement
- All pull requests must include appropriate tests
- Code coverage must not drop below 80% threshold
- CI pipeline will reject builds that don't pass all tests
- Violations will cause the linter to raise an error
