# Module 7 — Model Context Protocol (MCP)

A two-week graduate module for **Applied AI for Cybersecurity (IT7075C)**. It teaches the **Model
Context Protocol (MCP)**: why it exists, its host/client/server design, how to **build a server**
with FastMCP, and how to **connect a client and an LLM agent** that drives the tools. The module is
built from **Omar Santos's** materials (book *Agentic AI for Cybersecurity*, Ch. 2; the
*RAG, AI Apps, and AI Agents* LinkedIn course; and the
[AI-agents-for-cybersecurity](https://github.com/santosomar/AI-agents-for-cybersecurity) repo).

It builds on [Module 5 — LangChain](../05_LangChain/) and [Module 6 — LangGraph](../06_LangGraph/),
and feeds the orchestration capstone in [Module 8](../08_Cybersecurity_Orchestration/).

## Notebooks

- **[mcp_part1.ipynb](mcp_part1.ipynb)** — *Part 1: Concepts & building a server.* The M×N
  integration problem, host/client/server roles, the primitives (tools, resources, prompts),
  transports (stdio vs HTTP), and building a server with **FastMCP**.
- **[mcp_part2.ipynb](mcp_part2.ipynb)** — *Part 2: Connecting a client & an agent.* Open a client
  over stdio, discover and call tools, read a resource, then let an **LLM agent** drive the tools
  with `langchain-mcp-adapters` — close to Omar's `cyber_agent.py`.
- **[mcp_sample.ipynb](mcp_sample.ipynb)** — a minimal copy-paste **server + client** pair to use
  as the skeleton for Mini-Project 5.
- **[mcp_server.py](mcp_server.py)** — a real, runnable MCP server (FastMCP) exposing **safe,
  simulated** security tools (`port_scan`, `lookup_cve`, `list_targets`) and a CVE resource
  (`kb://cve`). The Part 2 client launches it automatically over stdio.

Each concept is presented as three cells: a **slide** (bullets to project), an **instructor script**
(narration to read aloud), and a **runnable code** cell.

## ⚠️ Ethics & safety

All scanning here is **simulated** against fictional lab hosts (`10.0.0.x`); no packets are sent.
Real scanning appears only in comments. Run real scans/exploits **only** against systems you are
explicitly authorized to test (your isolated Metasploitable VM or an approved practice target).
Keep API keys in `.env` / Colab Secrets — never in code.

## Setup

```bash
pip install -r requirements.txt
```

Part 1 and the manual client calls in Part 2 run **with no API key**. Only the **live agent** step
in Part 2 needs `OPENAI_API_KEY` (e.g. a `.env` in the project root); without it, that step prints a
notice and skips.

Open any notebook in Jupyter, VS Code, or Colab and run top to bottom. The client cells **launch
`mcp_server.py` automatically** as a stdio subprocess — you don't start it yourself. To run the
server standalone: `python mcp_server.py`.

> **Windows/Jupyter note:** MCP clients are async and the notebook already owns an event loop, so
> Part 2 runs each client call in a worker thread and sends the server's stderr to a **real file**
> (`mcp_server_stderr.log`). Passing the notebook's `sys.stderr` triggers a `fileno` error.

## Two-week plan

| | Deliverable |
|---|---|
| **Lecture** | `Module7_MCP.pptx` (slides) + Part 1 & Part 2 notebooks |
| **Week 1** | `Module7_Week1_Concepts` — short concept check + add one tool to the server |
| **Week 2** | **Mini-Project 5** — build your own MCP **server** *and* a **client/agent** that uses it |

*(Slides and assignments are generated under `assignments and projects/` and are not pushed to GitHub.)*

## Files

- `mcp_part1.ipynb`, `mcp_part2.ipynb`, `mcp_sample.ipynb` — the lecture and sample notebooks.
- `mcp_server.py` — the runnable MCP server with simulated security tools.
- `cve_knowledge_base.md` — the CVE data the server's `lookup_cve` tool and `kb://cve` resource use.
- `_build_mcp_part1.py`, `_build_mcp_part2.py`, `_build_mcp_sample.py` — generators for the notebooks.
- `requirements.txt` — Python dependencies.

## Editing the notebooks

The notebooks are **generated from the `_build_*.py` scripts**, not edited by hand. To change a
lecture, edit the build script and regenerate, e.g.:

```bash
python _build_mcp_part1.py     # -> mcp_part1.ipynb
```
