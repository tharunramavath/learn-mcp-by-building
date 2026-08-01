# Learn MCP by Building an MCP Server

> **The hands-on guide to the Model Context Protocol.** Build a calculator
> server, test it the way real AI apps do, upgrade it into a live weather
> server, and finally build **your own AI host** — a chat UI where an LLM calls
> your tools for real.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB)](https://www.python.org)
[![MCP SDK 2.x](https://img.shields.io/badge/MCP%20SDK-2.x-000000)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build time](https://img.shields.io/badge/build%20time-2%E2%80%933%20hours-brightgreen)]()

**MCP (Model Context Protocol)** is the open standard that lets AI apps (Claude,
ChatGPT, VS Code, Cursor) talk to your tools and data — **"USB-C for AI"**.
This repo is a from-zero, **build-it-yourself** tutorial: every concept becomes
a file you write, run, and break on purpose. No AI/ML background needed.

---

## Who this is for

- Developers who want to understand MCP by **building**, not just reading.
- Python users comfortable with functions, async, and JSON.
- People who learn best when they can **see the protocol wire traffic** fly by.

You do **not** need any AI/ML background, an API key, or an LLM for Steps 1–6.

---

## What you'll build

| Step | You build | You learn |
|------|-----------|-----------|
| 0 | Your environment | The Python MCP SDK |
| 1 | `server_basic.py` — an offline calculator server | The 3 primitives: **tools, resources, prompts** |
| 2 | `test_client_basic.py` — a tiny client | The whole JSON-RPC conversation |
| 3 | MCP Inspector | Visual tool-calling + raw protocol traffic |
| 4 | A real AI app (Claude / VS Code / Cursor) | What a **host** and client configs look like |
| 5 | `server_weather.py` — a live weather server | Async tools, external APIs, geocoding |
| 6 | — | The two layers & stateless discovery |
| 7 | `app.py` — your own AI host (chat UI) | Function calling driving real MCP tools |

---

## Quickstart (60 seconds)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python server_basic.py
```

That server **does nothing visible — by design**. It waits for a client. Open a
**second** terminal and talk to it:

```powershell
python test_client_basic.py
```

If you see discovery, tools, resources, prompts, and `add(2, 3) → 5.0` — you
just ran a full MCP conversation. Now go do the steps below.

---

## Table of contents

- [Read these docs first](#read-these-docs-first)
- [Project layout](#project-layout)
- [Step 0 — Setup](#step-0--setup-one-time)
- [Step 1 — Your first server](#step-1--your-first-server-server_basicpy)
- [Step 2 — Test it with a tiny client](#step-2--test-it-with-a-tiny-client-test_client_basicpy)
- [Step 3 — Explore with the MCP Inspector](#step-3--explore-with-the-mcp-inspector-visual-ui)
- [Step 4 — Attach to a real AI app](#step-4--attach-to-a-real-ai-app)
- [Step 5 — The real-world upgrade](#step-5--the-real-world-upgrade-server_weatherpy)
- [Step 6 — Under the hood](#step-6--under-the-hood-recommended-reading)
- [Step 7 — Become the host](#step-7--become-the-host-chat-with-your-servers-streamlit-ui)
- [Challenges](#challenges-do-these-yourself)
- [FAQ](#faq)
- [Where to go next](#where-to-go-next)
- [Troubleshooting](#troubleshooting)

---

## Read these docs first

> - `docs/00-learning-path.md` — **start here**: the recommended reading/doing order
> - `docs/01-concepts.md` — the theory: what MCP is, architecture, primitives
> - `docs/02-glossary.md` — a cheat-sheet of every term
> - `docs/03-inspector-v2-guide.md` — how the new Inspector v2 UI maps to the classic (v1) layout
> - `docs/04-mcp-vs-alternatives.md` — how MCP compares to plain function calling, provider tools, and REST APIs
> - `docs/05-faq.md` — a deeper FAQ than the short one at the bottom of this README

---

## Project layout

```
mcp-tutorial/
├── server_basic.py          STEP 1 - your first (offline) server
├── test_client_basic.py     STEP 2 - a tiny client that tests it
├── server_weather.py        STEP 5 - the real-world weather server
├── test_client_weather.py   STEP 5 - a client for the weather server
├── mcp_host.py              STEP 7 - the MCP host/client wrapper (sync bridge)
├── chat_engine.py           STEP 7 - the LLM agent loop (Groq function calling)
├── app.py                   STEP 7 - the Streamlit chat UI
├── run-chat.cmd             STEP 7 - double-click to launch the chat UI
├── claude_desktop_config.json  STEP 4 - config for Claude Desktop (edit the path)
├── .vscode/mcp.json         STEP 4 - config for VS Code
├── inspector.json           STEP 3 - Inspector catalog (launch config for both servers)
├── run-inspector.cmd        STEP 3 - double-click to launch the Inspector
├── requirements.txt
└── docs/
    ├── 00-learning-path.md   START HERE - the sequential reading order
    ├── 01-concepts.md
    ├── 02-glossary.md
    ├── 03-inspector-v2-guide.md
    ├── 04-mcp-vs-alternatives.md
    └── 05-faq.md
```

---

## Step 0 — Setup (one time)

```powershell
# From inside the mcp-tutorial/ folder:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

That installs the official Python MCP SDK (`mcp`) plus `httpx2` (the HTTP client
the weather server uses). Verify:

```powershell
python -c "from mcp.server import MCPServer; print('MCP SDK OK')"
```

### Prefer `uv`? (faster, modern alternative)

If you have [uv](https://docs.astral.sh/uv/) installed, you can skip the venv
setup entirely — the project has a `pyproject.toml`:

```powershell
uv sync            # creates .venv and installs all deps from pyproject.toml
uv run server_basic.py          # run the server
uv run test_client_basic.py     # run the test client
```

> **Windows note:** use `uv` for *running* scripts, but launch the Inspector with
> `npx @modelcontextprotocol/inspector --catalog inspector.json` instead of
> `uv run mcp dev` — see Step 3. If a GUI app says `'uv' is not recognized`,
> add uv's folder to your PATH permanently:
> `[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path","User") + ";$env:USERPROFILE\.local\bin", "User")`
> then fully restart the app.

---

## Step 1 — Your first server: `server_basic.py`

Open `server_basic.py` and read it top to bottom. It is ~90 lines and shows all
three primitives at once.

```python
from mcp.server import MCPServer

mcp = MCPServer("calculator")        # 1 line to create a server
```

### The 3 tools (what the AI can call)

```python
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together.
    Args:
        a: The first number.
        b: The second number.
    """
    return a + b
```

Three magic things happen here:

1. **`@mcp.tool()`** registers the function as an MCP tool.
2. The **type hints** (`a: float, b: float`) become the tool's input schema.
3. The **docstring** becomes the tool's description — this is what the AI model
   reads to decide when to call it. Write it like the model will read it.

### The 1 resource (read-only data)

```python
@mcp.resource("config://app", mime_type="application/json")
def get_app_config() -> dict:
    return APP_CONFIG
```

Resources have a **URI** (`config://app`). The app loads them to give the model
context — like opening a file.

### The 1 prompt (a template)

```python
@mcp.prompt()
def math_help(problem: str) -> list[dict]:
    return [{"role": "user", "content": f"You are a math tutor. Problem: {problem}"}]
```

Prompts are templates the **user** invokes explicitly (like a slash command).

### Run it

```powershell
python server_basic.py
```

It prints a log line and then just **sits there**. That is normal — a stdio
server waits for a client to spawn it and talk to it.

> **Why no output?** Over the `stdio` transport, your server's stdout *is* the
> protocol. If you `print()` anything, you corrupt the JSON-RPC messages and the
> server silently breaks. That's why we use `logging` (which goes to stderr).
> This is **the golden rule of stdio MCP servers** — see `docs/01-concepts.md`.

---

## Step 2 — Test it with a tiny client: `test_client_basic.py`

You don't need an AI app yet. This script is a minimal stand-in client that
connects to your server over stdio and drives the whole protocol.

```powershell
python test_client_basic.py
```

You'll see, in order:

1. **Discovery** — the client asks what the server supports (`server/discover`).
2. **List tools** — notice each tool's auto-generated `inputSchema`.
3. **List resources** — the `config://app` URI.
4. **List prompts** — `math_help`.
5. **Call tools** — `add(2, 3)` returns `5.0`.
6. **Read the resource** — your config JSON comes back.
7. **Get the prompt** — the template comes back.

That's the entire MCP conversation, end to end. The client code:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async with stdio_client(server_params) as (read, write):   # spawn server
    async with ClientSession(read, write) as session:      # open conversation
        await session.initialize()                         # handshake
        await session.list_tools()
        await session.call_tool("add", {"a": 2, "b": 3})
```

---

## Step 3 — Explore with the MCP Inspector (visual UI)

The official **MCP Inspector** is a web UI for poking at servers and watching
the raw JSON-RPC messages.

This project ships an `inspector.json` catalog that tells the Inspector how to
launch both servers using **paths relative to this folder** (no `uv`, no PATH
lookup, no machine-specific paths).

**Easiest way — double-click `run-inspector.cmd`**, or run it from the terminal:

```powershell
.\run-inspector.cmd
```

Or invoke npx directly:

```powershell
npx @modelcontextprotocol/inspector --catalog "<your-path>\mcp-tutorial\inspector.json"
```

The web UI opens at `http://localhost:6274` (the browser auto-launches; the URL
may carry an `MCP_INSPECTOR_API_TOKEN=` query param — keep it if you
bookmark the page). Pick a server (`calculator` or `weather`) from the catalog
and click **Connect**. Click around:

- **Tools / Resources / Prompts** tabs — browse what your server exposes.
- **Call a tool** — try `add` with `{"a": 10, "b": 5}`.
- **Protocol** tab — watch the actual JSON-RPC requests and responses fly by.
  This is where you *see* what Step 2 did programmatically.

> If the UI looks different from YouTube tutorials, that's because this project
> runs the new **Inspector v2**. See `docs/03-inspector-v2-guide.md` for a
> feature-by-feature map (transport type, command/args, pings, sampling, roots,
> protocol routes, etc.) to the v2 tabs.

> **Windows note:** avoid `mcp dev` / `uv run mcp dev` — it forces the Inspector
> to spawn your server via `uv`, which often fails on Windows (the Inspector's
> spawned process can't see `uv` on PATH). The `--catalog` approach above avoids
> that entirely by using relative paths to the venv Python. Also launch the
> Inspector from **PowerShell or cmd** (double-click `run-inspector.cmd`) rather
> than from Git Bash — the MSYS environment mis-resolves `node` for child
> processes and the Inspector dies with `spawn node ENOENT`. Only one Inspector
> can run at a time — if you see "PORT IS IN USE", close the existing
> tab/instance instead of starting another. First run downloads the Inspector
> via `npx` and takes a minute.

---

## Step 4 — Attach to a real AI app

Now the payoff: plug your server into an AI assistant you already use.

### Claude Desktop

Copy `claude_desktop_config.json` to your real config file:
`C:\Users\<you>\AppData\Roaming\Claude\claude_desktop_config.json`, then fully
restart Claude Desktop. Your `calculator` server will appear. Ask:
> *"Use the calculator server to multiply 17 by 23."*

The config tells Claude Desktop: *launch this server by running this Python
script*, then talk to it over stdio.

### VS Code

VS Code reads project-scoped MCP servers from `.vscode/mcp.json` (already
included). Open this folder in VS Code, then:

1. Open the command palette → **"MCP: List Servers"** / **"MCP: Add Server"**.
2. Or open **Copilot Chat** and use the MCP tools that appear.

### Cursor

Settings → **MCP** → **Add new global MCP server**, and paste the same JSON
shape from `claude_desktop_config.json`.

> **Paths in the config files:** `inspector.json` and `.vscode/mcp.json` use
> **relative paths** (`.venv\Scripts\python.exe`), so they work as long as you
> open the project folder. `claude_desktop_config.json` is a copy-paste example
> and uses a `<YOUR-PATH>` placeholder — replace it with the absolute path to
> your checkout before copying (Claude Desktop doesn't resolve relative paths).
> On Windows use double backslashes `\\` in JSON.

---

## Step 5 — The real-world upgrade: `server_weather.py`

Now you take what you learned and build something genuinely useful: a weather
server for **India** backed by the free [Open-Meteo API](https://open-meteo.com)
(no API key required).

Read `server_weather.py`. The MCP part is identical to Step 1 — what's new:

- **Async tools** — `async def` because we do I/O.
- **External API calls** — `httpx2` fetches live data; `make_request` wraps
  it with error handling so a network failure returns a friendly message
  instead of crashing.
- **City name geocoding** — users just type `Mumbai`, not coordinates.
  `geocode_city` resolves the name to a latitude/longitude internally via
  Open-Meteo's geocoding API. A classic real-world API pattern.
- **Heuristic alerts** — `get_alerts` derives advisories from current and
  near-term conditions (thunderstorm, heavy rain, fog, extreme heat), since
  India has no free keyless official alert feed.

Test it (needs internet):

```powershell
python test_client_weather.py
```

Then explore it in the Inspector (the `weather` server is already in the catalog):

```powershell
npx @modelcontextprotocol/inspector --catalog "<your-path>\mcp-tutorial\inspector.json"
```

Then plug it into VS Code / Claude Desktop using the `weather` entry already in
`.vscode/mcp.json` / `claude_desktop_config.json`, and ask:
> *"What's the weather like in Mumbai?"*

---

## Step 6 — Under the hood (recommended reading)

Read `docs/01-concepts.md` fully. The two ideas that make everything click:

1. **Two layers.** *Data layer* = the JSON-RPC 2.0 messages (what).
   *Transport layer* = how messages travel (stdio locally, Streamable HTTP
   remotely). Same messages, different plumbing.
2. **Stateless + discovery.** Every request carries the protocol version and
   capabilities; the client discovers what the server supports before using it.

Then try the challenges below.

---

## Step 7 — Become the host: chat with your servers (Streamlit UI)

So far your servers just sit and wait for a client. Now you build the other half
of MCP — the **host** (the AI app). This is a real chat UI in your browser that
spawns your servers, discovers their tools, and lets an LLM call them through
**function calling**.

Three files, each a distinct layer:

- **`mcp_host.py`** — a reusable MCP *client/host*. It spawns a server over
  stdio and exposes plain synchronous methods (`list_tools`, `call_tool`,
  `read_resource`, `get_prompt`, ...). MCP's Python SDK is async but Streamlit
  is sync, so it runs a real asyncio event loop on a background thread and
  bridges the two.
- **`chat_engine.py`** — the **agent loop**. It sends your message plus the
  discovered tool schemas to [Groq](https://console.groq.com/). If the model
  decides it needs a tool, the engine executes it on the server and feeds the
  result back, repeating until the model answers in plain text. That loop is
  *function calling* driving real MCP tools.
- **`app.py`** — the Streamlit UI. Pick a server, paste a Groq API key,
  connect, and chat. Every reply can show an **agent trace** of the real MCP
  tool calls that produced it.

Run it — double-click **`run-chat.cmd`**, or:

```powershell
python -m streamlit run app.py
```

The UI opens at `http://localhost:8501`. You need a free Groq API key
(https://console.groq.com/keys). Then:

1. Paste the key in the sidebar.
2. Pick the **calculator** server → **Connect**. The sidebar lists its
   discovered 3 tools, 1 resource, and 1 prompt.
3. Ask *"What is 17 * 23?"*. The **agent trace** under the reply shows the LLM
   called your real `multiply` tool and used its answer.
4. Switch to the **weather** server and ask *"What's the weather in Mumbai?"* —
   it geocodes the city and fetches live data, all via MCP.

> **Why this is the big finale:** every AI app is a host. Claude Desktop, VS
> Code, and Cursor do exactly what `app.py` does — spawn servers, discover
> tools, and call them on the model's behalf. You just built one from scratch.

---

## Challenges (do these yourself)

1. **Add a `divide` tool** to `server_basic.py`. What happens when `b == 0`?
2. **Add a resource template** — a resource with a URI like
   `weather://city/{city}` instead of a fixed URI.
3. **Make `server_basic.py` a remote server** — change the last line to
   `mcp.run(transport="streamable-http")` and see what URL it prints. (You'll
   need to configure a client for HTTP transport to talk to it.)
4. **Write your own tiny client** that takes a math question in English,
   extracts numbers, and calls your calculator tools.
5. **Add a tool to `server_basic.py`** and re-connect the chat UI — the host
   should discover it automatically. What happens if the LLM divides by zero?
6. **Swap the Groq model** in the chat sidebar. Which models call tools more
   reliably? (Watch the agent trace to see.)

---

## FAQ

**Do I need an API key or an AI model to follow along?**
No. Steps 1–6 need only Python. The only key in the whole project is the free
Groq key used in Step 7 (the host). You can go through the entire protocol
without ever touching an LLM.

**Why does my server "do nothing" when I run it?**
It's working. A stdio server doesn't run on its own — it waits for a client to
spawn it and speak JSON-RPC over stdin/stdout. See Step 2 / Step 3.

**What's the difference between a tool, a resource, and a prompt?**
Short version: *tools do something* (the model calls them), *resources are data
to read* (the app loads them), *prompts are recipes* (the user invokes them).
Full details in `docs/01-concepts.md`.

**Isn't this just "function calling"?**
Function calling is how an LLM decides to use a tool — MCP is the standard for
*transporting* tools and data between apps and models. They're complementary,
not the same thing. The whole comparison is in `docs/04-mcp-vs-alternatives.md`.

**stdio vs Streamable HTTP — which do I use?**
Same JSON-RPC messages, different plumbing. stdio for local servers you run
yourself; Streamable HTTP for remote/deployed servers. See `docs/01-concepts.md`.

**Can I plug my server into ChatGPT?**
Claude Desktop, VS Code, and Cursor are the easy wins in Step 4. Support varies
by app — any app that speaks MCP can use your server; that's the whole point.

**Do I have to learn JSON-RPC?**
No. The SDK generates and parses it for you — but Step 3 shows you the raw
traffic so you understand what's happening underneath.

More questions answered in `docs/05-faq.md`.

---

## Where to go next

- Official docs: <https://modelcontextprotocol.io>
- MCP specification: <https://modelcontextprotocol.io/specification/latest>
- Reference servers: <https://github.com/modelcontextprotocol/servers>

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'mcp'` | Activate the venv first, or run with `python -m` inside it. |
| LSP/editor red squiggles on `MCPServer` | Your editor is using system Python. Select the interpreter at `.venv\Scripts\python.exe`. |
| Server starts then exits instantly | Something printed to stdout. Search for `print(` in the server. |
| Weather returns "Unable to fetch" | No internet, or you hit the Open-Meteo rate limit. Wait a minute and retry. |
| Client hangs | The server isn't on your `PATH` in the config — use relative paths to the venv python (as shipped) or absolute ones. |
| `UnicodeEncodeError` on Windows | Avoid non-ASCII characters in tool output, or run with `PYTHONIOENCODING=utf-8`. |
| `streamlit: command not found` | The venv isn't active — run `.\.venv\Scripts\python.exe -m streamlit run app.py`. |
| Chat shows `Groq call failed: ... 401` | The API key is missing or wrong — get one at https://console.groq.com/keys. |
