"""Generator for mcp.ipynb — a graduate-level MCP + AI Agents teaching notebook.

Third module in the course (after RAG/ and LangChain/). Same three-cell rhythm
per topic as langchain.ipynb:
  1. A slide-style markdown cell (bullet points).
  2. An "Instructor Script" markdown cell (~80-150 words of narration).
  3. A runnable code cell with clean, printed output.

Design choice: concepts run OFFLINE (an in-notebook mock MCP server/client and a
deterministic stand-in LLM), so the protocol is fully reproducible in class. A
few cells then talk to the REAL MCP server in this folder (mcp_server.py) over
stdio, guarded so they degrade to a notice if the `mcp` package is missing.

Run:  python _build_mcp_notebook.py   ->  writes mcp.ipynb
"""
import json

cells = []


def md(source):
    cells.append({"cell_type": "markdown", "metadata": {},
                  "source": source.splitlines(keepends=True)})


def code(source):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": source.rstrip("\n").splitlines(keepends=True)})


def slide(title, bullets):
    md(f"# {title}\n\n" + "\n".join(f"- {b}" for b in bullets))


def script(text):
    md("> ### \U0001F3A4 Instructor Script\n>\n> " + text.replace("\n", "\n> "))


# ---------------------------------------------------------------------------
# Title / framing
# ---------------------------------------------------------------------------
md(
    "# MCP & AI Agents: Standardized Tools for Autonomous Systems\n"
    "### A Graduate-Level, Hands-On Teaching Notebook\n\n"
    "**Audience:** Graduate students who have completed the `RAG/` and `LangChain/` modules.\n\n"
    "**Where this fits:** This is the third step of a three-part story.\n"
    "1. **Chains** (LangChain module): we wired LLMs into a *fixed* pipeline.\n"
    "2. **RAG** (RAG module): we *grounded* the LLM in real data.\n"
    "3. **Agents + MCP** (this module): we let the LLM *decide* what to do, and we give it tools "
    "through a **standard protocol**.\n\n"
    "**Format:** Each topic has three parts — a \U0001F4CA *slide*, a \U0001F3A4 *instructor "
    "script*, and a \U0001F4BB *runnable code example*.\n\n"
    "**Design choice:** The protocol is taught **offline** with a tiny in-notebook mock MCP "
    "server/client and a deterministic stand-in LLM — no API key needed. A few cells then connect "
    "to the **real MCP server** in this folder (`mcp_server.py`) over stdio; they are guarded so "
    "the notebook still runs if the `mcp` package is not installed.\n\n"
    "---\n\n"
    "## Learning Objectives\n"
    "By the end of this notebook, students will be able to:\n"
    "- Explain the **M×N integration problem** that MCP solves.\n"
    "- Describe MCP's **host / client / server** architecture and its primitives (tools, "
    "resources, prompts).\n"
    "- Read the **JSON-RPC** messages MCP uses (`tools/list`, `tools/call`).\n"
    "- Build an MCP **server** (FastMCP) and connect a **client** to it.\n"
    "- Explain the **agent loop** and how MCP gives agents standardized tool access.\n"
    "- Load MCP tools into a **LangChain/LangGraph agent**.\n"
    "- Reason about the **security risks** of giving an LLM tools."
)

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
md("## \U0001F6E0️ Setup — Imports & Offline Helpers\n\n"
   "We reuse the offline **stand-in chat model** idea from the LangChain notebook, add a small "
   "`run_async` helper (so we can call async MCP code from notebook cells), and detect whether the "
   "real `mcp` package is available.")

code(
    r'''# If needed:
# !pip install -q langchain-core mcp langchain-mcp-adapters langgraph

import asyncio, concurrent.futures, json
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import AIMessage

# --- Offline stand-in chat model (same idea as the LangChain module) ---------
def _mock_chat(prompt_value):
    text = prompt_value.to_string() if hasattr(prompt_value, "to_string") else str(prompt_value)
    low = text.lower()
    if "vsftpd" in low or "backdoor" in low:
        return AIMessage(content="vsftpd 2.3.4 has a known backdoor (CVE-2011-2523) — critical.")
    if "report" in low:
        return AIMessage(content="SUMMARY: 3 services found; 1 critical finding. See details above.")
    return AIMessage(content="[stand-in LLM] analysis would appear here.")
mock_llm = RunnableLambda(_mock_chat)

# --- Run an async coroutine from a sync notebook cell, in any context --------
def run_async(coro):
    """Works whether or not an event loop is already running (e.g. Jupyter)."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)                 # no loop -> simplest path
    with concurrent.futures.ThreadPoolExecutor(1) as ex:   # inside a loop -> worker thread
        return ex.submit(lambda: asyncio.run(coro)).result()

# --- Is the real MCP SDK available? ------------------------------------------
try:
    import mcp  # noqa: F401
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False

print("Offline helpers ready. Real MCP SDK available:", MCP_AVAILABLE)'''
)

# ---------------------------------------------------------------------------
# 1. Why MCP
# ---------------------------------------------------------------------------
slide("\U0001F500 1 — Why MCP? The M×N Integration Problem", [
    "Every AI app wants to use many tools/data sources",
    "Without a standard: **M** apps × **N** tools = M×N custom integrations",
    "Each pairing re-invents auth, schemas, error handling",
    "MCP makes it **M + N**: build to one protocol",
    "Like a universal adapter for LLM ↔ tools",
])
script(
    "Before MCP, connecting language models to the outside world was a combinatorial mess. If you "
    "have M applications — chat clients, IDEs, agents — and N capabilities — a database, a scanner, "
    "a ticketing system — naively you write a custom integration for every pairing, which is M "
    "times N pieces of glue, each with its own authentication, data format, and quirks. The Model "
    "Context Protocol, introduced by Anthropic in late 2024, turns that into M plus N: every tool "
    "is wrapped once as an MCP *server*, and every application speaks MCP as a *client*, so any "
    "client can use any server. People call MCP the 'USB-C of AI' for this reason. The numbers "
    "below make the savings concrete."
)
code(
    r'''M, N = 6, 8   # apps, tools
print(f"{M} AI apps and {N} tools/data sources\n")
print(f"  Without a standard : {M} x {N} = {M*N:>3} custom integrations")
print(f"  With MCP           : {M} + {N} = {M+N:>3} integrations (each builds to ONE protocol)")
print(f"\n  Saved {M*N - (M+N)} integrations — and the gap grows as you add more.")'''
)

# ---------------------------------------------------------------------------
# 2. What is MCP
# ---------------------------------------------------------------------------
slide("\U0001F50C 2 — What is MCP?", [
    "An **open protocol** standardizing how apps give LLMs context & tools",
    "Client ↔ server messages over **JSON-RPC 2.0**",
    "Servers expose **tools, resources, prompts**",
    "Model-agnostic: works with any LLM or framework",
    "Growing ecosystem of reusable servers (GitHub, Slack, DBs, ...)",
])
script(
    "So what *is* MCP, concretely? It is an open specification for how an application supplies a "
    "language model with context and capabilities. Communication is plain JSON-RPC 2.0 messages "
    "between a client and a server, so it is language- and model-agnostic — there is nothing "
    "OpenAI- or Anthropic-specific about it. A server advertises three kinds of things: tools "
    "(functions the model can call), resources (read-only data the model can fetch), and prompts "
    "(reusable templates). Because the interface is standard, a community of reusable servers has "
    "appeared — for GitHub, Slack, Google Drive, Postgres, and many more — that you can plug into "
    "any MCP-aware host. We will build our own server later in this notebook."
)
code(
    r'''facts = {
    "Introduced by": "Anthropic (open-sourced, late 2024)",
    "Transport messages": "JSON-RPC 2.0 (requests, responses, notifications)",
    "Server exposes": "tools (callable), resources (readable), prompts (templates)",
    "Model dependency": "none — works with any LLM / agent framework",
    "Analogy": "a universal port ('USB-C') between AI apps and tools/data",
}
for k, v in facts.items():
    print(f"  {k:20s}: {v}")'''
)

# ---------------------------------------------------------------------------
# 3. Architecture
# ---------------------------------------------------------------------------
slide("\U0001F3DB️ 3 — Architecture: Host, Client, Server", [
    "**Host**: the AI app the user interacts with (e.g. Claude Desktop, an IDE, your agent)",
    "**Client**: lives in the host; keeps a 1:1 connection to one server",
    "**Server**: wraps a capability (a tool/data source) and exposes it via MCP",
    "One host can run **many** clients → many servers",
    "Servers can be local (your machine) or remote",
])
script(
    "MCP has three roles. The **host** is the application the user actually uses — Claude Desktop, "
    "an IDE plugin, or the agent you write. Inside the host run one or more **clients**, and each "
    "client maintains a dedicated, one-to-one connection to a single **server**. A **server** is a "
    "small program that wraps one capability — a scanner, a database, a file system — and exposes "
    "it through MCP's standard messages. The host orchestrates: it may spin up several clients at "
    "once, each talking to a different server, giving the model a whole toolbox. Keep this "
    "separation clear, because the security boundary later in the notebook sits exactly at the "
    "client-server connection. The diagram below sketches the layout."
)
code(
    r'''print("              HOST  (the AI application: agent, IDE, desktop app)")
print("              |")
print("     +--------+---------+-----------------+")
print("     |                  |                 |")
print("  Client A           Client B          Client C       (1 client : 1 server)")
print("     |                  |                 |")
print("     v                  v                 v")
print("  Server: nmap     Server: CVE KB    Server: SIEM      (each wraps one capability)")
print("\nThe host gives the model a toolbox by running several clients at once.")'''
)

# ---------------------------------------------------------------------------
# 4. Primitives
# ---------------------------------------------------------------------------
slide("\U0001F9F1 4 — MCP Primitives: Tools, Resources, Prompts", [
    "**Tools** — functions the model can *call* (have side effects): `port_scan(target)`",
    "**Resources** — read-only data the model can *fetch*: a file, a CVE database",
    "**Prompts** — reusable, parameterized prompt templates the server offers",
    "Tools are *model-controlled*; resources are *app-controlled*",
    "Our server (next) exposes all three",
])
script(
    "An MCP server can offer three kinds of primitives, and the distinction matters. **Tools** are "
    "functions the model may choose to call — like running a scan or creating a ticket — and they "
    "can have side effects, so they are *model-controlled*: the LLM decides when to invoke them. "
    "**Resources** are read-only data the application can load into context, such as a file or a "
    "knowledge base; these are *application-controlled*, fetched deliberately rather than at the "
    "model's whim. **Prompts** are reusable templates the server publishes so clients get a "
    "consistent, expert-authored way to ask for something. The mental model: tools *do*, resources "
    "*inform*, prompts *guide*. The `mcp_server.py` in this folder exposes two tools, a resource, "
    "and could add prompts."
)
code(
    r'''primitives = [
    ("Tool",     "model-controlled", "callable function w/ side effects", "port_scan(target)"),
    ("Resource", "app-controlled",   "read-only data to load as context", "kb://cve  (CVE database)"),
    ("Prompt",   "user-controlled",  "reusable parameterized template",   "/triage_alert {id}"),
]
print(f"{'PRIMITIVE':10s}{'CONTROL':18s}{'WHAT IT IS':36s}EXAMPLE")
print("-" * 92)
for name, control, what, ex in primitives:
    print(f"{name:10s}{control:18s}{what:36s}{ex}")'''
)

# ---------------------------------------------------------------------------
# 5. JSON-RPC on the wire (offline mock)
# ---------------------------------------------------------------------------
slide("\U0001F4E1 5 — The Protocol on the Wire (JSON-RPC)", [
    "MCP messages are **JSON-RPC 2.0**",
    "`tools/list` → server returns tool names + input schemas",
    "`tools/call` → server runs the tool, returns `content`",
    "Each request has an `id`; the response echoes it",
    "Below: a **mock** server/client so you can see the raw messages",
])
script(
    "Let's demystify the protocol by looking at the actual messages. Underneath, MCP is just "
    "JSON-RPC 2.0: a request is a JSON object with a method, parameters, and an id; the response "
    "echoes that id and carries a result. The two methods you will use most are `tools/list`, which "
    "asks a server what tools it has and returns their names and input schemas, and `tools/call`, "
    "which runs a named tool with arguments and returns its output as `content`. To make this "
    "tangible without any network or dependency, we implement a tiny mock server and client right "
    "here and print the raw JSON crossing between them. The real SDK hides these messages, but "
    "seeing them once makes the whole protocol click."
)
code(
    r'''# A minimal mock MCP server + client — pure Python, to expose the raw JSON-RPC.
class MockMCPServer:
    def __init__(self):
        self._tools = {
            "port_scan": {
                "description": "Simulated port scan of a target host.",
                "inputSchema": {"type": "object", "properties": {"target": {"type": "string"}}},
                "fn": lambda target: f"{target}: 21/ftp vsftpd 2.3.4, 22/ssh OpenSSH 7.2",
            }
        }
    def handle(self, request):                       # JSON-RPC request dict -> response dict
        rid, method, params = request.get("id"), request["method"], request.get("params", {})
        if method == "tools/list":
            tools = [{"name": n, "description": t["description"], "inputSchema": t["inputSchema"]}
                     for n, t in self._tools.items()]
            result = {"tools": tools}
        elif method == "tools/call":
            fn = self._tools[params["name"]]["fn"]
            result = {"content": [{"type": "text", "text": fn(**params["arguments"])}]}
        else:
            return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "no method"}}
        return {"jsonrpc": "2.0", "id": rid, "result": result}

server = MockMCPServer()

req1 = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
print("CLIENT -> SERVER (discover tools):")
print(json.dumps(req1, indent=2))
print("\nSERVER -> CLIENT:")
print(json.dumps(server.handle(req1), indent=2))

req2 = {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
        "params": {"name": "port_scan", "arguments": {"target": "10.0.0.5"}}}
print("\nCLIENT -> SERVER (call a tool):")
print(json.dumps(req2, indent=2))
print("\nSERVER -> CLIENT:")
print(json.dumps(server.handle(req2), indent=2))'''
)

# ---------------------------------------------------------------------------
# 6. Transports
# ---------------------------------------------------------------------------
slide("\U0001F50C 6 — Transports: stdio vs HTTP", [
    "Same JSON-RPC messages, different **pipe**",
    "**stdio**: client launches the server as a subprocess; talk over stdin/stdout",
    "Great for **local** tools (files, scanners on your machine)",
    "**Streamable HTTP / SSE**: server runs as a web service",
    "Great for **remote**, shared, multi-user servers",
])
script(
    "MCP separates the *messages* from the *pipe* that carries them, and there are two common "
    "transports. With **stdio**, the client launches the server as a child process and they "
    "exchange JSON-RPC over standard input and output — perfect for local tools that live on your "
    "machine, like a file reader or a scanner, because there is no port to open and the lifetime is "
    "tied to the client. With **streamable HTTP** (and its server-sent-events variant), the server "
    "runs as a long-lived web service that many clients can reach over the network — the right "
    "choice for a shared, remote, or multi-user server. The protocol and your tool code are "
    "identical either way; you pick the transport to match deployment. Our server defaults to "
    "stdio, which we use next."
)
code(
    r'''rows = [
    ("How the server starts", "client spawns it as a subprocess", "runs as a web service"),
    ("Communication",         "stdin / stdout pipes",             "HTTP requests (+ SSE stream)"),
    ("Best for",              "local tools, single user",         "remote / shared / multi-user"),
    ("Network port",          "none",                             "yes (e.g. :8000)"),
]
print(f"{'':24s}{'stdio':36s}{'streamable HTTP'}")
print("-" * 92)
for label, a, b in rows:
    print(f"{label:24s}{a:36s}{b}")
print("\nOur mcp_server.py uses stdio (the default): mcp.run().")'''
)

# ---------------------------------------------------------------------------
# 7. Building a server (FastMCP)
# ---------------------------------------------------------------------------
slide("\U0001F6E0️ 7 — Building an MCP Server (FastMCP)", [
    "The `mcp` SDK's **FastMCP** makes a server tiny",
    "`@mcp.tool()` turns a typed Python function into a tool",
    "The decorator auto-generates the input **schema** from type hints",
    "`@mcp.resource(uri)` exposes read-only data",
    "`mcp.run()` starts it (stdio by default)",
])
script(
    "Writing a server is surprisingly little code thanks to FastMCP in the official SDK. You "
    "create a `FastMCP` instance, then decorate ordinary, type-annotated Python functions with "
    "`@mcp.tool()`; the decorator reads your type hints and docstring to auto-generate the tool's "
    "name, description, and JSON input schema — the same metadata a model needs to call it "
    "correctly. A `@mcp.resource(uri)` decorator exposes read-only data under a URI. Finally "
    "`mcp.run()` starts the server on stdio. The `mcp_server.py` beside this notebook does exactly "
    "this for our cybersecurity tools — `port_scan` and `lookup_cve` — with **simulated** data so "
    "it is safe and reproducible. Below we print its tool definitions so you see the shape before "
    "we connect to it."
)
md("Here is the essence of `mcp_server.py` (the file beside this notebook has the full, "
   "documented version with simulated data):\n\n"
   "```python\n"
   "from mcp.server.fastmcp import FastMCP\n"
   "mcp = FastMCP(\"cyber-recon\")\n\n"
   "@mcp.tool()\n"
   "def port_scan(target: str) -> str:\n"
   "    \"\"\"Run a (simulated) port scan; return open ports + service versions.\"\"\"\n"
   "    ...                      # returns canned nmap-style output (safe, offline)\n\n"
   "@mcp.tool()\n"
   "def lookup_cve(service: str) -> str:\n"
   "    \"\"\"Look up known CVEs for a service in the local knowledge base.\"\"\"\n"
   "    ...\n\n"
   "@mcp.resource(\"kb://cve\")          # read-only data, fetched by URI\n"
   "def cve_kb() -> str:\n"
   "    ...\n\n"
   "if __name__ == \"__main__\":\n"
   "    mcp.run()                       # stdio transport by default\n"
   "```")
code(
    r'''# Build a tiny FastMCP server right here to SEE @tool registration (we don't run() it).
from mcp.server.fastmcp import FastMCP

demo = FastMCP("demo")

@demo.tool()
def greet(name: str) -> str:
    """Say hello to someone by name."""
    return f"hello, {name}"

# The decorated function is still directly callable...
print("greet('analyst') ->", greet("analyst"))

# ...and it is now a registered MCP tool whose input schema came from the type hints:
for t in run_async(demo.list_tools()):
    print(f"\nregistered tool : {t.name}")
    print(f"description     : {t.description}")
    print(f"input schema    : {t.inputSchema}")'''
)

# ---------------------------------------------------------------------------
# 8. Connecting a client (REAL)
# ---------------------------------------------------------------------------
slide("\U0001F4DE 8 — Connecting a Client (the real server)", [
    "Client spawns `mcp_server.py` over **stdio**",
    "`initialize()` → handshake & capability exchange",
    "`list_tools()` → discover what's available",
    "`call_tool(name, args)` → run it, get `content` back",
    "This is the real `mcp` SDK — not a mock",
])
script(
    "Now we talk to the real server. Using the `mcp` SDK, a client opens a stdio connection that "
    "launches `mcp_server.py` as a subprocess, performs an `initialize` handshake to exchange "
    "capabilities, and can then call `list_tools` to discover the server's tools and "
    "`call_tool` to run one. The code is asynchronous because the transport is, so we wrap it with "
    "the `run_async` helper from setup to call it from a normal cell. Watch the output: these are "
    "the genuine tool names and the real (simulated) scan result coming back from a separate "
    "process over the protocol. If the `mcp` package is not installed, the cell prints a notice and "
    "skips, so the rest of the notebook still runs."
)
code(
    r'''import os, sys

async def mcp_demo():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])
    # errlog -> devnull: in a Jupyter kernel sys.stderr has no real file handle,
    # which would break the subprocess launch; a real file avoids that.
    with open(os.devnull, "w") as errlog:
        async with stdio_client(params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()                   # handshake
                tools = await session.list_tools()           # discover
                names = [t.name for t in tools.tools]
                scan = await session.call_tool("port_scan", {"target": "10.0.0.5"})
                return names, scan.content[0].text

if MCP_AVAILABLE:
    try:
        tool_names, scan_text = run_async(mcp_demo())
        print("Discovered tools:", tool_names)
        print("\ncall_tool('port_scan', target='10.0.0.5') ->")
        print(scan_text)
    except Exception as e:
        print("Live client demo could not run here:", type(e).__name__, str(e)[:80])
        print("Run this notebook in Jupyter, or `python mcp_server.py` separately, to see it live.")
else:
    print("mcp not installed — skipping the live client demo. (pip install mcp)")'''
)

# ---------------------------------------------------------------------------
# 9. AI Agents — the loop
# ---------------------------------------------------------------------------
slide("\U0001F916 9 — AI Agents: The Reason–Act–Observe Loop", [
    "A **chain** runs fixed steps; an **agent** decides steps at runtime",
    "Loop: **reason** about the goal → **act** (call a tool) → **observe** result",
    "Repeat until the goal is met, then answer",
    "The LLM picks *which* tool and *what* arguments",
    "Tools are where the agent touches the real world",
])
script(
    "An agent is an LLM placed inside a loop with access to tools. Instead of following a script, "
    "it reasons about the goal, decides on an action — usually calling a tool with specific "
    "arguments — observes the result, and loops again, continuing until it judges the task done and "
    "produces a final answer. This reason-act-observe cycle, often called ReAct, is what makes an "
    "agent feel autonomous: the *control flow comes from the model*, not from you. Below we "
    "illustrate the loop with a deterministic stand-in 'policy' and local tool functions so it runs "
    "offline; the key thing to watch is that the sequence of tool calls is *chosen during "
    "execution* based on what each step returns, not fixed in advance."
)
code(
    r'''# Local tools the agent can use (stand-ins for the MCP tools):
def t_port_scan(target): return "21/ftp vsftpd 2.3.4; 22/ssh OpenSSH 7.2; 80/http Apache 2.4.49"
def t_lookup_cve(service): return "vsftpd 2.3.4 -> CVE-2011-2523 (backdoor, critical)"
TOOLS = {"port_scan": t_port_scan, "lookup_cve": t_lookup_cve}

def agent_policy(goal, observations):
    """A toy stand-in for the LLM's decision. Real agents let the model choose."""
    if not observations:                       return ("port_scan", {"target": goal})
    if "vsftpd" in observations[-1] and len(observations) == 1:
                                                return ("lookup_cve", {"service": "vsftpd 2.3.4"})
    return ("FINISH", {})

def run_agent(goal, max_steps=5):
    obs = []
    for step in range(1, max_steps + 1):
        action, args = agent_policy(goal, obs)
        if action == "FINISH":
            print(f"  step {step}: FINISH -> produce report"); break
        print(f"  step {step}: REASON -> call {action}{args}")
        result = TOOLS[action](**args)
        print(f"           OBSERVE -> {result}")
        obs.append(result)
    return obs

print("Goal: assess host 10.0.0.5\n")
run_agent("10.0.0.5")'''
)

# ---------------------------------------------------------------------------
# 10. Agents + MCP
# ---------------------------------------------------------------------------
slide("\U0001F517 10 — Agents + MCP: A Standard Toolbox", [
    "An agent needs tools; MCP is how it gets them **without custom code**",
    "Point the agent at MCP servers → it discovers tools at runtime",
    "Swap, add, or share servers without touching the agent",
    "Same tools usable by *any* MCP-aware host",
    "Decouples *who builds the tool* from *who uses it*",
])
script(
    "Here is why agents and MCP belong together. An agent is only as useful as the tools it can "
    "reach, and hard-coding each tool into the agent recreates the M×N mess from topic 1. MCP "
    "fixes that: you point the agent at one or more MCP servers, and it discovers their tools at "
    "runtime via `tools/list`. You can add a new capability by starting another server, swap a "
    "simulated scanner for a real one, or share a server across teams — all without editing the "
    "agent's code. It also cleanly decouples responsibilities: a security team can publish a "
    "vetted scanning server while application teams simply consume it. In short, MCP turns tools "
    "into reusable, standardized infrastructure that any agent can pick up."
)
code(
    r'''print("Hard-coded tools (brittle):")
print("  agent  --has to import & wrap-->  nmap, CVE API, SIEM, ...   (changes => edit the agent)")
print("\nMCP tools (decoupled):")
print("  agent  --speaks MCP-->  [ server: nmap ] [ server: CVE ] [ server: SIEM ]")
print("  add/replace a server  =>  agent gains/loses tools with NO code change")
print("  the SAME servers also work in Claude Desktop, an IDE, or a teammate's agent")'''
)

# ---------------------------------------------------------------------------
# 11. LangChain/LangGraph managing MCP
# ---------------------------------------------------------------------------
slide("\U0001F9E9 11 — LangChain/LangGraph Managing MCP", [
    "`langchain-mcp-adapters` bridges MCP ↔ LangChain tools",
    "`load_mcp_tools(session)` → MCP tools become LangChain tools",
    "`MultiServerMCPClient({...})` connects to several servers at once",
    "Feed the tools to `create_react_agent` (LangGraph)",
    "The agent now calls MCP tools through the LLM",
])
script(
    "LangChain integrates MCP through the `langchain-mcp-adapters` package, which converts MCP "
    "tools into the LangChain tool objects you met in the LangChain module. Given an open client "
    "session, `load_mcp_tools` returns a list of ready-to-use LangChain tools; "
    "`MultiServerMCPClient` goes further and connects to several servers at once, merging their "
    "tools. You then hand those tools to a LangGraph agent built with `create_react_agent`, pair it "
    "with a chat model, and the agent will call your MCP tools as needed. Below we actually load "
    "our server's tools as LangChain tools — no LLM required for that step — and print them, then "
    "show the few lines that wire them into a live agent. This is the bridge we use in the "
    "`cybersecurity_automation.ipynb` capstone."
)
code(
    r'''async def load_tools_demo():
    import os, sys
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from langchain_mcp_adapters.tools import load_mcp_tools
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])
    with open(os.devnull, "w") as errlog:
        async with stdio_client(params, errlog=errlog) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                return await load_mcp_tools(session)      # MCP tools -> LangChain tools

try:
    from langchain_mcp_adapters.tools import load_mcp_tools  # noqa: F401
    have_adapters = MCP_AVAILABLE
except ImportError:
    have_adapters = False

if have_adapters:
    try:
        lc_tools = run_async(load_tools_demo())
        print("MCP tools loaded as LangChain tools:")
        for t in lc_tools:
            print(f"  - {t.name:12s} ({type(t).__name__}): {t.description.splitlines()[0][:60]}")
    except Exception as e:
        print("Could not load tools here:", type(e).__name__, str(e)[:80])
        print("Run in Jupyter to see MCP tools load as LangChain tools.")
else:
    print("langchain-mcp-adapters not installed — skipping. (pip install langchain-mcp-adapters)")

print("""
# Wire them into a live LangGraph agent (needs an API key):
# from langchain_mcp_adapters.client import MultiServerMCPClient
# from langgraph.prebuilt import create_react_agent
# from langchain_openai import ChatOpenAI
#
# client = MultiServerMCPClient({"recon": {"command": "python",
#         "args": ["mcp_server.py"], "transport": "stdio"}})
# tools = await client.get_tools()
# agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini"), tools)
# await agent.ainvoke({"messages": "Assess host 10.0.0.5 and summarize the risk."})
""")'''
)

# ---------------------------------------------------------------------------
# 12. Comparison: chain vs agent vs agent+MCP
# ---------------------------------------------------------------------------
slide("⚖️ 12 — Chain vs. Agent vs. Agent + MCP", [
    "**Chain**: fixed steps you design — predictable, cheap",
    "**Agent**: model chooses steps — flexible, dynamic",
    "**Agent + MCP**: dynamic *and* tools are standardized & reusable",
    "Cost & unpredictability rise left → right",
    "This is the arc of the whole course",
])
script(
    "Let's place today's ideas against the rest of the course. A chain runs a fixed sequence you "
    "designed: predictable, cheap, easy to debug — what we built in the LangChain and RAG modules. "
    "An agent lets the model choose the steps at runtime: far more flexible, but costlier in tokens "
    "and harder to predict. Adding MCP doesn't change the agent's autonomy; it changes where the "
    "tools come from — standardized, reusable servers instead of bespoke code — which is what makes "
    "the autonomous approach actually maintainable and scalable. As you move left to right you "
    "trade predictability and cost for flexibility and reach. The table captures the progression "
    "we will demonstrate end to end in the capstone notebook."
)
code(
    r'''rows = [
    ("Control flow",    "you design it",  "model decides",   "model decides"),
    ("Data source",     "LLM memory",     "RAG / tools",     "RAG + MCP tools"),
    ("Tool integration","hard-coded",     "hard-coded",      "standardized (MCP)"),
    ("Flexibility",     "fixed",          "dynamic",         "dynamic + reusable"),
    ("Cost / risk",     "low",            "higher",          "higher"),
]
print(f"  {'':18s}{'CHAIN':16s}{'AGENT':16s}{'AGENT + MCP'}")
print("  " + "-" * 66)
for label, a, b, c in rows:
    print(f"  {label:18s}{a:16s}{b:16s}{c}")'''
)

# ---------------------------------------------------------------------------
# 13. Security considerations
# ---------------------------------------------------------------------------
slide("\U0001F512 13 — Security: Giving an LLM Tools is Dangerous", [
    "**Untrusted servers**: a malicious server can return harmful tool output",
    "**Tool-description / prompt injection**: text from a tool can hijack the agent",
    "**Over-broad permissions**: least privilege for every tool",
    "**Confused deputy**: the agent acts with *its* credentials, not the user's",
    "**Human-in-the-loop** for destructive actions; log every tool call",
])
script(
    "For a security audience this topic is essential: handing an LLM real tools turns prompt "
    "injection into remote code execution. Treat MCP servers like any third-party dependency — an "
    "untrusted server can return crafted output, and because the agent reads tool results as text, "
    "a malicious description or result can carry instructions that hijack the agent's next action. "
    "Apply least privilege: each tool should do the minimum it needs, never expose a raw shell, and "
    "scope credentials tightly to avoid a confused-deputy problem where the agent wields more "
    "authority than the user should have. Gate destructive or irreversible actions behind "
    "human approval, validate and sandbox tool inputs and outputs, and log every tool call for "
    "audit. Autonomy is powerful precisely because it is dangerous — engineer the guardrails first."
)
code(
    r'''def needs_human_approval(tool, args):
    DESTRUCTIVE = {"delete", "shutdown", "exploit", "deploy", "block_ip", "quarantine"}
    return any(d in tool.lower() for d in DESTRUCTIVE)

for tool, args in [("port_scan", {"target": "10.0.0.5"}),
                   ("lookup_cve", {"service": "vsftpd"}),
                   ("quarantine_host", {"host": "10.0.0.5"}),
                   ("block_ip", {"ip": "203.0.113.9"})]:
    gate = "NEEDS HUMAN APPROVAL" if needs_human_approval(tool, args) else "auto-allowed (read-only)"
    print(f"  {tool:18s} -> {gate}")
print("\nGuardrail pattern: read-only tools run freely; state-changing tools require sign-off.")'''
)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
slide("✅ Summary & Key Takeaways", [
    "MCP standardizes LLM ↔ tools/data: **M+N**, not M×N",
    "**Host / client / server** over JSON-RPC; **tools / resources / prompts**",
    "Transports: **stdio** (local) and **HTTP** (remote)",
    "**Agents** add a reason–act–observe loop; MCP gives them a standard toolbox",
    "**Security first**: least privilege, injection-aware, human-in-the-loop",
])
script(
    "To wrap up: MCP is an open, JSON-RPC protocol that standardizes how AI applications connect to "
    "tools and data, collapsing the M-by-N integration problem into M plus N. Its architecture is "
    "host, client, and server, and a server exposes tools to call, resources to read, and prompts "
    "to reuse, over either stdio for local use or HTTP for remote. Agents put an LLM in a "
    "reason-act-observe loop where the model chooses the actions, and MCP is how that agent gets a "
    "standardized, swappable toolbox — which LangChain wires up with `load_mcp_tools` and a "
    "LangGraph agent. Above all, giving a model tools demands a security-first mindset: least "
    "privilege, awareness of injection through tool output, and human approval for anything "
    "destructive. Next we put it all together to automate a penetration test in "
    "`cybersecurity_automation.ipynb`."
)
code(
    r'''print("The course arc in one line:")
print("  Chains (fixed)  ->  RAG (grounded)  ->  Agents + MCP (autonomous, standardized tools)")
print("\nNext: cybersecurity_automation.ipynb — a pentest assistant that evolves across all three.")'''
)

# ---------------------------------------------------------------------------
nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
        "language_info": {"name": "python"},
        "colab": {"provenance": []},
    },
    "cells": cells,
}

with open("mcp.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Wrote mcp.ipynb with {len(cells)} cells.")
