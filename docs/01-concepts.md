# 01 · Everything you need to learn about MCP

This is your reference sheet. Read it once, then keep it as a cheat sheet while
you go through the steps in the [`README.md`](https://github.com/tharunramavath/learn-mcp-by-building#readme).

---

## 1. What is MCP?

**MCP (Model Context Protocol)** is an open standard that lets AI applications
(Claude, ChatGPT, VS Code, Cursor, ...) connect to **external systems**: your
files, a database, an API, a smart home, whatever you build.

Think of it as **"USB-C for AI"**. Just like USB-C gives you one universal plug
that works with every device, MCP gives AI apps one universal protocol for
talking to tools and data.

Before MCP, every AI app had to build a custom integration for every system.
With MCP, **you build the integration once** and it works in any MCP-capable app.

> MCP does not dictate how the AI app uses its language model. It only standardizes
> how context (data + tools + prompts) is exchanged.

---

## 2. The architecture: 3 participants

```
┌─────────────────────────┐          ┌─────────────────────────┐
│  HOST  (the AI app)     │          │  SERVER (your program)  │
│  e.g. Claude Desktop,   │          │  exposes tools,         │
│  VS Code, Cursor        │          │  resources, prompts     │
└─────────────────────────┘          └─────────────────────────┘
        │                                    ▲
        │  creates one CLIENT per server     │  one dedicated
        ▼                                    │  connection each
┌─────────────────────────┐                  │
│  CLIENT (inside host)   │──────────────────┘
└─────────────────────────┘
```

- **Host** — the AI application you actually use. It talks to the user and the LLM.
- **Client** — a component the host creates for each server. It maintains the connection.
- **Server** — *your code*. A program that provides context (tools, resources, prompts).

One host can have many clients, each connected to a different server. That is how
a single AI app gets files + weather + calendar + GitHub at once.

---

## 3. The two layers

MCP is split into two layers that work together.

### Data layer (the "what")
Defines the **JSON-RPC 2.0** message format and the *primitives* (tools, resources,
prompts). It is the part you interact with most as a developer.

### Transport layer (the "how")
Defines how messages physically travel. Two transports exist:

| Transport | When to use | How it works |
|-----------|-------------|--------------|
| **stdio** | Local servers on the same machine | The client launches your server as a subprocess and talks to it over stdin/stdout. One client per server. |
| **Streamable HTTP** | Remote servers | Messages go over HTTP POST + Server-Sent Events. Many clients, needs auth. |

> The exact same JSON-RPC messages work over both transports. Only the plumbing differs.

---

## 4. The three server primitives

These are THE most important concept. Servers can expose three kinds of things:

| Primitive | What it is | Who controls it | Protocol methods |
|-----------|------------|-----------------|------------------|
| **Tool** | A function the AI can **call** to take an action (calculator, send email, query a DB) | The **model** (it decides when to call) | `tools/list`, `tools/call` |
| **Resource** | **Read-only** data the app can load for context (a file, a schema, docs) | The **application** | `resources/list`, `resources/read` |
| **Prompt** | A **reusable template** telling the model how to do a task | The **user** (explicitly invoked) | `prompts/list`, `prompts/get` |

Rule of thumb:
- **Does it do something?** → a *tool*.
- **Is it data to read?** → a *resource*.
- **Is it a recipe/instruction?** → a *prompt*.

### How the AI actually uses them
1. The client asks the server to **discover** capabilities (`server/discover`).
2. It lists the primitives (`tools/list`, `resources/list`, `prompts/list`).
3. The LLM sees the tools and decides to call one → `tools/call`.
4. The server executes and returns a result the LLM can use.

---

## 5. The request/response lifecycle (you will see this in Step 2)

Every message is JSON-RPC 2.0 with a request `id`, a `method`, and `params`.
A typical conversation with a calculator server:

```jsonc
// 1. List tools
{ "jsonrpc": "2.0", "id": 1, "method": "tools/list" }

// 2. Response — the schema of each tool
{
  "jsonrpc": "2.0", "id": 1,
  "result": {
    "tools": [
      {
        "name": "add",
        "description": "Add two numbers together.",
        "inputSchema": {
          "type": "object",
          "properties": {
            "a": { "type": "number" },
            "b": { "type": "number" }
          },
          "required": ["a", "b"]
        }
      }
    ]
  }
}

// 3. Call a tool
{ "jsonrpc": "2.0", "id": 2, "method": "tools/call",
  "params": { "name": "add", "arguments": { "a": 2, "b": 3 } } }

// 4. Result
{ "jsonrpc": "2.0", "id": 2,
  "result": { "content": [ { "type": "text", "text": "5" } ] } }
```

The SDK hides this from you — your job is just to write normal Python functions.

---

## 6. Key properties of the protocol

- **Stateless.** Every request carries the protocol version + capabilities in its
  `_meta` field, so the server never infers anything from previous requests.
- **Capability negotiation.** Servers advertise what they support
  (`tools`, `resources`, `prompts`) via `server/discover`.
- **Versioned.** Client and server negotiate a protocol version (e.g. `2026-07-28`).
- **Input schemas.** Tools declare their inputs as **JSON Schema**, generated
  automatically from your type hints and docstrings.

---

## 7. The golden rule for stdio servers

> **NEVER write to stdout** (`print()`). stdout is the protocol channel.
> Corrupt it and the server silently breaks.

Use the `logging` module instead — it writes to **stderr**, which is safe.

```python
import logging
logger = logging.getLogger(__name__)

# ❌ BREAKS the server over stdio
print("Server started")

# ✅ Safe — goes to stderr
logger.info("Server started")
```

For HTTP servers stdout is fine, but the habit of using `logging` is good everywhere.

---

## 8. What to learn after this tutorial

Once you've built the two servers in this project, the natural next topics are:

1. **Resource templates** — dynamic URIs like `weather://forecast/{city}`.
2. **Notifications & subscriptions** — servers push "tool list changed" updates.
3. **Streamable HTTP transport** — deploy your server remotely with OAuth.
4. **Client primitives** — `elicitation` (server asks the user questions).
5. **Building your own MCP client** — the flip side of everything here.

The official spec lives at <https://modelcontextprotocol.io/specification/latest>.
