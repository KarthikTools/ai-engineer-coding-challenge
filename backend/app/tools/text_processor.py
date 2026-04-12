"""
TextProcessorTool — handles text manipulation tasks.

Supported operations:
    - uppercase / lowercase conversion
    - word count
    - character count
    - reverse text
    - title case
"""

from __future__ import annotations

import re
from typing import Dict, List
from .base import BaseTool


class TextProcessorTool(BaseTool):
    """Tool for text processing operations like case conversion and word count."""

    @property
    def name(self) -> str:
        return "TextProcessorTool"

    @property
    def description(self) -> str:
        return "Processes text — uppercase, lowercase, word count, character count, reverse, title case"

    # Keywords grouped by operation for clear matching
    _OPERATION_KEYWORDS: Dict[str, List[str]] = {
        "uppercase": ["uppercase", "upper case", "upper", "capitalize all", "all caps", "to upper"],
        "lowercase": ["lowercase", "lower case", "lower", "to lower"],
        "word_count": ["word count", "count words", "how many words", "number of words"],
        "char_count": ["character count", "count characters", "how many characters", "char count", "length"],
        "reverse": ["reverse", "backwards", "flip"],
        "title_case": ["title case", "title", "capitalize"],
    }

    def can_handle(self, user_input: str) -> float:
        """Score how well this tool matches the input."""
        lower = user_input.lower()

        # Check for explicit operation keywords
        for keywords in self._OPERATION_KEYWORDS.values():
            for kw in keywords:
                if kw in lower:
                    return 0.9

        # Generic text-processing hints
        text_hints = ["text", "string", "convert", "process"]
        if any(hint in lower for hint in text_hints):
            return 0.5

        return 0.0

    def execute(self, user_input: str) -> str:
        """Parse the input, detect the operation, and apply it."""
        lower = user_input.lower()
        operation = self._detect_operation(lower)
        text = self._extract_text(user_input)

        if operation == "uppercase":
            return text.upper()
        elif operation == "lowercase":
            return text.lower()
        elif operation == "word_count":
            count = len(text.split())
            return f"Word count: {count}"
        elif operation == "char_count":
            return f"Character count: {len(text)}"
        elif operation == "reverse":
            return text[::-1]
        elif operation == "title_case":
            return text.title()
        else:
            # Default: uppercase (most commonly requested)
            return text.upper()

    def _detect_operation(self, lower_input: str) -> str:
        """Determine which text operation the user wants."""
        for operation, keywords in self._OPERATION_KEYWORDS.items():
            for kw in keywords:
                if kw in lower_input:
                    return operation
        return "uppercase"

    def _extract_text(self, user_input: str) -> str:
        """
        Extract the target text from the user's input.

        Handles patterns like:
            - 'Convert "hello world" to uppercase'
            - "uppercase hello world"
            - "reverse the text: hello world"
        """
        # Try to find quoted text first
        quoted = re.findall(r'["\'](.+?)["\']', user_input)
        if quoted:
            return quoted[0]

        # Try "text: <content>" or "text <content>" patterns
        colon_match = re.search(r':\s*(.+)$', user_input)
        if colon_match:
            return colon_match.group(1).strip()

        # Remove operation keywords and return the rest
        cleaned = user_input
        for keywords in self._OPERATION_KEYWORDS.values():
            for kw in keywords:
                cleaned = re.sub(re.escape(kw), '', cleaned, flags=re.IGNORECASE)

        # Remove common filler words
        for word in ["convert", "to", "the", "text", "of", "please", "make", "it"]:
            cleaned = re.sub(r'\b' + word + r'\b', '', cleaned, flags=re.IGNORECASE)

        cleaned = cleaned.strip().strip('"\'')
        return cleaned if cleaned else user_input
