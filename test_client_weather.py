"""
test_client_weather.py — tests the weather server (server_weather.py).

Calls the two weather tools against the live Open-Meteo API (no API key
needed). Requires internet access. Users only type a city name — the server
resolves it to a latitude/longitude internally.

Run it:  python test_client_weather.py
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_FILE = "server_weather.py"


def banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


async def main() -> None:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_FILE],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            banner("1. DISCOVERY")
            print("Server capabilities:", session.server_capabilities)
            print("Server info        :", session.server_info)

            banner("2. LIST TOOLS")
            for t in (await session.list_tools()).tools:
                print(f"\n- {t.name}: {t.description}")

            banner("3. CALL get_alerts(city='Mumbai')")
            result = await session.call_tool("get_alerts", {"city": "Mumbai"})
            print(result.content[0].text)

            banner("4. CALL get_forecast(city='New Delhi')")
            result = await session.call_tool("get_forecast", {"city": "New Delhi"})
            print(result.content[0].text)

            banner("5. READ RESOURCE weather://about")
            res = await session.read_resource("weather://about")
            for chunk in res.contents:
                print(getattr(chunk, "text", chunk))

            banner("DONE - weather server works against the live API")


if __name__ == "__main__":
    asyncio.run(main())
