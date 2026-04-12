"""
In-memory persistence layer with export capability.

Stores task results in a Python dictionary for fast lookup.
Supports exporting all data to JSON format.
"""

from __future__ import annotations

import json
from typing import Optional, Dict, List
from app.models import TaskResult


class TaskStore:
    """
    In-memory task storage with export capability.

    Design Decision: Using a dict keyed by task ID for O(1) lookups.
    A list would give O(n) lookups but simpler iteration — since we need
    both, a dict is the right choice (iteration is still easy with .values()).
    """

    def __init__(self) -> None:
        self._tasks: Dict[str, TaskResult] = {}

    def save(self, task: TaskResult) -> TaskResult:
        """Save or update a task."""
        self._tasks[task.id] = task
        return task

    def get(self, task_id: str) -> Optional[TaskResult]:
        """Retrieve a single task by ID."""
        return self._tasks.get(task_id)

    def get_all(self) -> List[TaskResult]:
        """Return all tasks, most recent first."""
        return sorted(
            self._tasks.values(),
            key=lambda t: t.created_at,
            reverse=True,
        )

    def count(self) -> int:
        """Return the number of stored tasks."""
        return len(self._tasks)

    def clear(self) -> None:
        """Remove all tasks (useful for testing)."""
        self._tasks.clear()

    def export_json(self) -> str:
        """
        Export all tasks to a JSON string.

        This satisfies the 'in-memory storage with ability to export' requirement.
        """
        tasks = self.get_all()
        return json.dumps(
            [task.model_dump(mode="json") for task in tasks],
            indent=2,
            default=str,
        )


# Singleton instance — shared across the application
task_store = TaskStore()
