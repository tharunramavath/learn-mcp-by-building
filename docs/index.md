# Learn MCP by Building an MCP Server

The hands-on guide to the **Model Context Protocol** (MCP) — "USB-C for AI".

This repo teaches MCP from zero by building real things: a calculator server, a
live weather server, test clients, and finally your own AI host with a Streamlit
chat UI. Every concept is a file you write, run, and break on purpose.

## The path

| Doc | What it is |
|-----|------------|
| [Learning Path](00-learning-path.md) | **Start here** — the recommended reading/doing order (~3-4 hours) |
| [Concepts](01-concepts.md) | The theory: architecture, the 3 primitives, transports |
| [Glossary](02-glossary.md) | Cheat-sheet of every MCP term |
| [Inspector Guide](03-inspector-v2-guide.md) | Map the new Inspector v2 UI to classic tutorials |
| [MCP vs Alternatives](04-mcp-vs-alternatives.md) | Function calling, LangChain, REST — when MCP wins |
| [FAQ](05-faq.md) | Common questions and gotchas |

## What you'll build

1. `server_basic.py` — an offline calculator server (tools, resources, prompts)
2. `test_client_basic.py` — a tiny client that drives the whole protocol
3. The MCP Inspector — poke at the server and watch the raw JSON-RPC
4. Real AI apps — plug into Claude Desktop, VS Code, Cursor
5. `server_weather.py` — a live weather server (async, external APIs, geocoding)
6. Under the hood — the two layers and stateless discovery
7. `app.py` — your own AI host: a Streamlit chat UI where an LLM calls your tools

## Quickstart (60 seconds)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python server_basic.py
```

Open a **second** terminal:

```powershell
python test_client_basic.py
```

If you see discovery, tools, resources, prompts, and `add(2, 3) -> 5.0`, you just
ran a full MCP conversation.

Full step-by-step instructions are in the
[GitHub README](https://github.com/tharunramavath/learn-mcp-by-building).
