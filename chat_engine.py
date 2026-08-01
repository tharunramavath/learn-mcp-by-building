"""
chat_engine.py — STEP 7: the LLM agent loop that drives the chat UI.

This is the "brain" between the user, the Groq LLM, and the MCP host:

    user message
        -> send conversation + tool schemas to Groq
        -> Groq either answers OR requests tool calls
        -> if tool calls: execute them via MCPHost, append results as
          `role="tool"` messages, loop back to Groq
        -> repeat until Groq answers with plain text (max rounds)

Groq uses the same function-calling protocol as OpenAI: you pass `tools`
(a list of {type, function} schemas) and it returns `message.tool_calls`.

This module is deliberately UI-free so you can test the loop from the CLI.
"""

from __future__ import annotations

import json
from typing import Any, cast

from groq import Groq
from groq.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

from mcp_host import MCPHost

SYSTEM_PROMPT = (
    "You are a helpful assistant connected to real MCP servers. "
    "You have tools available that talk to those servers. "
    "Use them to answer questions accurately (e.g. do the math or fetch "
    "real weather data) instead of guessing. When you use a tool, briefly "
    "mention what you did. If a tool errors, tell the user what went wrong."
)

MAX_TOOL_ROUNDS = 5


def _extract_tool_result(result: Any) -> str:
    """Flatten an MCP call_tool result into plain text for the LLM."""
    parts = []
    for content in result.content:
        parts.append(getattr(content, "text", str(content)))
    return "\n".join(parts) if parts else "(tool returned nothing)"


def run_agent_turn(
    client: Groq,
    model: str,
    host: MCPHost,
    tools: list[dict[str, Any]],
    messages: list[dict[str, str]],
) -> tuple[str, list[dict[str, Any]]]:
    """Run one user turn. Returns (assistant_reply, trace).

    The trace is a list of {"tool", "arguments", "result"} dicts describing
    every MCP tool the LLM called, for the UI to display.
    """
    # Local copy; we mutate it as tool results come back.
    conversation: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *messages,
    ]
    trace: list[dict[str, Any]] = []
    reply = ""

    for _round in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=model,
            messages=cast(list[ChatCompletionMessageParam], conversation),
            tools=cast(list[ChatCompletionToolParam], tools),
        )
        message = response.choices[0].message

        if not message.tool_calls:
            # Groq answered with plain text — we're done.
            reply = message.content or ""
            break

        # Record the assistant message (including its tool_calls) so the API
        # sees the full exchange, then execute each requested tool.
        conversation.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ],
            }
        )

        for tc in message.tool_calls:
            name = tc.function.name
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}

            try:
                result = host.call_tool(name, args)
                result_text = _extract_tool_result(result)
            except Exception as e:  # surface tool errors to the LLM, don't crash
                result_text = f"Tool error: {e}"

            trace.append({"tool": name, "arguments": args, "result": result_text})
            conversation.append(
                {"role": "tool", "tool_call_id": tc.id, "content": result_text}
            )

    if not reply:
        reply = "I hit the tool-call limit before I could finish. Please try again."

    return reply, trace
