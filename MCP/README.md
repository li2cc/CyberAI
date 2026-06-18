# MCP & AI Agents + a Pentest Automation Capstone

A graduate lecture module for the *AI for Cybersecurity* course. It teaches the **Model Context
Protocol (MCP)** and **AI agents**, then ties the whole course together by automating a
penetration test that evolves through **chains → RAG → agents + MCP**. It builds on the
[LangChain](../LangChain/) and [RAG](../RAG/) modules.

The module is two Jupyter notebooks plus a real, runnable MCP server:

- **[mcp.ipynb](mcp.ipynb)** — the *concepts* lecture: the M×N integration problem, MCP's
  host/client/server architecture, primitives (tools, resources, prompts), the JSON-RPC messages,
  transports (stdio vs HTTP), building a server with **FastMCP**, connecting a client, the **agent
  loop**, **LangChain/LangGraph managing MCP**, a chain-vs-agent-vs-MCP comparison, and the
  **security risks** of giving an LLM tools.
- **[cybersecurity_automation.ipynb](cybersecurity_automation.ipynb)** — the *worked example /
  capstone*: a penetration-testing assistant built three times — as a **chain** (Lecture 1), then
  with **RAG** over a CVE knowledge base (Lecture 2), then as an **agent** that orchestrates MCP
  tools (Lecture 3).
- **[mcp_server.py](mcp_server.py)** — a real MCP server (FastMCP) exposing **safe, simulated**
  cybersecurity tools (`port_scan`, `lookup_cve`, `list_targets`) and a CVE resource. The notebooks
  connect to it over stdio.

Each topic is presented as three cells: a **slide** (bullets to project), an **instructor script**
(narration to read aloud), and a **runnable code** cell with clean output.

## ⚠️ Ethics & safety

All scanning in this module is **simulated** against fictional lab hosts (`10.0.0.x`); no packets
are ever sent. Real scanning (shelling out to `nmap`) appears only in comments. Run real scans
**only** against systems you are explicitly authorized to test.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) API key for the live agent

`mcp.ipynb` and Stages 1–2 (plus the offline agent) of `cybersecurity_automation.ipynb` run **with
no API key** — they use simulated tools, local embeddings, and a deterministic stand-in model. Only
the **live LangGraph agent** step needs `OPENAI_API_KEY` (e.g. in a `.env` file in the project
root):

```
OPENAI_API_KEY=sk-your-openai-key-here
```

If no key is set, that step prints a notice and skips, so the rest of the notebook still runs.

### 3. Open a notebook

Open either `.ipynb` in Jupyter, VS Code, or Colab and run the cells top to bottom. The cells that
connect to the MCP server **launch `mcp_server.py` automatically** as a stdio subprocess — you do
not need to start it yourself. You can also run it standalone:

```bash
python mcp_server.py
```

## Files

- `mcp.ipynb` — MCP + AI Agents concepts (runs offline; ships with outputs).
- `cybersecurity_automation.ipynb` — the chains→RAG→agent+MCP capstone (Stages 1–2 + offline agent
  run offline; the live agent step needs a key).
- `mcp_server.py` — the deployable MCP server with simulated security tools.
- `cve_knowledge_base.md` — the CVE knowledge base the RAG stage retrieves from.
- `_build_mcp_notebook.py` — generator that writes `mcp.ipynb`.
- `_build_cybersecurity_automation.py` — generator that writes `cybersecurity_automation.ipynb`.
- `requirements.txt` — Python dependencies.

## Editing the notebooks

The notebooks are **generated from the `_build_*.py` scripts**, not edited by hand. To change a
lecture, edit the build script and regenerate:

```bash
python _build_mcp_notebook.py                  # -> mcp.ipynb
python _build_cybersecurity_automation.py      # -> cybersecurity_automation.ipynb
```

To re-embed fresh outputs in the concepts notebook after regenerating:

```bash
jupyter nbconvert --to notebook --execute --inplace mcp.ipynb
```

## How It Works

`mcp.ipynb` teaches the protocol with an in-notebook **mock** server/client (so you can read the
raw JSON-RPC) and then connects to the **real** `mcp_server.py` over stdio to list and call tools
for real. It then introduces the agent loop and shows `langchain-mcp-adapters` turning MCP tools
into LangChain tools for a LangGraph agent.

`cybersecurity_automation.ipynb` is the payoff. The same pentest assistant is built three ways so
students feel each limitation and its fix:

1. **Chains** — `nmap → LLM parses → LLM analyzes → report`. The LLM *guesses* vulnerabilities from
   memory (no CVE IDs) — motivating RAG.
2. **RAG** — `nmap → parse → retrieve real CVEs → LLM analyzes → report`. Answers now cite real
   CVEs (e.g. CVE-2011-2523) from the knowledge base — but the pipeline is still fixed.
3. **Agent + MCP** — an agent *decides* which tools to call, via the standardized MCP server.
   Dynamic, scalable, and reusable.

**The one-line story:** *we start by using LLMs to interpret security data, then make them accurate
with real knowledge, and finally make them autonomous with agents and standardized tools.*
