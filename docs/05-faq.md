# 05 · FAQ

The full version of the short FAQ in the README. Answers assume you've done the
steps — click the link in each answer to go deeper.

---

## General

**What exactly is MCP?**
An open standard that lets AI apps (Claude, ChatGPT, VS Code, Cursor) connect to
external tools and data. "USB-C for AI": build the integration once, plug it
into any MCP-capable app. → `docs/01-concepts.md`

**Is MCP a programming language or a framework?**
Neither. It's a **protocol** — a defined format for messages (JSON-RPC 2.0) and
how they travel (transport). The Python SDK turns it into decorators you write
normal functions behind.

**Do I need an AI model to follow this tutorial?**
No, not for Steps 1–6. You write servers and a tiny client, and you watch real
JSON-RPC traffic — no LLM involved. Only Step 7 (the host) needs the free Groq
API key.

**Who owns MCP?**
It started at Anthropic and is now developed in the open under the Model
Context Protocol organization, with contributions from Anthropic, OpenAI,
Google, Microsoft, and many others.

---

## Architecture

**What's the difference between Host, Client, and Server?**
- **Host** = the AI app you use (Claude Desktop, VS Code, your Step 7 app).
- **Client** = a component the host creates for each server; maintains the
  connection.
- **Server** = your program that exposes tools, resources, and prompts.

One host can talk to many servers at once — each via its own client. → `docs/01-concepts.md`

**What's the difference between a tool, a resource, and a prompt?**
- **Tool** — something the model can *call to act* (calculate, fetch, send).
- **Resource** — read-only *data* the app loads as context.
- **Prompt** — a reusable *instruction template* the user invokes.

Rule of thumb: *does something* → tool; *is data* → resource; *is a recipe* →
prompt.

**Which transport should I use?**
- **stdio** — server lives on the same machine; the client spawns it and talks
  over stdin/stdout. Used throughout this tutorial.
- **Streamable HTTP** — server is remote; HTTP POST + Server-Sent Events, with
  auth. Same JSON-RPC messages, different plumbing.

**Why can't I `print()` in a stdio server?**
Because stdout *is* the protocol channel. A stray `print()` corrupts the JSON-RPC
stream and the server silently breaks. Use `logging` (stderr) instead. This is
the golden rule — see `docs/01-concepts.md`.

---

## Function calling & MCP

**Isn't MCP just function calling?**
Function calling = the *grammar* an LLM uses to request a tool. MCP = the
*transport + discovery* standard that carries tools and data between apps and
servers. They're complementary. → `docs/04-mcp-vs-alternatives.md`

**Why does Step 7 (the host) use Groq function calling *and* MCP?**
The Groq API decides *which* tool to call (function calling). The MCP host
(`mcp_host.py`) actually *runs* it on the server and returns the result. Two
different layers working together — exactly how real AI apps work.

**Can I use the host UI with a different LLM provider?**
Yes, with a small change: swap the `groq` client in `chat_engine.py` for any
OpenAI-compatible client (they share the function-calling message format).
Anthropic and Gemini use a similar but slightly different format.

---

## Using your servers

**Why does `python server_basic.py` just sit there?**
It's working correctly. A stdio server doesn't run on its own — a client must
spawn it and start the conversation (Step 2's script or the Inspector in Step 3).

**Why does the Inspector look different from YouTube tutorials?**
This project runs Inspector v2 (tabs), while older tutorials show v1 (one
screen). They inspect the same protocol. → `docs/03-inspector-v2-guide.md`

**Do the config files contain my paths?**
No — the repo is path-independent. `inspector.json` and `.vscode/mcp.json` use
relative paths so they work for anyone who opens the folder.
`claude_desktop_config.json` uses a `<YOUR-PATH>` placeholder because Claude
Desktop requires absolute paths — replace it before copying.

**The weather tool says "Unable to fetch". What now?**
Usually no internet access, an Open-Meteo rate limit (wait a minute), or a
temporarily blocked User-Agent. The server logs the underlying error to stderr.

---

## Troubleshooting recap

Full table in the README. The four most common gotchas:

| Symptom | Likely cause |
|---|---|
| `No module named 'mcp'` | venv not activated |
| Server starts then instantly exits | `print()` in server code (stdout pollution) |
| Client hangs | Config path wrong / server not spawnable |
| `Groq call failed: ... 401` | Missing or wrong Groq API key |

---

## Learn more

- Official docs: <https://modelcontextprotocol.io>
- Specification: <https://modelcontextprotocol.io/specification/latest>
- Reference servers: <https://github.com/modelcontextprotocol/servers>
