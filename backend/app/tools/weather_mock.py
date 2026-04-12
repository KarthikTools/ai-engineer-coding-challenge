"""
WeatherMockTool — returns simulated weather data for any city.

No external API calls — uses deterministic mock data seeded from the city name
so the same city always returns the same weather (good for testing).
"""

import hashlib
import re
from .base import BaseTool


class WeatherMockTool(BaseTool):
    """Tool that returns mock weather data for a given city."""

    @property
    def name(self) -> str:
        return "WeatherMockTool"

    @property
    def description(self) -> str:
        return "Returns mock weather information for a given city"

    _CONDITIONS = [
        "Sunny", "Partly Cloudy", "Cloudy", "Rainy",
        "Thunderstorms", "Snowy", "Foggy", "Windy", "Clear",
    ]

    _WEATHER_KEYWORDS = [
        "weather", "temperature", "forecast", "climate",
        "hot", "cold", "rain", "sunny", "cloudy", "snow",
        "degrees", "celsius", "fahrenheit",
    ]

    _CITY_PREPOSITIONS = ["in", "for", "at", "of"]

    def can_handle(self, user_input: str) -> float:
        """Score how well this tool matches the input."""
        lower = user_input.lower()

        if any(kw in lower for kw in self._WEATHER_KEYWORDS):
            return 0.9

        return 0.0

    def execute(self, user_input: str) -> str:
        """Extract city name and return mock weather data."""
        city = self._extract_city(user_input)

        if not city:
            return "Please specify a city. Example: 'What's the weather in Tokyo?'"

        weather = self._generate_weather(city)
        return (
            f"Weather for {city.title()}:\n"
            f"  Temperature: {weather['temp_c']}°C ({weather['temp_f']}°F)\n"
            f"  Condition: {weather['condition']}\n"
            f"  Humidity: {weather['humidity']}%\n"
            f"  Wind: {weather['wind_kph']} km/h"
        )

    def _extract_city(self, user_input: str) -> str:
        """
        Extract the city name from the user's input.

        Handles patterns like:
            - "weather in New York"
            - "What's the temperature in London?"
            - "Tokyo weather"
        """
        text = user_input.strip()

        # Try "weather in <city>" pattern
        for prep in self._CITY_PREPOSITIONS:
            pattern = rf'{prep}\s+([A-Za-z\s]+?)[\?\.\!]*$'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Try "<city> weather" pattern
        match = re.match(r'^([A-Za-z\s]+?)\s+weather', text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try quoted city name
        quoted = re.findall(r'["\'](.+?)["\']', text)
        if quoted:
            return quoted[0]

        # Last resort: remove known keywords and return what's left
        cleaned = text
        for kw in self._WEATHER_KEYWORDS + ["what", "is", "the", "whats", "what's", "tell", "me", "about", "get", "?", ".", "!"]:
            cleaned = re.sub(r'\b' + re.escape(kw) + r'\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip().strip('?!.')

        return cleaned if cleaned else ""

    def _generate_weather(self, city: str) -> dict:
        """
        Generate deterministic mock weather based on city name.

        Using a hash ensures the same city always returns the same weather,
        making tests predictable while still appearing varied.
        """
        seed = int(hashlib.md5(city.lower().encode(), usedforsecurity=False).hexdigest(), 16)

        temp_c = (seed % 45) - 5  # Range: -5°C to 39°C
        condition_idx = seed % len(self._CONDITIONS)
        humidity = 30 + (seed % 60)  # Range: 30% to 89%
        wind = 5 + (seed % 40)  # Range: 5 to 44 km/h

        return {
            "temp_c": temp_c,
            "temp_f": round(temp_c * 9 / 5 + 32, 1),
            "condition": self._CONDITIONS[condition_idx],
            "humidity": humidity,
            "wind_kph": wind,
        }
