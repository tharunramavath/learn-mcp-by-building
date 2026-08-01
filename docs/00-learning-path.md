# 00 · How to learn MCP, step by step

This is the **reading/doing order** for this project. Follow it top to bottom.
Everything builds on what came before — don't skip the early steps even if they
feel simple, because each one introduces a skill the later steps assume.

> **Total time:** ~3–4 hours for the whole path.
> **Golden rule:** after each step, you should be able to explain *why* it
> matters, not just run the command.

---

## Phase 0 — The 30-second idea (5 min)

1. Read **[`README.md`](https://github.com/tharunramavath/learn-mcp-by-building#readme) → "What is MCP?"** — the "USB-C for AI" analogy.
2. Read **[`02-glossary.md`](02-glossary.md)** — skim the table. Don't memorize it; just get
   a feel for the vocabulary (Host, Client, Server, Tool, Resource, Prompt).
3. Look at the project layout in the README so you know which file is which.

**Checkpoint:** can you say in one sentence what MCP does?

---

## Phase 1 — Theory first (20 min)

Read **[`01-concepts.md`](01-concepts.md)** fully, then come back to it later as reference.

Pay special attention to the **3 participants** (Host → Client → Server) and the
**2 layers** (data layer = JSON-RPC messages, transport layer = stdio / HTTP).
These two ideas are the mental model everything else hangs on.

**Checkpoint:** draw the architecture from memory. Where does the client live?
What travels over stdio?

---

## Phase 2 — Build the first server (20 min)

Now the theory becomes code. Follow **[`README.md`](https://github.com/tharunramavath/learn-mcp-by-building#readme) → Step 1**:

1. Read `server_basic.py` top to bottom.
2. Notice the 3 primitives: `@mcp.tool()` (add/multiply/greet),
   `@mcp.resource()` (config), `@mcp.prompt()` (math_help).
3. Notice *why* type hints + docstrings are in the code — they become the tool's
   schema and description.
4. Run it: `python server_basic.py` — it "does nothing" and waits. That's normal.

**Checkpoint:** point to each primitive in the file and say what the AI can do
with it.

---

## Phase 3 — Prove it with a tiny client (20 min)

Follow **[`README.md`](https://github.com/tharunramavath/learn-mcp-by-building#readme) → Step 2**. Run `python test_client_basic.py` and watch the
output **in order**:

1. Discovery (`server/discover`)
2. List tools / resources / prompts
3. Call `add(2, 3)` → `5.0`
4. Read the resource, get the prompt

This is the whole MCP conversation, end to end. If you only do one thing today,
make it this step — it turns "protocol" from a buzzword into something you've
seen with your own eyes.

**Checkpoint:** list the 7 messages the client sends, in order.

---

## Phase 4 — The Inspector (visual tool) (20 min)

Follow **[`README.md`](https://github.com/tharunramavath/learn-mcp-by-building#readme) → Step 3**. The Inspector gives you the same conversation
from Phase 3, but in a clickable web UI.

1. Double-click `run-inspector.cmd` (or run the npx command).
2. Connect to the `calculator` server.
3. Browse the Tools / Resources / Prompts tabs.
4. Call `add` with `{"a": 10, "b": 5}`.
5. Open the **Protocol** tab and watch the raw JSON-RPC fly by.

If the UI doesn't look like YouTube tutorials, read **[`03-inspector-v2-guide.md`](03-inspector-v2-guide.md)**
— it maps the old v1 layout to the new v2 tabs.

**Checkpoint:** find the `tools/call` request you just made in the Protocol tab.

---

## Phase 5 — Plug into a real AI app (20 min)

Follow **[`README.md`](https://github.com/tharunramavath/learn-mcp-by-building#readme) → Step 4**. This is the payoff — your server running inside
a tool you already use:

1. **Claude Desktop** — copy `claude_desktop_config.json` to the real config
   path, restart, ask it to use the calculator.
2. **VS Code** — use `.vscode/mcp.json` and the MCP commands in the palette.
3. **Cursor** — paste the same config into Settings → MCP.

**Checkpoint:** get one AI app to call your `multiply` tool on its own.

---

## Phase 6 — Real-world upgrade: weather (20 min)

Follow **[`README.md`](https://github.com/tharunramavath/learn-mcp-by-building#readme) → Step 5**. This shows how real servers differ from toys:

1. Read `server_weather.py` — async tools, an external HTTP call, a two-step
   lookup (grid point → forecast).
2. Run `python test_client_weather.py` (needs internet).
3. Connect the `weather` server in the Inspector.

**Checkpoint:** explain the two-step forecast flow out loud.

---

## Phase 7 — Be the host: chat with your servers (30 min)

Follow **[`README.md`](https://github.com/tharunramavath/learn-mcp-by-building#readme) → Step 7**. Until now the servers were "dumb" — this is
where you become the **AI app** (the host):

1. Read `mcp_host.py` — a sync wrapper around the async MCP client. Note the
   background asyncio loop and the one-long-lived-coroutine trick that keeps the
   stdio transport alive.
2. Read `chat_engine.py` — the agent loop: LLM requests a tool call, the host
   runs it, the result goes back to the LLM. Repeat until it answers.
3. Run `run-chat.cmd`, paste a free Groq key, connect to the **calculator**
   server, and ask *"What is 17 * 23?"*. Open the **agent trace** under the
   reply — you'll see the LLM called your real `multiply` tool.
4. Switch to the **weather** server and ask about Mumbai.

**Checkpoint:** explain the loop — what happens to a tool call between Groq and
your server, and who runs it.

---

## Phase 8 — Under the hood (15 min)

Follow **[`README.md`](https://github.com/tharunramavath/learn-mcp-by-building#readme) → Step 6**. Re-read the two big ideas in [`01-concepts.md`](01-concepts.md):

1. **Two layers** — data (what) vs transport (how).
2. **Stateless + discovery** — the client always asks before using.

Then re-read the glossary — it should feel obvious now.

**Checkpoint:** finish this phase and the glossary reads like plain English.

---

## Phase 9 — Challenges (do these yourself)

From **[`README.md`](https://github.com/tharunramavath/learn-mcp-by-building#readme) → Challenges** — no hints, that's the point:

1. Add a `divide` tool. What happens when `b == 0`?
2. Add a resource template (`weather://city/{city}`).
3. Run `server_basic.py` over Streamable HTTP instead of stdio.
4. Write a tiny client that parses a math question and calls your tools.

**Checkpoint:** each challenge fails at least once — debug it, don't look up the
answer.

---

## After the path — go deeper

| When you're ready | Read |
|---|---|
| Definitions of any term | [`02-glossary.md`](02-glossary.md) |
| Any MCP concept in depth | [`01-concepts.md`](01-concepts.md) |
| "Why not just use function calling?" | [`04-mcp-vs-alternatives.md`](04-mcp-vs-alternatives.md) |
| Any question not answered here | [`05-faq.md`](05-faq.md) |
| The full spec | <https://modelcontextprotocol.io/specification/latest> |
| More real servers | <https://github.com/modelcontextprotocol/servers> |

---

## TL;DR cheat sheet

| Phase | You learn | You run |
|------|-----------|---------|
| 0 | What MCP is | — |
| 1 | Theory (participants, layers) | — |
| 2 | The 3 primitives in code | `python server_basic.py` |
| 3 | The whole protocol conversation | `python test_client_basic.py` |
| 4 | Visual inspection | `run-inspector.cmd` |
| 5 | Integration with AI apps | config files |
| 6 | Real-world servers | `python test_client_weather.py` |
| 7 | You are the host (LLM + MCP) | `run-chat.cmd` |
| 8 | Why it works | — |
| 9 | Prove you learned it | challenges |
