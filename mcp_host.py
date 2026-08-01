"""
mcp_host.py — STEP 7: a reusable MCP *host* (client side).

Until now you wrote MCP *servers* and a throwaway test client. This module is
the other half of the architecture: it is the **client/host** that any AI app
is — it spawns an MCP server, talks to it over stdio, discovers its primitives,
and calls its tools.

Why a background thread + asyncio loop?
    Streamlit is synchronous, but the MCP SDK client is async. So this host
    runs a real asyncio event loop on a daemon thread, and exposes plain,
    synchronous methods that schedule coroutines on that loop and block until
    they finish. The MCP server subprocess stays alive for the whole session.

    Important Windows/anyio detail: the whole MCP session (stdio transport +
    client session) lives in ONE long-lived coroutine on the loop. Opening the
    async context managers across multiple tasks breaks anyio's task-group
    bookkeeping ("cancel scope entered in a different task"), so we never do
    that. Individual calls (list_tools, call_tool, ...) are separate small
    coroutines submitted to the loop.

Usage:
    host = MCPHost("server_basic.py")
    host.connect()
    tools = host.list_tools()            # [Tool]
    host.call_tool("add", {"a": 2, "b": 3})
    host.disconnect()
"""

from __future__ import annotations

import asyncio
import sys
import threading
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPHost:
    """A synchronous wrapper around an async MCP client session."""

    def __init__(self, server_file: str) -> None:
        # Spawn the server with the SAME interpreter that runs this app.
        # That guarantees the venv's `mcp` package is the one the server imports.
        self.server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_file],
        )
        self._loop: asyncio.AbstractEventLoop | None = None
        self._thread: threading.Thread | None = None
        self._session: ClientSession | None = None
        self._session_task: Any = None

        # Cross-thread signals: the session coroutine runs on the background
        # loop; these events let the main thread wait for it to be ready/done.
        self._ready = threading.Event()
        self._done = threading.Event()
        self._startup_error: BaseException | None = None
        self.connected = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Start the background loop and open the MCP session."""
        if self.connected:
            return

        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(
            target=self._loop.run_forever,
            daemon=True,
            name="mcp-host-loop",
        )
        self._thread.start()

        # Launch the long-lived session coroutine on the loop. It owns every
        # async context manager (stdio transport + client session) so anyio
        # never sees them opened in one task and closed in another. Keep the
        # future so disconnect() can await the cleanup instead of polling.
        self._session_task = asyncio.run_coroutine_threadsafe(
            self._run_session(), self._loop
        )

        # Block the calling thread until the session is up (or failed).
        if not self._ready.wait(timeout=30):
            raise TimeoutError("Timed out connecting to the MCP server.")
        if self._startup_error is not None:
            raise self._startup_error
        self.connected = True

    async def _run_session(self) -> None:
        """Open the stdio transport + client session and keep them alive."""
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    self._session = session
                    self._ready.set()
                    # Park here until disconnect() signals, keeping the
                    # transport + subprocess alive the whole time.
                    await asyncio.get_running_loop().run_in_executor(
                        None, self._done.wait
                    )
        except BaseException as e:  # surface startup failures to connect()
            self._startup_error = e
            self._ready.set()
        finally:
            self.connected = False
            self._done.set()

    def disconnect(self) -> None:
        """Close the session, the server process, and the loop."""
        if not self.connected or self._loop is None:
            return
        # Unblock the parked session coroutine, then wait for it to finish
        # closing the transport (which kills the server subprocess).
        self._done.set()
        if self._session_task is not None:
            try:
                self._session_task.result(timeout=15)
            except Exception:
                pass  # session cleanup already failed; fall through to stop loop
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)
        self._loop.close()
        self._loop = None
        self._thread = None
        self._session = None
        self._session_task = None
        self.connected = False

    # ------------------------------------------------------------------
    # Async -> sync bridge
    # ------------------------------------------------------------------

    def _run(self, coro: Any) -> Any:
        """Schedule a coroutine on the background loop and block for its result."""
        if self._loop is None or self._session is None:
            raise RuntimeError("Not connected. Call connect() first.")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result()

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def list_tools(self) -> list[Any]:
        return self._run(self._session.list_tools()).tools

    def list_resources(self) -> list[Any]:
        return self._run(self._session.list_resources()).resources

    def list_prompts(self) -> list[Any]:
        return self._run(self._session.list_prompts()).prompts

    # ------------------------------------------------------------------
    # Invocation
    # ------------------------------------------------------------------

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        return self._run(self._session.call_tool(name, arguments))

    def read_resource(self, uri: str) -> str:
        """Read a resource and flatten its content parts to plain text."""
        result = self._run(self._session.read_resource(uri))
        parts = []
        for chunk in result.contents:
            parts.append(getattr(chunk, "text", str(chunk)))
        return "\n".join(parts)

    def get_prompt(self, name: str, arguments: dict[str, Any]) -> list[dict[str, str]]:
        """Fetch a prompt template and convert its messages to plain dicts."""
        result = self._run(self._session.get_prompt(name, arguments))
        messages = []
        for msg in result.messages:
            content = getattr(msg.content, "text", str(msg.content))
            messages.append({"role": msg.role, "content": content})
        return messages

    # ------------------------------------------------------------------
    # Schema conversion: MCP tool -> LLM function-calling tool
    # ------------------------------------------------------------------

    def tool_to_function_schema(self, tool: Any) -> dict[str, Any]:
        """Turn an MCP Tool into an OpenAI/Groq-style function tool schema."""
        return {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,  # already a JSON Schema
            },
        }
