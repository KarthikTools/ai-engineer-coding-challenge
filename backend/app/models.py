"""
Pydantic models for the Task Agent application.

Defines the data structures for tasks, execution steps, and API responses.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
import uuid


class TaskStatus(str, Enum):
    """Possible states of a task."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionStep(BaseModel):
    """A single step in the agent's execution trace."""
    step_number: int
    description: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TaskRequest(BaseModel):
    """Incoming request to create a new task."""
    input: str = Field(..., min_length=1, max_length=1000, description="The user's task description")


class TaskResult(BaseModel):
    """Complete result of a processed task."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    input: str
    status: TaskStatus = TaskStatus.PENDING
    output: Optional[str] = None
    tool_used: Optional[str] = None
    execution_steps: List[ExecutionStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    model_config = ConfigDict(
        ser_json_timedelta="iso8601",
    )
