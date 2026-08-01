# 02 · MCP Glossary

A quick cheat-sheet of every term you'll bump into.

| Term | Meaning |
|------|---------|
| **MCP** | Model Context Protocol. Open standard for connecting AI apps to tools and data. "USB-C for AI." |
| **Host** | The AI application you use (Claude Desktop, VS Code, Cursor, ChatGPT...). |
| **Client** | Component inside a host; one per server. Maintains the connection to the server. |
| **Server** | Your program. Exposes tools, resources, and prompts. |
| **Tool** | A function the AI model can call to take an action. (Model-controlled.) |
| **Resource** | Read-only data (file, schema, doc) the app loads as context. (Application-controlled.) |
| **Prompt** | A reusable instruction template invoked by the user. |
| **JSON-RPC 2.0** | The message protocol MCP is built on: requests, responses, notifications. |
| **Data layer** | The "what" of MCP: the JSON-RPC messages and primitives. |
| **Transport layer** | The "how": how messages travel. |
| **stdio transport** | Local transport. Client spawns server as a subprocess; talks over stdin/stdout. |
| **Streamable HTTP** | Remote transport. HTTP POST + Server-Sent Events; supports auth. |
| **Discovery** | `server/discover` — the client asks the server what it supports and which versions it speaks. |
| **Capabilities** | The features a server/client supports (`tools`, `resources`, `prompts`, ...). |
| **`tools/list`** | Discover available tools. |
| **`tools/call`** | Execute a tool with arguments. |
| **`resources/list`** | Discover available resources. |
| **`resources/read`** | Fetch a resource's content by URI. |
| **`prompts/list`** | Discover available prompts. |
| **`prompts/get`** | Fetch a prompt's template and arguments. |
| **JSON Schema** | The format used to describe a tool's expected inputs. |
| **Input schema** | The `inputSchema` on a tool — auto-generated from Python type hints + docstrings. |
| **MIME type** | Declares resource content type (e.g. `text/markdown`, `application/json`). |
| **Notification** | A message with no response expected (e.g. "tools changed"). |
| **Stateless** | Each request stands alone; carries version + capabilities in `_meta`. |
| **Protocol version** | The negotiated version string (e.g. `2026-07-28`). |
| **MCP Inspector** | Official web UI for poking at your server and watching the JSON-RPC traffic. |
| **`mcp dev`** | CLI command that launches the Inspector pointed at your server. |
| **Elicitation** | Client primitive: server can ask the user for more input. |
| **Sampling** | *(deprecated in 2026-07-28)* server asks the client's LLM for a completion. |
