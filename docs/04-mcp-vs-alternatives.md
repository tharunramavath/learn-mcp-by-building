# 04 · MCP vs. the alternatives

A common first question is: *"Why do I need MCP at all? Can't I just use function
calling / LangChain tools / a REST API?"* This document answers that precisely.
There is no single winner — each tool has a job. The skill is knowing when to
pick which.

---

## 1. MCP vs. plain LLM function calling

**Function calling** (a.k.a. tool calling) is what the model does: given a list
of tool schemas, it returns a JSON request to call one. OpenAI, Groq, Anthropic,
and others all implement it. In Step 7 you use Groq's function calling directly.

| | Plain function calling | MCP |
|---|---|---|
| What it standardizes | The **shape** of a tool call from the model | The **whole conversation**: discovery, transport, primitives, auth |
| Where tools live | Hard-coded into *one* app's code | Anywhere — any server, any host |
| Portability | Your `tools=` list is tied to that app | One server works in Claude, VS Code, Cursor, ... |
| Who owns the schema | You duplicate it per app | The server declares it once; hosts discover it |

**Analogy:** function calling is the *grammar* (how to say "call this tool").
MCP is the *postal service* (how a tool call reliably travels from any app to any
server and back). You can absolutely use function calling without MCP — you'll
just re-implement the plumbing yourself for every app.

---

## 2. MCP vs. provider-native tool ecosystems (OpenAI tools, Claude skills)

OpenAI and Anthropic ship their own tool/host ecosystems. MCP overlaps with them
but isn't a replacement — it's a neutral protocol those ecosystems also adopt.

- **Provider-native tools** are optimized for *that provider's* models and app
  (e.g. Claude Desktop's skills, OpenAI's hosted actions). Lock-in is the trade-off.
- **MCP** is provider-agnostic. Anthropic, OpenAI, Google, Microsoft, and
  others all support it. You write the server once and it runs in all of them.

If you control your whole stack, provider-native tooling is fine. If you want one
integration to reach many apps (or you don't control the host), MCP wins.

---

## 3. MCP vs. LangChain / LlamaIndex "tools"

Agent frameworks (LangChain, LlamaIndex, Semantic Kernel, ...) give you an
abstraction for "tools" plus memory, planning, and routing on top of an LLM.

- The framework's `@tool` is an **in-process** abstraction — it lives inside your
  agent program.
- MCP is an **out-of-process** protocol — the tool lives in a separate process
  (a server) and any host can reach it.

These are **complementary layers**. Modern integrations let you expose an MCP
server *as* a framework tool, or wrap framework tools *in* an MCP server. A
useful mental model:

```
LLM model  <-(function calling)->  agent framework  <-(MCP)->  your servers
```

---

## 4. MCP vs. a plain REST API

| | REST API | MCP |
|---|---|---|
| Who calls it | A human or a client app you wrote | An AI app, automatically, based on schema |
| Discovery | Docs / OpenAPI you maintain separately | `tools/list` etc. — the server describes itself |
| Action vs. data | Everything is endpoints you design | Primitives (tools / resources / prompts) encode *intent* |
| Integration cost | You integrate it per-app | One server, many hosts |

A REST API is a perfectly good way to expose a service. MCP layers a
**standardized, self-describing, model-friendly contract** on top. You can (and
often will) implement an MCP server that *calls* a REST API behind the scenes —
that's exactly what `server_weather.py` does with Open-Meteo.

---

## 5. Decision guide

| Situation | Reach for |
|---|---|
| I want to expose my service to many AI apps | **MCP** |
| I'm building a one-off script that calls an LLM | **Function calling** (no protocol needed) |
| I'm building a multi-step agent with memory & planning | **Agent framework** (LangChain etc.), optionally exposing MCP |
| I have a normal web service | **REST API**, plus an MCP server in front if AI apps need it |

---

## 6. Why this tutorial teaches MCP

Because it's the layer that makes everything else possible:

- It **standardizes the contract** so you build once, use everywhere.
- It **separates servers from hosts**, so you understand both halves of the
  ecosystem (you build a server in Steps 1–5 *and* a host in Step 7).
- It's **transport-agnostic**: the same JSON-RPC messages run over stdio
  locally and Streamable HTTP remotely.
- It's **where the industry is going** — the model providers, code editors, and
  agent frameworks all adopted it.

Learning function calling alone teaches you one app's API. Learning MCP teaches
you the shape of the whole ecosystem.
