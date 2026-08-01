"""
server_weather.py — STEP 5: the real-world upgrade (India edition).

Same MCP concepts as server_basic.py, but now the tools do something useful:
they call the free Open-Meteo API (https://open-meteo.com) over HTTP.

  * 2 TOOLS     — get_alerts(city), get_forecast(city)
  * 1 RESOURCE  — weather://about  (static info the app can load as context)
  * 1 PROMPT    — weather-report   (template that uses the tools)

Users just type a city name like "Mumbai". The server resolves it to a
latitude/longitude internally via Open-Meteo's geocoding API, then fetches the
weather. No lat/lon input needed from the caller.

Open-Meteo needs no API key. It only requires a real User-Agent header.

Run it:      python server_weather.py           (then connect a client)
Test it:     python test_client_weather.py
Explore it:  .\run-inspector.cmd  ->  pick the "weather" server
"""

import logging
from typing import Any

import httpx2
from mcp.server import MCPServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server-weather")

mcp = MCPServer("weather")

GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_API = "https://api.open-meteo.com/v1/forecast"
USER_AGENT = "mcp-tutorial/1.0 (your@email.com)"

# WMO weather codes -> plain-language description.
WMO_CODES: dict[int, str] = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


async def make_request(url: str, params: dict[str, Any]) -> dict[str, Any] | None:
    """GET a URL from Open-Meteo; return parsed JSON, or None on any error."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    async with httpx2.AsyncClient() as client:
        try:
            response = await client.get(
                url, params=params, headers=headers, timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:  # network error, 4xx/5xx, bad JSON, ...
            logger.error("Open-Meteo request failed for %s: %s", url, e)
            return None


async def geocode_city(city: str) -> dict[str, Any] | None:
    """Resolve a city name to its latitude/longitude (India only)."""
    city = city.strip()
    if not city:
        return None
    data = await make_request(
        GEOCODING_API,
        {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
            "countryCode": "IN",
        },
    )
    if not data or not data.get("results"):
        return None
    result = data["results"][0]
    return {
        "name": result.get("name", city),
        "admin1": result.get("admin1", ""),
        "latitude": result["latitude"],
        "longitude": result["longitude"],
    }


def describe_weather(code: int | None) -> str:
    if code is None:
        return "Unknown conditions"
    return WMO_CODES.get(code, "Unknown conditions")


# ---------------------------------------------------------------------------
# TOOLS
# ---------------------------------------------------------------------------


@mcp.tool()
async def get_alerts(city: str) -> str:
    """Get active weather advisories for a city in India.

    Alerts are derived heuristically from current conditions and today's /
    tomorrow's forecast (thunderstorm, heavy rain, fog, extreme heat). This is
    a free approximation, not the official IMD warning feed.

    Args:
        city: Name of an Indian city, e.g. Mumbai, New Delhi, Bengaluru, Chennai.
    """
    location = await geocode_city(city)
    if location is None:
        return f"Could not find '{city}' in India. Try another city name."

    data = await make_request(
        FORECAST_API,
        {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": "temperature_2m,weather_code",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min",
            "forecast_days": 2,
            "timezone": "auto",
        },
    )
    if data is None or "current" not in data or "daily" not in data:
        return f"Unable to fetch current conditions for {location['name']}."

    current = data["current"]
    daily = data["daily"]

    alerts: list[str] = []
    seen: set[str] = set()

    def add(period: str, message: str) -> None:
        key = f"{period}: {message}"
        if key not in seen:
            seen.add(key)
            alerts.append(f"- {key}")

    def check(period: str, code: int | None, temps: list[float | None]) -> None:
        if code in (95, 96, 99):
            add(period, "Thunderstorm expected - stay indoors where possible.")
        if code in (61, 63, 65, 80, 81, 82):
            add(period, "Rain / rain showers expected - carry an umbrella.")
        if code in (45, 48):
            add(period, "Fog possible - drive carefully and use fog lights.")
        hot = any(t is not None and t >= 40 for t in temps)
        cold = any(t is not None and t <= 5 for t in temps)
        if hot:
            add(period, "Extreme heat - stay hydrated and avoid the midday sun.")
        if cold:
            add(period, "Very cold conditions - dress warmly.")

    check("Now", current.get("weather_code"), [current.get("temperature_2m")])

    today_codes = daily.get("weather_code", [])
    today_maxes = daily.get("temperature_2m_max", [])
    today_mins = daily.get("temperature_2m_min", [])
    for i in range(min(2, len(today_codes))):
        label = "Today" if i == 0 else "Tomorrow"
        check(label, today_codes[i], [today_maxes[i], today_mins[i]])

    if not alerts:
        return f"No significant weather advisories for {location['name']} right now."
    return "\n".join(alerts)


@mcp.tool()
async def get_forecast(city: str) -> str:
    """Get the weather forecast for a city in India.

    Step 1: geocode the city name into a latitude/longitude (Open-Meteo).
    Step 2: fetch the daily forecast for those coordinates.

    Args:
        city: Name of an Indian city, e.g. Mumbai, New Delhi, Bengaluru, Chennai.
    """
    location = await geocode_city(city)
    if location is None:
        return f"Could not find '{city}' in India. Try another city name."

    data = await make_request(
        FORECAST_API,
        {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "forecast_days": 5,
            "timezone": "auto",
        },
    )
    if data is None or "daily" not in data:
        return f"Unable to fetch the forecast for {location['name']}."

    daily = data["daily"]
    days = daily.get("time", [])
    codes = daily.get("weather_code", [])
    maxes = daily.get("temperature_2m_max", [])
    mins = daily.get("temperature_2m_min", [])
    rain = daily.get("precipitation_probability_max", [])
    if not days:
        return f"No forecast available for {location['name']}."

    place = location["name"]
    if location["admin1"]:
        place = f"{place}, {location['admin1']}"

    lines = [f"Forecast for {place}:"]
    for i in range(len(days)):
        lines.append(
            f"- {days[i]}: {describe_weather(codes[i])}, "
            f"low {mins[i]} / high {maxes[i]} deg C, "
            f"{rain[i]}% chance of rain"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# RESOURCE
# ---------------------------------------------------------------------------


@mcp.resource(
    "weather://about",
    mime_type="text/markdown",
    description="Information about this weather MCP server and how to use its tools.",
)
def about_resource() -> str:
    return """# Weather MCP Server (India)

A minimal MCP server backed by the free [Open-Meteo API](https://open-meteo.com).

## Tools
- `get_alerts(city)` - weather advisories for an Indian city (e.g. `Mumbai`).
- `get_forecast(city)` - 5-day forecast for an Indian city.

## How it works
You only type a **city name**. The server resolves it to a latitude/longitude
internally using Open-Meteo's geocoding API, then fetches the forecast.

## Limitations
- Alerts are a heuristic based on current conditions, not the official IMD feed.
- Requires internet access to api.open-meteo.com.
"""


# ---------------------------------------------------------------------------
# PROMPT
# ---------------------------------------------------------------------------


@mcp.prompt()
def weather_report(city: str) -> list[dict]:
    """Create a template for a plain-language weather report.

    Args:
        city: Name of the city to report on.
    """
    return [
        {
            "role": "user",
            "content": (
                "You are a friendly local weather broadcaster. Produce a short, "
                "plain-language weather report. Use the get_forecast tool to get "
                "real data. If you also checked get_alerts, mention any active "
                "warnings first. Be concise and end with a helpful tip.\n\n"
                f"City: {city}"
            ),
        }
    ]


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting weather server over stdio...")
    mcp.run(transport="stdio")
