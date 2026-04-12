"""
Agent Controller — the "brain" of the system.

Responsible for:
    1. Parsing the user's input
    2. Selecting the best tool (using confidence scoring)
    3. Executing the tool
    4. Building a structured execution trace
    5. Handling errors gracefully with retry logic

Design Decisions:
    - Tools are registered at initialization, making the agent extensible.
      Adding a new tool requires zero changes to the controller.
    - Confidence scoring (can_handle) allows the agent to pick the BEST tool,
      not just the first one that matches.
    - The execution trace is built step-by-step, giving full transparency
      into the agent's "reasoning" process.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List, Tuple
from app.models import TaskResult, TaskStatus, ExecutionStep
from app.tools.base import BaseTool
from app.tools import TextProcessorTool, CalculatorTool, WeatherMockTool


class AgentController:
    """
    Orchestrates task processing by selecting and executing tools.

    The controller follows a simple agentic loop:
        Input → Parse → Select Tool → Execute → Build Trace → Return Result
    """

    def __init__(self, tools: Optional[List[BaseTool]] = None) -> None:
        """
        Initialize with a list of tools. If none provided, use defaults.

        This dependency injection pattern makes testing easy —
        you can pass in mock tools for unit tests.
        """
        if tools is None:
            self.tools: List[BaseTool] = [
                TextProcessorTool(),
                CalculatorTool(),
                WeatherMockTool(),
            ]
        else:
            self.tools = tools

    def process_task(self, task: TaskResult, max_retries: int = 1) -> TaskResult:
        """
        Process a task through the agent pipeline.

        Args:
            task: The TaskResult object with the user's input.
            max_retries: Number of retry attempts on failure (bonus feature).

        Returns:
            The updated TaskResult with output, steps, and status.
        """
        steps: List[ExecutionStep] = []
        step_num = 0

        # Step 1: Receive input
        step_num += 1
        steps.append(ExecutionStep(
            step_number=step_num,
            description=f'Received input: "{task.input}"',
        ))

        # Step 2: Analyze input and score tools
        step_num += 1
        tool, confidence = self._select_tool(task.input)

        if tool is None:
            steps.append(ExecutionStep(
                step_number=step_num,
                description="No suitable tool found for this input.",
            ))
            task.status = TaskStatus.FAILED
            task.error = "Could not determine an appropriate tool for this task. Try rephrasing your request."
            task.execution_steps = steps
            return task

        steps.append(ExecutionStep(
            step_number=step_num,
            description=f"Analyzed input. Selected tool: {tool.name} (confidence: {confidence:.0%})",
        ))

        # Step 3: Execute tool (with retry logic)
        attempt = 0
        last_error = None

        while attempt <= max_retries:
            try:
                step_num += 1
                if attempt > 0:
                    steps.append(ExecutionStep(
                        step_number=step_num,
                        description=f"Retry attempt {attempt}/{max_retries} — re-executing {tool.name}",
                    ))

                result = tool.execute(task.input)

                steps.append(ExecutionStep(
                    step_number=step_num,
                    description=f"Tool executed successfully. Result: {result}",
                ))

                # Step 4: Return result
                step_num += 1
                steps.append(ExecutionStep(
                    step_number=step_num,
                    description="Returning result to user.",
                ))

                task.output = result
                task.tool_used = tool.name
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now(timezone.utc)
                task.execution_steps = steps
                return task

            except Exception as e:
                last_error = str(e)
                if attempt < max_retries:
                    steps.append(ExecutionStep(
                        step_number=step_num,
                        description=f"Tool execution failed: {last_error}. Will retry...",
                    ))
                attempt += 1

        # All retries exhausted
        step_num += 1
        steps.append(ExecutionStep(
            step_number=step_num,
            description=f"All attempts failed. Last error: {last_error}",
        ))

        task.status = TaskStatus.FAILED
        task.error = last_error
        task.tool_used = tool.name
        task.execution_steps = steps
        return task

    def _select_tool(self, user_input: str) -> Tuple[Optional[BaseTool], float]:
        """
        Select the best tool for the given input based on confidence scores.

        Returns:
            A tuple of (best_tool, confidence). Returns (None, 0.0) if no tool
            has a confidence above the threshold.
        """
        best_tool: Optional[BaseTool] = None
        best_score = 0.0
        threshold = 0.1  # Minimum confidence to consider a tool

        for tool in self.tools:
            try:
                score = tool.can_handle(user_input)
                if score > best_score:
                    best_score = score
                    best_tool = tool
            except Exception:
                # A tool's can_handle should never crash the agent
                continue

        if best_score < threshold:
            return None, 0.0

        return best_tool, best_score

    def get_available_tools(self) -> List[dict]:
        """Return metadata about all registered tools (useful for the UI)."""
        return [
            {"name": tool.name, "description": tool.description}
            for tool in self.tools
        ]
