"""
FastAPI API routes for the Task Agent application.

Endpoints:
    POST /tasks       — Submit a new task for processing
    GET  /tasks       — List all past tasks
    GET  /tasks/{id}  — Get a specific task by ID
    GET  /tasks/export — Export all tasks as JSON
    GET  /tools       — List available tools
"""

from __future__ import annotations

from typing import List
from fastapi import APIRouter, HTTPException
from app.models import TaskRequest, TaskResult
from app.store import task_store
from app.agent import AgentController

router = APIRouter()
agent = AgentController()


@router.post("/tasks", response_model=TaskResult, status_code=201)
async def create_task(request: TaskRequest):
    """
    Submit a new task for the agent to process.

    The agent will:
    1. Analyze the input
    2. Select the appropriate tool
    3. Execute the tool
    4. Return the result with an execution trace
    """
    # Create a new task
    task = TaskResult(input=request.input)

    # Process through the agent controller
    processed_task = agent.process_task(task)

    # Persist the result
    task_store.save(processed_task)

    return processed_task


@router.get("/tasks", response_model=List[TaskResult])
async def list_tasks():
    """Return all tasks, most recent first."""
    return task_store.get_all()


@router.get("/tasks/export")
async def export_tasks():
    """Export all tasks as a downloadable JSON string."""
    return {"data": task_store.export_json(), "count": task_store.count()}


@router.get("/tasks/{task_id}", response_model=TaskResult)
async def get_task(task_id: str):
    """Retrieve a specific task by its ID."""
    task = task_store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


@router.get("/tools")
async def list_tools():
    """List all available tools and their descriptions."""
    return agent.get_available_tools()
