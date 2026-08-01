# 03 · MCP Inspector v2 guide

Most tutorials and blog screenshots show the **classic Inspector (v1)**. This
project runs the **new Inspector v2** — same MCP protocol underneath, but the
UI was redesigned from "everything on one screen" into **tabs**.

This cheat-sheet maps every classic v1 feature to where it lives in v2.

## The one-screen → tabs idea

v1 crammed transport type, command/args, capability checkboxes, Tools,
Resources, Prompts, and a raw JSON-RPC console onto one page.

v2 splits those into:

| v2 area | What it is |
|---|---|
| **Client Settings** (gear in header) | **OAuth client identity** — Enterprise IdP, CIMD, Dynamic Client Registration. Only needed for remote HTTP servers that require OAuth. Ignore it for local stdio servers. |
| **Connection** (per-server config) | Transport type, Command, Args, cwd, env — the same fields v1 had in its top bar. Set in the catalog (`inspector.json`) or per-server connection settings. |
| **Server Settings** (per-server) | Protocol era, log level, roots, advertised extensions, pagination, timeouts — this is where v1's "client settings" capability toggles live. |
| **Tools** tab | List tools, see schemas, call them with JSON args, see results |
| **Resources** tab | List resource URIs + metadata, read their contents, subscribe |
| **Prompts** tab | List prompt templates + their arguments, run them, preview messages |
| **Protocol** tab | The JSON-RPC conversation: every request/response/notification the client and server exchanged |
| **Network** tab | The transport-level traffic: HTTP method, status, `Mcp-*` headers, timing, error taxonomy |
| **Logs** tab | Server log messages (`notifications/message`) |
| **Tasks** tab | Long-running tool runs (when using the "Run as task" feature) |
| **Apps** tab | Sandboxed MCP apps (advanced) |

## Feature mapping: v1 → v2

| You saw in the tutorial (v1) | Where it is in v2 |
|---|---|
| **Transport type** dropdown (stdio / SSE / Streamable HTTP) | Connection settings dialog → **Transport** selector. Also set per-server in `inspector.json` (`"type": "stdio"`). |
| **Command** + **Arguments** boxes | Connection settings dialog → **Command** / **Args** fields. Also in `inspector.json` as `command`, `args`, `cwd`, `env`. |
| **Tools** tab | **Tools** tab — identical purpose: pick a tool, fill the input schema, run it, see the result. |
| **Resources** tab | **Resources** tab — click a URI to read its content; metadata (MIME type, description) shown in the list. |
| **Prompts** tab | **Prompts** tab — shows each prompt's arguments and lets you run it. |
| **Pings** | Look for a **Ping** action in the connection header/menu; every ping shows up as a `ping` request in the **Protocol** tab. |
| **Sampling** | Deprecated in the 2026-07-28 spec — not exposed as a toggle in v2. |
| **Elicitation** | Not a settings toggle. It appears as a **pending-request modal** (MRTR round-trip) when a tool needs more input from you. |
| **Roots** | **Server Settings → Roots** — set the `roots` the client advertises. |
| **Routes** (protocol methods) | **Protocol** tab — the request/response lifecycle; **Network** tab — the raw transport frames and `Mcp-*` headers. |
| **Raw JSON-RPC console** | **Protocol** tab (semantic view) and **Network** tab (raw traffic). |
| **Notifications pane** | **Logs** tab + a notifications view. |
| **Capability checkboxes** (client settings) | **Server Settings** — protocol era, log level, advertised extensions, pagination, etc. |

## Heads-up: the "Client Settings" gear is OAuth, not capabilities

In v1, "client settings" meant capability checkboxes (tools, resources, prompts,
sampling, elicitation, roots). **In v2 the header gear is different** — it opens
the **OAuth client identity** dialog:

- **Enterprise-Managed Authorization** — sign in through your org's IdP instead
  of each server's own OAuth login.
- **CIMD (Client ID Metadata Document)** — the preferred client-identity
  mechanism in the 2026-07-28 spec.
- **Dynamic Client Registration** — the older mechanism, still used when CIMD
  is off.

These only matter for **remote HTTP servers** that require OAuth. Your
`calculator` and `weather` servers are **local stdio** servers — they don't do
OAuth, so you can ignore this dialog.

The toggles you remember from v1 live in **Server Settings** instead (open the
*server's* settings, not the client header gear).

## Quick walkthrough (with the calculator server)

1. Start the Inspector (see Step 3 of the README):
   ```powershell
   .\run-inspector.cmd
   ```
   (or `npx @modelcontextprotocol/inspector --catalog "...\inspector.json"`)
2. Pick **`calculator`** in the catalog and click **Connect**.
3. **Tools** tab → click `add` → enter `{"a": 10, "b": 5}` → **Call tool** → result `15.0`.
4. **Resources** tab → click `config://app` → see your config JSON.
5. **Prompts** tab → run `math_help` with `{"problem": "17 * 23"}`.
6. **Protocol** tab → scroll the conversation: you'll see `initialize`, `server/discover`,
   `tools/list`, `tools/call` — the exact JSON-RPC messages from Step 2 of the tutorial.
7. **Network** tab → see the same traffic at the transport level.
8. **Logs** tab → your server's `INFO:server-basic:...` log lines.

## Why the tutorials look different

The tutorials were recorded against `@modelcontextprotocol/inspector@0.x` /
`@1.x` (npm tag `v1-latest`). The npm tag `latest` is now **2.0.0**, which this
project uses.

> **Tried v1 on this machine and it failed?** That's a Windows/MSYS quirk, not
> your fault. The v1 CLI's `npx` shim re-spawns `node` for its client server and
> the spawned process can't find `node`, so it dies with `spawn node ENOENT`.
> v2 doesn't have this problem. If you really want the v1 UI for comparison, run
> its `cli.js` **directly with `node`** (this skips the broken shim):

```powershell
node "<your-npm-cache>\_npx\<version-hash>\node_modules\@modelcontextprotocol\inspector\cli\build\cli.js" "<your-path>\mcp-tutorial\.venv\Scripts\python.exe" "<your-path>\mcp-tutorial\server_basic.py"
```

> The npm-cache path is version-specific; re-run `npx @modelcontextprotocol/inspector@1.0.1 --version` to refresh it if the folder hash changes.

Both versions inspect the same server — you're not missing any functionality in v2.
