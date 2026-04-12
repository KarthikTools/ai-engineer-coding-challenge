"""
Base class for all tools.

Every tool in the system inherits from BaseTool, which enforces a consistent
interface. This makes the agent controller tool-agnostic — it doesn't need
to know the internals of any specific tool.

Design Pattern: Strategy Pattern — each tool is a strategy that the agent
selects at runtime based on the user's input.
"""

from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    Abstract base class for agent tools.

    Subclasses must implement:
        - name: A unique identifier for the tool
        - description: A human-readable description of what the tool does
        - execute(input): The core logic of the tool
        - can_handle(input): Whether this tool is appropriate for the given input
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the tool."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of the tool's capabilities."""
        ...

    @abstractmethod
    def execute(self, user_input: str) -> str:
        """
        Execute the tool's logic on the given input.

        Args:
            user_input: The raw user input string.

        Returns:
            The result as a string.

        Raises:
            ValueError: If the input is invalid for this tool.
        """
        ...

    @abstractmethod
    def can_handle(self, user_input: str) -> float:
        """
        Return a confidence score (0.0 to 1.0) that this tool can handle the input.

        This allows the agent to pick the *best* tool, not just the first match.
        A higher score means higher confidence.

        Args:
            user_input: The raw user input string.

        Returns:
            A float between 0.0 (cannot handle) and 1.0 (perfect match).
        """
        ...
