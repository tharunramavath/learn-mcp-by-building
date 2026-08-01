"""
server_basic.py — STEP 1: your very first MCP server (offline).

This server has NO internet dependencies. It teaches the three MCP
primitives with three tiny things:

  * 3 TOOLS      — greet(), add(), multiply()   (functions the AI can call)
  * 1 RESOURCE   — config://app                  (read-only data the app can load)
  * 1 PROMPT     — math-help                     (a reusable instruction template)

Run it:  python server_basic.py
It will just sit there waiting — a client (see test_client_basic.py) has to
start it and talk to it. A stdio server never prints anything to the console.
"""

import logging

from mcp.server import MCPServer

# The golden rule for stdio servers: NEVER use print().
# stdout is the protocol channel. Use logging (goes to stderr) instead.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("server-basic")

# One line to create an MCP server. Give it a name.
mcp = MCPServer("calculator")

# A small in-memory "database" that our resource below will serve.
APP_CONFIG = {
    "app_name": "mcp-tutorial-calculator",
    "version": "1.0.0",
    "description": "A tiny MCP server that greets people and does math.",
    "author": "you",
}


# ---------------------------------------------------------------------------
# TOOLS
# ---------------------------------------------------------------------------
# A @tool is a function the AI model can decide to call.
# The SDK turns your type hints + docstring into the tool's input schema.
# ---------------------------------------------------------------------------


@mcp.tool()
def greet(name: str) -> str:
    """Greet a person warmly.

    Args:
        name: The name of the person to greet.
    """
    return f"Hello, {name}! Welcome to your first MCP server."


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together.

    Args:
        a: The first number.
        b: The second number.
    """
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers together.

    Args:
        a: The first number.
        b: The second number.
    """
    return a * b


# ---------------------------------------------------------------------------
# RESOURCES
# ---------------------------------------------------------------------------
# A @resource exposes read-only data. The app (not the model) loads it to
# give the model context. The function runs only when someone reads the URI.
# ---------------------------------------------------------------------------


@mcp.resource(
    "config://app",
    mime_type="application/json",
    description="Static configuration describing this MCP server.",
)
def get_app_config() -> dict:
    """Serve the APP_CONFIG dictionary as a JSON resource."""
    return APP_CONFIG


# ---------------------------------------------------------------------------
# PROMPTS
# ---------------------------------------------------------------------------
# A @prompt is a reusable template. The user invokes it explicitly; it tells
# the model how to act. Here it returns the chat messages to send the model.
# ---------------------------------------------------------------------------


@mcp.prompt()
def math_help(problem: str) -> list[dict]:
    """Create a template that instructs the model to solve a math problem step by step.

    Args:
        problem: The math problem the user wants solved.
    """
    return [
        {
            "role": "user",
            "content": (
                "You are a patient math tutor. Solve this problem step by step, "
                "showing each step clearly. When useful, use the calculator tools "
                "(add, multiply) rather than doing arithmetic in your head.\n\n"
                f"Problem: {problem}"
            ),
        }
    ]


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logger.info("Starting calculator server over stdio...")
    # stdio = the server talks JSON-RPC over stdin/stdout to whoever spawned it.
    mcp.run(transport="stdio")
