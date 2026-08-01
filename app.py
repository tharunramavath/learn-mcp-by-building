"""
app.py — STEP 7: chat with your MCP servers from a Streamlit UI.

Run it:   streamlit run app.py        (or double-click run-chat.cmd)

How it works:
    This app is an MCP *host*. You pick a server (calculator or weather),
    enter a Groq API key, and chat. When the LLM decides it needs a tool, the
    app calls the MCP server over stdio and feeds the result back — you watch
    every tool call in the "agent trace" under each reply.

Flow:
    1. Sidebar: Groq API key + model + server  ->  Connect
    2. app.py spawns the MCP server via MCPHost (mcp_host.py)
    3. app.py discovers tools/resources/prompts and shows them
    4. Each message goes through the Groq agent loop (chat_engine.py)
    5. Tool calls are routed back to the MCP server via MCPHost
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st
from groq import Groq

from chat_engine import run_agent_turn
from mcp_host import MCPHost

BASE_DIR = Path(__file__).resolve().parent

# server label -> server script
SERVERS = {
    "calculator (offline tools)": "server_basic.py",
    "weather (India, live API)": "server_weather.py",
}

# A few Groq models that support tool calling well. "Custom" unlocks a text box.
GROQ_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-20b",
    "qwen/qwen3.6-27b",
    "Custom…",
]

MAX_MESSAGES_IN_CONTEXT = 20  # keep the LLM call small


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------


def init_state() -> None:
    st.session_state.setdefault("host", None)  # MCPHost or None
    st.session_state.setdefault("server_file", None)
    st.session_state.setdefault("tools", [])  # discovered MCP tools
    st.session_state.setdefault("resources", [])
    st.session_state.setdefault("prompts", [])
    st.session_state.setdefault("messages", [])  # chat history
    st.session_state.setdefault("trace", [])  # last turn's tool calls
    st.session_state.setdefault("groq_client", None)
    st.session_state.setdefault("last_trace_turn", 0)


# ---------------------------------------------------------------------------
# Sidebar helpers
# ---------------------------------------------------------------------------


def connect(server_label: str, model: str) -> None:
    """Spawn the selected MCP server and discover its primitives."""
    # Tear down any previous connection first.
    disconnect()

    server_file = str(BASE_DIR / SERVERS[server_label])
    try:
        host = MCPHost(server_file)
        host.connect()
    except Exception as e:  # spawn/initialize failure
        st.error(f"Could not connect to the MCP server: {e}")
        return

    st.session_state.host = host
    st.session_state.server_file = server_file

    # Discovery — the same three calls the test client makes.
    st.session_state.tools = host.list_tools()
    st.session_state.resources = host.list_resources()
    st.session_state.prompts = host.list_prompts()
    st.session_state.groq_client = Groq(api_key=st.session_state.api_key)
    st.success(
        f"Connected to **{server_label}** and found "
        f"{len(st.session_state.tools)} tool(s), "
        f"{len(st.session_state.resources)} resource(s), "
        f"{len(st.session_state.prompts)} prompt(s)."
    )
    st.session_state.messages = []  # start fresh for the new server


def disconnect() -> None:
    host = st.session_state.get("host")
    if host is not None:
        host.disconnect()
    st.session_state.host = None
    st.session_state.groq_client = None


# ---------------------------------------------------------------------------
# Sidebar UI
# ---------------------------------------------------------------------------


def render_sidebar() -> tuple[str, str]:
    st.sidebar.title("MCP Chat")
    st.sidebar.caption(
        "An MCP **host** in a browser: pick a server, connect, and chat. "
        "The LLM calls the server's real tools."
    )

    api_key = st.sidebar.text_input(
        "Groq API key",
        type="password",
        value=os.environ.get("GROQ_API_KEY", ""),
        help="Get one at https://console.groq.com/keys. Stored only in this "
        "browser session, never written to disk.",
    )
    st.session_state.api_key = api_key

    model_choice = st.sidebar.selectbox("Groq model", GROQ_MODELS)
    model = (
        st.sidebar.text_input("Custom model ID", value="llama-3.3-70b-versatile")
        if model_choice == "Custom…"
        else model_choice
    )

    server_label = st.sidebar.selectbox("MCP server", list(SERVERS.keys()))

    col1, col2 = st.sidebar.columns(2)
    if col1.button("Connect", use_container_width=True):
        if not api_key.strip():
            st.sidebar.error("Enter a Groq API key first.")
        else:
            connect(server_label, model)
    if col2.button("Disconnect", use_container_width=True):
        disconnect()
        st.rerun()

    st.sidebar.divider()

    # ---- Discovered primitives (read-only views) ----
    with st.sidebar.expander("Tools", expanded=False):
        for t in st.session_state.tools:
            st.markdown(f"**{t.name}**  \n{t.description or ''}")

    with st.sidebar.expander("Resources", expanded=False):
        for r in st.session_state.resources:
            st.markdown(f"- `{r.uri}`")

    with st.sidebar.expander("Prompts", expanded=False):
        for p in st.session_state.prompts:
            st.markdown(f"- `{p.name}`")

    return model, server_label


# ---------------------------------------------------------------------------
# Main chat area
# ---------------------------------------------------------------------------


def render_chat(model: str) -> None:
    st.header("Chat with your MCP server")

    if st.session_state.host is None:
        st.info("Connect to a server in the sidebar, then start chatting.")
        return

    host: MCPHost = st.session_state.host

    # Re-render the conversation.
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Show the tool calls that produced this assistant reply.
            if (
                msg["role"] == "assistant"
                and i == st.session_state.last_trace_turn
                and st.session_state.trace
            ):
                with st.expander("Agent trace (MCP tool calls)", expanded=False):
                    for call in st.session_state.trace:
                        st.markdown(f"**{call['tool']}** args={call['arguments']}")
                        st.code(call["result"])

    prompt = st.chat_input(
        'Try: "What is 17 * 23?" or "What is the weather in Mumbai?"'
    )
    if not prompt:
        return

    # Append the user message.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build the tool schemas for the LLM from the discovered MCP tools.
    tools = [host.tool_to_function_schema(t) for t in st.session_state.tools]

    # Keep the context window bounded.
    context = st.session_state.messages[-MAX_MESSAGES_IN_CONTEXT:]

    with st.chat_message("assistant"):
        with st.spinner("Thinking… calling MCP tools if needed…"):
            try:
                reply, trace = run_agent_turn(
                    st.session_state.groq_client,
                    model,
                    host,
                    tools,
                    context,
                )
            except Exception as e:
                st.error(f"Groq call failed: {e}")
                return

        st.markdown(reply)
        if trace:
            with st.expander("Agent trace (MCP tool calls)", expanded=True):
                for call in trace:
                    st.markdown(f"**{call['tool']}** args={call['arguments']}")
                    st.code(call["result"])

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.trace = trace
    st.session_state.last_trace_turn = len(st.session_state.messages) - 1


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    st.set_page_config(page_title="MCP Chat", page_icon="🔌", layout="wide")
    init_state()
    model, _ = render_sidebar()
    render_chat(model)


if __name__ == "__main__":
    main()
