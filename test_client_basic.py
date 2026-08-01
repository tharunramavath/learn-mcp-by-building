"""
test_client_basic.py — STEP 2: a tiny MCP client that tests the calculator server.

This script is NOT your real MCP client (that's your AI app). It's a minimal
stand-in so you can watch the protocol work without a GUI.

What it does, in order:
  1. Spawns server_basic.py as a subprocess (stdio transport).
  2. Discovers what the server offers.
  3. Lists tools, resources, and prompts.
  4. Calls the `add` and `multiply` tools.
  5. Reads the `config://app` resource.
  6. Fetches the `math-help` prompt.

Run it:  python test_client_basic.py
"""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_FILE = "server_basic.py"


def banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


async def main() -> None:
    # Use the same Python interpreter that is running this script.
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_FILE],
    )

    # stdio_client starts the server process and gives us two pipes.
    # ClientSession turns those pipes into an MCP conversation.
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            banner("1. DISCOVERY — what the server can do")
            caps = session.server_capabilities
            print("Server capabilities:", caps)
            print("Server info        :", session.server_info)

            banner("2. LIST TOOLS")
            tools = (await session.list_tools()).tools
            for t in tools:
                print(f"\n- {t.name}: {t.description}")
                print(f"  inputSchema: {t.input_schema}")

            banner("3. LIST RESOURCES")
            resources = (await session.list_resources()).resources
            for r in resources:
                print(f"\n- {r.uri} ({r.mime_type}): {r.description}")

            banner("4. LIST PROMPTS")
            prompts = (await session.list_prompts()).prompts
            for p in prompts:
                print(f"\n- {p.name}: {p.description}")

            banner("5. CALL A TOOL: add(2, 3)")
            result = await session.call_tool("add", {"a": 2, "b": 3})
            print("Result:", result.content[0].text)

            banner("6. CALL A TOOL: multiply(4, 1.5)")
            result = await session.call_tool("multiply", {"a": 4, "b": 1.5})
            print("Result:", result.content[0].text)

            banner("7. CALL A TOOL: greet('Ada')")
            result = await session.call_tool("greet", {"name": "Ada"})
            print("Result:", result.content[0].text)

            banner("8. READ A RESOURCE: config://app")
            res = await session.read_resource("config://app")
            for chunk in res.contents:
                print("Resource contents:", getattr(chunk, "text", chunk))

            banner("9. GET A PROMPT: math-help")
            prompt = await session.get_prompt("math_help", {"problem": "17 * 23"})
            for msg in prompt.messages:
                content = getattr(msg.content, "text", msg.content)
                print(f"\n[{msg.role}] {content}")

            banner("DONE - all MCP primitives exercised successfully")

            # Session closes, server process is shut down automatically.


if __name__ == "__main__":
    asyncio.run(main())
