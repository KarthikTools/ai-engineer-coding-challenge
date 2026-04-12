"""
Unit tests for the three tools: TextProcessor, Calculator, WeatherMock.

These tests validate:
    - Correct execution of each tool's logic
    - Proper confidence scoring via can_handle()
    - Edge case handling
"""

import pytest
from app.tools import TextProcessorTool, CalculatorTool, WeatherMockTool


# ── TextProcessorTool ──────────────────────────────────────────────────────

class TestTextProcessorTool:

    def setup_method(self):
        self.tool = TextProcessorTool()

    def test_name(self):
        assert self.tool.name == "TextProcessorTool"

    def test_uppercase(self):
        result = self.tool.execute('Convert "hello world" to uppercase')
        assert result == "HELLO WORLD"

    def test_lowercase(self):
        result = self.tool.execute('Convert "HELLO WORLD" to lowercase')
        assert result == "hello world"

    def test_word_count(self):
        result = self.tool.execute('Word count of "the quick brown fox"')
        assert "4" in result

    def test_char_count(self):
        result = self.tool.execute('Character count of "hello"')
        assert "5" in result

    def test_reverse(self):
        result = self.tool.execute('Reverse "hello"')
        assert result == "olleh"

    def test_title_case(self):
        result = self.tool.execute('Title case "hello world"')
        assert result == "Hello World"

    def test_can_handle_high_confidence(self):
        assert self.tool.can_handle("convert to uppercase") >= 0.8

    def test_can_handle_low_confidence(self):
        assert self.tool.can_handle("calculate 3 + 5") < 0.5

    def test_can_handle_no_match(self):
        assert self.tool.can_handle("weather in tokyo") == 0.0


# ── CalculatorTool ─────────────────────────────────────────────────────────

class TestCalculatorTool:

    def setup_method(self):
        self.tool = CalculatorTool()

    def test_name(self):
        assert self.tool.name == "CalculatorTool"

    def test_simple_addition(self):
        result = self.tool.execute("3 + 5")
        assert "8" in result

    def test_subtraction(self):
        result = self.tool.execute("10 - 3")
        assert "7" in result

    def test_multiplication(self):
        result = self.tool.execute("4 * 6")
        assert "24" in result

    def test_division(self):
        result = self.tool.execute("20 / 4")
        assert "5" in result

    def test_natural_language(self):
        result = self.tool.execute("calculate 3 plus 5")
        assert "8" in result

    def test_complex_expression(self):
        result = self.tool.execute("(10 + 5) * 2")
        assert "30" in result

    def test_can_handle_high_confidence(self):
        assert self.tool.can_handle("calculate 3 + 5") >= 0.8

    def test_can_handle_arithmetic_pattern(self):
        assert self.tool.can_handle("3 + 5") >= 0.7

    def test_can_handle_no_match(self):
        assert self.tool.can_handle("convert to uppercase") == 0.0

    def test_safe_eval_rejects_imports(self):
        with pytest.raises(ValueError):
            self.tool.execute("__import__('os').system('ls')")


# ── WeatherMockTool ────────────────────────────────────────────────────────

class TestWeatherMockTool:

    def setup_method(self):
        self.tool = WeatherMockTool()

    def test_name(self):
        assert self.tool.name == "WeatherMockTool"

    def test_weather_response(self):
        result = self.tool.execute("weather in Tokyo")
        assert "Tokyo" in result
        assert "°C" in result
        assert "Humidity" in result

    def test_deterministic_results(self):
        """Same city should always return the same weather."""
        result1 = self.tool.execute("weather in London")
        result2 = self.tool.execute("weather in London")
        assert result1 == result2

    def test_different_cities_different_results(self):
        result1 = self.tool.execute("weather in London")
        result2 = self.tool.execute("weather in Tokyo")
        assert result1 != result2

    def test_can_handle_high_confidence(self):
        assert self.tool.can_handle("weather in Tokyo") >= 0.8

    def test_can_handle_no_match(self):
        assert self.tool.can_handle("calculate 3 + 5") == 0.0

    def test_city_extraction_preposition(self):
        result = self.tool.execute("What's the weather in New York?")
        assert "New York" in result

    def test_no_city(self):
        result = self.tool.execute("weather")
        assert "specify a city" in result.lower() or "Weather" in result
