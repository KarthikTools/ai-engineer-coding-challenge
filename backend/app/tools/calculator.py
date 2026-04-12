"""
CalculatorTool — handles basic arithmetic operations.

Supports: +, -, *, /, parentheses, and common math phrases like
"what is 3 plus 5" or "calculate 10 / 2".
"""

import re
import ast
from .base import BaseTool


class CalculatorTool(BaseTool):
    """Tool for evaluating basic arithmetic expressions safely."""

    @property
    def name(self) -> str:
        return "CalculatorTool"

    @property
    def description(self) -> str:
        return "Evaluates basic arithmetic expressions (add, subtract, multiply, divide)"

    # Mapping of word-based operators to symbols
    _WORD_TO_OPERATOR = {
        "plus": "+", "add": "+", "added": "+", "sum": "+",
        "minus": "-", "subtract": "-", "subtracted": "-", "difference": "-",
        "times": "*", "multiply": "*", "multiplied": "*", "product": "*",
        "divided by": "/", "divide": "/", "over": "/",
        "modulo": "%", "mod": "%", "remainder": "%",
        "power": "**", "to the power of": "**", "raised to": "**",
    }

    # Allowed AST node types for safe evaluation
    _ALLOWED_NODES = {
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow,
        ast.FloorDiv, ast.USub, ast.UAdd,
    }

    def can_handle(self, user_input: str) -> float:
        """Score how well this tool matches the input."""
        lower = user_input.lower()

        # Check for math operation words
        math_words = [
            "calculate", "compute", "math", "arithmetic",
            "plus", "minus", "times", "divided", "multiply", "add",
            "subtract", "sum", "difference", "product",
        ]
        if any(word in lower for word in math_words):
            return 0.9

        # Check for arithmetic expression pattern (e.g., "3 + 5")
        if re.search(r'\d+\s*[+\-*/^%]\s*\d+', user_input):
            return 0.85

        # Check if it's mostly numbers and operators
        cleaned = re.sub(r'[^0-9+\-*/().%\s]', '', user_input).strip()
        if cleaned and len(cleaned) / max(len(user_input.strip()), 1) > 0.6:
            return 0.7

        return 0.0

    def execute(self, user_input: str) -> str:
        """Parse and safely evaluate the arithmetic expression."""
        expression = self._normalize_expression(user_input)

        if not expression:
            raise ValueError("Could not parse a valid arithmetic expression from the input.")

        result = self._safe_eval(expression)
        # Format nicely: remove trailing .0 for whole numbers
        if isinstance(result, float) and result.is_integer():
            result = int(result)

        return f"{expression} = {result}"

    def _normalize_expression(self, user_input: str) -> str:
        """Convert natural language math into a valid expression string."""
        text = user_input.lower().strip()

        # Remove common preambles
        for prefix in ["calculate", "compute", "what is", "what's", "evaluate", "solve"]:
            text = re.sub(r'^' + prefix + r'\s*', '', text)

        # Replace word operators with symbols (longer phrases first)
        for word, symbol in sorted(self._WORD_TO_OPERATOR.items(), key=lambda x: -len(x[0])):
            text = text.replace(word, f" {symbol} ")

        # Replace ^ with **
        text = text.replace('^', '**')

        # Keep only valid math characters
        text = re.sub(r'[^0-9+\-*/.()%\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def _safe_eval(self, expression: str) -> float:
        """
        Safely evaluate a math expression using AST parsing.

        Security: We only allow numeric literals and arithmetic operators.
        No function calls, imports, or variable access.
        """
        try:
            tree = ast.parse(expression, mode='eval')
        except SyntaxError:
            raise ValueError(f"Invalid mathematical expression: '{expression}'")

        # Validate every node in the AST
        for node in ast.walk(tree):
            if type(node) not in self._ALLOWED_NODES:
                raise ValueError(
                    f"Unsafe expression — disallowed operation: {type(node).__name__}"
                )

        result = eval(compile(tree, '<expression>', 'eval'))

        if not isinstance(result, (int, float)):
            raise ValueError("Expression did not produce a numeric result.")

        return float(result)
