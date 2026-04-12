"""
Unit tests for the AgentController.

Tests the core "brain" logic:
    - Tool selection based on input
    - Execution trace generation
    - Error handling and retry logic
    - Task status transitions
"""

import pytest
from app.agent.controller import AgentController
from app.models import TaskResult, TaskStatus
from app.tools.base import BaseTool


class FailingTool(BaseTool):
    """A tool that always fails — used to test error handling."""

    @property
    def name(self) -> str:
        return "FailingTool"

    @property
    def description(self) -> str:
        return "Always fails"

    def can_handle(self, user_input: str) -> float:
        return 0.9

    def execute(self, user_input: str) -> str:
        raise RuntimeError("Simulated failure")


class TestAgentController:

    def setup_method(self):
        self.agent = AgentController()

    def test_selects_calculator(self):
        task = TaskResult(input="calculate 3 + 5")
        result = self.agent.process_task(task)
        assert result.tool_used == "CalculatorTool"
        assert result.status == TaskStatus.COMPLETED
        assert "8" in result.output

    def test_selects_text_processor(self):
        task = TaskResult(input='Convert "hello" to uppercase')
        result = self.agent.process_task(task)
        assert result.tool_used == "TextProcessorTool"
        assert result.status == TaskStatus.COMPLETED
        assert "HELLO" in result.output

    def test_selects_weather(self):
        task = TaskResult(input="What's the weather in Tokyo?")
        result = self.agent.process_task(task)
        assert result.tool_used == "WeatherMockTool"
        assert result.status == TaskStatus.COMPLETED
        assert "Tokyo" in result.output

    def test_execution_trace_has_steps(self):
        task = TaskResult(input="calculate 2 + 2")
        result = self.agent.process_task(task)
        assert len(result.execution_steps) >= 3
        # Step 1: Received input
        assert "Received input" in result.execution_steps[0].description
        # Step 2: Selected tool
        assert "CalculatorTool" in result.execution_steps[1].description
        # Last step: Returning result
        assert "Returning" in result.execution_steps[-1].description

    def test_no_matching_tool(self):
        """When no tool matches, the agent should report failure gracefully."""
        task = TaskResult(input="xyzzy nonsense gibberish 12345")
        result = self.agent.process_task(task)
        assert result.status == TaskStatus.FAILED
        assert result.error is not None

    def test_error_handling_and_retry(self):
        """Agent should retry on failure and eventually report the error."""
        agent = AgentController(tools=[FailingTool()])
        task = TaskResult(input="anything")
        result = agent.process_task(task, max_retries=1)
        assert result.status == TaskStatus.FAILED
        assert "Simulated failure" in result.error
        # Should have retry steps in the trace
        step_descriptions = [s.description for s in result.execution_steps]
        assert any("Retry" in d for d in step_descriptions)

    def test_get_available_tools(self):
        tools = self.agent.get_available_tools()
        assert len(tools) == 3
        names = [t["name"] for t in tools]
        assert "TextProcessorTool" in names
        assert "CalculatorTool" in names
        assert "WeatherMockTool" in names

    def test_completed_task_has_timestamp(self):
        task = TaskResult(input="3 + 5")
        result = self.agent.process_task(task)
        assert result.completed_at is not None
