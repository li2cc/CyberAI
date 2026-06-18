"""Generator for cybersecurity_automation.ipynb — the course capstone.

A penetration-testing assistant that EVOLVES across the three ideas of the
course, so students feel the limitations and fixes first-hand:

  Stage 1 — CHAINS  : nmap -> LLM parses -> LLM analyzes (from memory) -> report
                      Limitation: the LLM *guesses* vulnerabilities (hallucination).
  Stage 2 — RAG     : nmap -> parse -> RETRIEVE real CVEs -> LLM analyzes -> report
                      Fix: answers are grounded in a real CVE knowledge base.
  Stage 3 — AGENT+MCP: an agent DECIDES which tools to call, via a standard
                      MCP server (mcp_server.py). Fix: dynamic, scalable, reusable.

Presentation style matches RAG/rag_example.ipynb and LangChain/langchain_example.ipynb:
each step = slide + instructor script + runnable code. Stages 1-2 and the offline
agent run with no API key; the live agent step needs OPENAI_API_KEY + the `mcp` SDK.

SAFETY: all scanning is SIMULATED against fictional lab hosts. Real scanning is
shown only in comments and must target only systems you are authorized to test.

Run:  python _build_cybersecurity_automation.py   ->  writes cybersecurity_automation.ipynb
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
md(
    "# Automating a Penetration Test: Chains → RAG → Agents + MCP\n"
    "### The Course Capstone — One System, Three Evolutions\n\n"
    "**Audience:** Graduate students who have completed the `LangChain/`, `RAG/`, and `MCP/` "
    "concept notebooks.\n\n"
    "**Goal:** Build a penetration-testing assistant and watch it grow up across the three big "
    "ideas of the course. Each stage fixes a real limitation of the last:\n\n"
    "1. \U0001F517 **Chains** — `nmap → LLM parses → LLM analyzes → report`. "
    "*The LLM guesses vulnerabilities from memory.*\n"
    "2. \U0001F50D **RAG** — `… → retrieve real CVEs → LLM analyzes → report`. "
    "*Answers are grounded in a real CVE knowledge base.*\n"
    "3. \U0001F916 **Agent + MCP** — *the agent decides which tools to call*, through a standard "
    "MCP server. *Dynamic, scalable, reusable.*\n\n"
    "> **Reproducibility:** Stages 1–2 and the offline agent run **with no API key** "
    "(simulated `nmap`, local embeddings, a deterministic stand-in LLM). The **live agent** step "
    "needs `OPENAI_API_KEY` and the `mcp` SDK; it is guarded so the rest of the notebook still "
    "runs.\n\n"
    "> ⚠️ **Ethics & safety:** All scanning here is **simulated** against fictional lab hosts "
    "(`10.0.0.x`). Real scanning (shelling out to `nmap`) is shown only in comments — run it "
    "**only** against systems you are explicitly authorized to test."
)

# ---- Setup ------------------------------------------------------------------
md("## \U0001F6E0️ Setup")
code(
    r'''# If needed:
# !pip install -q langchain-core sentence-transformers
# Optional (Stage 3 live agent): !pip install -q mcp langchain-mcp-adapters langgraph langchain-openai

import re
from typing import List
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage

print("Core imports ready.")'''
)
md("### Simulated recon + a stand-in LLM (offline, no key)\n\n"
   "We simulate `nmap` against fictional lab hosts (the same hosts our `mcp_server.py` knows), and "
   "we reuse the deterministic **stand-in chat model** idea from earlier modules. The stand-in is "
   "intentionally simple — its job is to show the *pipeline mechanics*; the live OpenAI step later "
   "shows real, fluent analysis.")
code(
    r'''# --- Simulated nmap (safe, offline; mirrors mcp_server.py) -------------------
SIMULATED_HOSTS = {
    "10.0.0.5": ["21/tcp open ftp vsftpd 2.3.4",
                 "22/tcp open ssh OpenSSH 7.2p2",
                 "80/tcp open http Apache httpd 2.4.49"],
    "10.0.0.8": ["445/tcp open microsoft-ds Samba smbd 3.5.0",
                 "3306/tcp open mysql MySQL 5.5.40"],
    "10.0.0.12": ["23/tcp open telnet Linux telnetd",
                  "6379/tcp open redis Redis 4.0.9"],
}

def simulated_nmap(target: str) -> str:
    lines = SIMULATED_HOSTS.get(target, [])
    return "\n".join(lines) if lines else "(no open ports)"
    # --- Real scan (AUTHORIZED targets only) ---
    # import subprocess
    # return subprocess.run(["nmap","-sV",target], capture_output=True, text=True).stdout

def parse_services(scan_output: str) -> List[str]:
    """Pull 'service version' strings out of nmap-style lines."""
    services = []
    for line in scan_output.splitlines():
        toks = line.split()
        if len(toks) >= 4 and "/" in toks[0]:        # e.g. 21/tcp open ftp vsftpd 2.3.4
            services.append(" ".join(toks[3:]))
    return services

print("Scan of 10.0.0.5:\n" + simulated_nmap("10.0.0.5"))
print("\nParsed services:", parse_services(simulated_nmap("10.0.0.5")))'''
)

# ===========================================================================
# STAGE 1 — CHAINS
# ===========================================================================
md("---\n## \U0001F517 STAGE 1 — Chains: An LLM-Powered Pentest Assistant\n\n"
   "*Theme: “Use LangChain to turn an LLM into a cybersecurity assistant.”*")

slide("\U0001F517 Stage 1 — Recon → Parse → Analyze → Report (a Chain)", [
    "Run (simulated) nmap on a target",
    "LLM **parses** the scan into a service list",
    "LLM **analyzes** each service for likely vulnerabilities",
    "LLM **generates** a readable report",
    "All wired as a LangChain chain: `prompt | model | parser`",
])
script(
    "We start where Lecture 1 left off: a fixed pipeline built from chains. We scan a host, then "
    "use the LLM in three roles — parser, analyst, and report writer — strung together with LCEL. "
    "The scan output goes into a prompt, the model reasons about what each service might be "
    "vulnerable to, and an output parser hands us a clean report. This is genuinely useful: in "
    "thirty minutes you can stand up an assistant that turns raw scanner output into prose. Watch "
    "the structure, because the *shape* — prompt, model, parser — is exactly what you learned in "
    "the LangChain module, now applied to security. We use the offline stand-in model so it runs "
    "in class; the live version is a one-line swap shown later."
)
code(
    r'''def _analyst_from_memory(prompt_value):
    """Stand-in LLM playing 'security analyst from general knowledge'."""
    text = prompt_value.to_string() if hasattr(prompt_value, "to_string") else str(prompt_value)
    services = [l for l in text.splitlines() if "/" not in l and l.strip()
                and any(c.isdigit() for c in l)]
    body = ("Based on general knowledge, these services *may* have known issues "
            "(UNVERIFIED — the model is guessing):\n")
    for s in services:
        body += f"  - {s.strip()}: possibly outdated; could have public exploits.\n"
    return AIMessage(content=body + "Recommend manual verification.")

analyst_memory_llm = RunnableLambda(_analyst_from_memory)

report_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a penetration-testing assistant. Analyze the services and write a short "
               "vulnerability report."),
    ("user", "Services found:\n{services}"),
])

stage1_chain = report_prompt | analyst_memory_llm | StrOutputParser()

services = parse_services(simulated_nmap("10.0.0.5"))
report = stage1_chain.invoke({"services": "\n".join(services)})
print("=== STAGE 1 REPORT (chain, LLM from memory) ===\n")
print(report)'''
)

slide("⚠️ Stage 1 — The Critical Limitation", [
    "The LLM **guesses** vulnerabilities from its training memory",
    "No CVE IDs, no sources, no version-specific accuracy",
    "Training data is stale; new CVEs are unknown",
    "→ **hallucination risk** in a security context = dangerous",
    "This motivates Stage 2 (RAG)",
])
script(
    "Now the crucial teaching moment. Read that report again: it is plausible, fluent, and "
    "unverifiable. The model is guessing from general training knowledge, so it gives no CVE "
    "identifiers, cites no sources, and cannot know about vulnerabilities disclosed after its "
    "training cutoff. In most domains a vague answer is merely unhelpful; in security it is "
    "dangerous, because a hallucinated 'all clear' or a wrong remediation can leave a real hole "
    "open. The lesson students should take away is that an LLM's memory is the wrong source of "
    "truth for fast-moving factual data like vulnerabilities. That single limitation is exactly "
    "what Retrieval-Augmented Generation fixes, which is where we go next."
)
code(
    r'''print("What Stage 1 produced:")
print("  - source of 'facts' : the LLM's training memory (a guess)")
print("  - CVE identifiers    : none")
print("  - up to date         : no (frozen at training cutoff)")
print("  - trustworthy        : NOT for security decisions")
print("\nFix: ground the analysis in a real, current CVE knowledge base -> Stage 2 (RAG).")'''
)

# ===========================================================================
# STAGE 2 — RAG
# ===========================================================================
md("---\n## \U0001F50D STAGE 2 — RAG: Ground the Analysis in Real CVEs\n\n"
   "*Theme: “From guessing → retrieving real security knowledge.”*")

slide("\U0001F50D Stage 2 — Retrieve Real CVEs, Then Analyze", [
    "Embed a CVE knowledge base into a vector store (the RAG module)",
    "For each detected service, **retrieve** matching CVE entries",
    "Feed the *retrieved* CVEs to the LLM as context",
    "Report now cites **real CVE IDs**, not guesses",
    "Updated pipeline: `nmap → parse → retrieve → analyze → report`",
])
script(
    "Stage 2 upgrades the assistant exactly as Lecture 2 promised: we replace the model's memory "
    "with retrieval from a real CVE knowledge base. Using the embeddings and vector-store tools "
    "from the RAG module, we index `cve_knowledge_base.md`, then for each service the scan found we "
    "retrieve the most relevant CVE entries and pass those into the prompt as context. The model's "
    "job changes from *recall* to *reading comprehension over supplied facts* — far more reliable. "
    "The report now references concrete identifiers like CVE-2011-2523 with real descriptions and "
    "remediations. Same scan, same model, but grounded output. This is the single most important "
    "upgrade for any real security assistant."
)
code(
    r'''from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore

class STEmbeddings(Embeddings):
    def __init__(self, name="all-MiniLM-L6-v2"):
        self.m = SentenceTransformer(name)
    def embed_documents(self, texts): return self.m.encode(texts, normalize_embeddings=True).tolist()
    def embed_query(self, text):      return self.m.encode(text, normalize_embeddings=True).tolist()

# Index the CVE knowledge base (one Document per '#' section).
kb_text = open("cve_knowledge_base.md", encoding="utf8").read()
sections = [s.strip() for s in kb_text.split("#") if s.strip()]
docs = [Document(page_content=s, metadata={"title": s.splitlines()[0]}) for s in sections]

cve_store = InMemoryVectorStore(STEmbeddings())
cve_store.add_documents(docs)
print(f"Indexed {len(docs)} CVE entries into the vector store.\n")

def retrieve_cves(service: str, k: int = 1, threshold: float = 0.30) -> str:
    hits = cve_store.similarity_search_with_score(service, k=k)
    kept = [d.page_content for d, score in hits if score >= threshold]
    return "\n\n".join(kept) if kept else f"No known CVEs found for: {service}"

# Show retrieval per service:
for s in services:
    title = retrieve_cves(s).splitlines()[0]
    print(f"  {s:28s} ->  {title}")'''
)
md("Now build the **RAG chain**: retrieve CVEs for the services, then have the (stand-in) LLM "
   "write a grounded report from that real context.")
code(
    r'''def _analyst_grounded(prompt_value):
    """Stand-in LLM that answers ONLY from the retrieved CVE context (extractive)."""
    text = prompt_value.to_string() if hasattr(prompt_value, "to_string") else str(prompt_value)
    context = text.split("# Retrieved CVEs", 1)[-1].split("Human:", 1)[0].strip()
    cve_ids = re.findall(r"CVE-\d{4}-\d+", context)
    head = f"GROUNDED REPORT — cites {len(set(cve_ids))} real CVE(s): {', '.join(sorted(set(cve_ids)))}\n\n"
    return AIMessage(content=head + context[:600] + (" ..." if len(context) > 600 else ""))

grounded_llm = RunnableLambda(_analyst_grounded)
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a pentest assistant. Use ONLY the retrieved CVEs to assess the host.\n"
               "# Retrieved CVEs\n{context}"),
    ("user", "Assess host {target} given services:\n{services}"),
])

def build_context(target):
    return "\n\n".join(retrieve_cves(s) for s in parse_services(simulated_nmap(target)))

stage2_chain = (
    {"context": RunnableLambda(build_context),
     "services": lambda t: "\n".join(parse_services(simulated_nmap(t))),
     "target": RunnableLambda(lambda t: t)}
    | rag_prompt | grounded_llm | StrOutputParser()
)

print("=== STAGE 2 REPORT (RAG, grounded in real CVEs) ===\n")
print(stage2_chain.invoke("10.0.0.5"))'''
)

slide("✅ Stage 2 — What Improved", [
    "Vulnerability facts come from **real documents**, not memory",
    "Report cites **specific CVE IDs** with descriptions & fixes",
    "Hallucination sharply **reduced**",
    "Knowledge base is **updatable** without retraining",
    "Still a *fixed* pipeline — Stage 3 makes it dynamic",
])
script(
    "Compare the two reports side by side and the win is obvious: Stage 2 names real CVEs with "
    "real remediations drawn from documents, while Stage 1 offered fluent guesses. Accuracy is up, "
    "hallucination is down, and crucially the knowledge base can be refreshed the moment a new CVE "
    "is published — no model retraining required. This is exactly why RAG is foundational for "
    "domain-specific assistants. But notice what is *still* true: the pipeline is fixed. We "
    "hard-coded the order — scan, then parse, then retrieve, then analyze — and the assistant can "
    "only ever do that one sequence. What if a finding should trigger a deeper scan, or a different "
    "tool? For that the system must *decide* for itself, which is Stage 3: agents and MCP."
)
code(
    r'''print(f"{'':22s}{'STAGE 1 (chain)':22s}{'STAGE 2 (RAG)'}")
print("-" * 60)
for label, a, b in [("Vulnerability info", "LLM memory", "real CVE documents"),
                    ("CVE identifiers",   "none",       "yes (e.g. CVE-2011-2523)"),
                    ("Accuracy",          "medium",     "high"),
                    ("Hallucination",     "high",       "reduced"),
                    ("Updatable",         "retrain",    "edit the KB")]:
    print(f"{label:22s}{a:22s}{b}")'''
)

# ===========================================================================
# STAGE 3 — AGENT + MCP
# ===========================================================================
md("---\n## \U0001F916 STAGE 3 — Agents + MCP: Let the System Decide\n\n"
   "*Theme: “From pipelines → autonomous cybersecurity systems.”*")

slide("\U0001F916 Stage 3 — An Agent Orchestrates MCP Tools", [
    "Expose `port_scan` and `lookup_cve` as **MCP tools** (`mcp_server.py`)",
    "An **agent** decides *which* tool to call, *when*, and *with what*",
    "Loop: reason → call a tool → observe → repeat → report",
    "Tools are standardized & reusable (swap/add servers freely)",
    "Final pipeline is **dynamic**, not hard-coded",
])
script(
    "Stage 3 removes the last constraint: the fixed sequence. Instead of us scripting scan-then-"
    "retrieve, we expose those capabilities as MCP tools on the server we built in the MCP module, "
    "and we hand them to an agent. The agent runs the reason-act-observe loop: it decides to scan "
    "a host, reads the result, decides to look up CVEs for the services it found, and continues "
    "until it can write the report. The control flow now comes from the model, and because the "
    "tools are MCP-standardized we can add a new scanner or a SIEM server later without touching "
    "the agent. First we run a deterministic **offline** version so you can watch the loop make "
    "decisions with no key; then we show the **live** LangGraph + MCP agent."
)
code(
    r'''# --- Offline agent: a deterministic loop that DECIDES its next tool call ------
def tool_port_scan(target): return simulated_nmap(target)
def tool_lookup_cve(service): return retrieve_cves(service).splitlines()[0]
AGENT_TOOLS = {"port_scan": tool_port_scan, "lookup_cve": tool_lookup_cve}

def offline_agent(goal_target, max_steps=8):
    print(f"GOAL: assess host {goal_target}\n")
    findings, scanned, services_left = [], False, []
    for step in range(1, max_steps + 1):
        # --- the 'policy' (a real agent lets the LLM choose this) ---
        if not scanned:
            action, args = "port_scan", {"target": goal_target}
        elif services_left:
            action, args = "lookup_cve", {"service": services_left.pop(0)}
        else:
            print(f"  step {step}: REASON -> enough info, write the report"); break

        print(f"  step {step}: REASON -> call {action}({args})")
        result = AGENT_TOOLS[action](**args)
        print(f"           OBSERVE -> {result[:70]}{'...' if len(result) > 70 else ''}")
        if action == "port_scan":
            scanned = True
            services_left = parse_services(result)
        else:
            findings.append(result)
    print("\n=== STAGE 3 REPORT (agent-orchestrated) ===")
    for f in findings:
        print("  -", f)

offline_agent("10.0.0.5")'''
)

slide("\U0001F680 Stage 3 (Live) — LangGraph Agent over the MCP Server", [
    "`load_mcp_tools` → MCP tools become LangChain tools",
    "`create_react_agent(llm, tools)` builds the agent loop for you",
    "The LLM now picks tools dynamically at runtime",
    "Needs `OPENAI_API_KEY` + the `mcp` SDK (else this step skips)",
    "Same `mcp_server.py` you connected to in `mcp.ipynb`",
])
script(
    "Finally, the real thing. We connect to `mcp_server.py` over stdio, load its tools as LangChain "
    "tools with `load_mcp_tools`, and build a LangGraph ReAct agent with `create_react_agent`, "
    "backed by a real OpenAI model. Now the agent genuinely decides: it will call `port_scan`, read "
    "the services, call `lookup_cve` for each, and synthesize a grounded report — and it would just "
    "as easily use a new tool if we added one to the server. This step needs an API key and the "
    "`mcp` package, so it is guarded; without them it prints how to run it. Everything before this "
    "ran offline, so the lecture works either way. This is the destination of the whole course: an "
    "autonomous, grounded, tool-using security assistant built on standard parts."
)
code(
    r'''import os, sys

async def run_live_agent(goal):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from langchain_mcp_adapters.tools import load_mcp_tools
    from langgraph.prebuilt import create_react_agent
    from langchain_openai import ChatOpenAI

    import asyncio
    # errlog=sys.stderr surfaces server crashes (e.g. a bad import); swallowing
    # it to os.devnull turns a dead server into a silent hang on initialize().
    params = StdioServerParameters(command=sys.executable, args=["mcp_server.py"])
    async with stdio_client(params, errlog=sys.stderr) as (read, write):
        async with ClientSession(read, write) as session:
            await asyncio.wait_for(session.initialize(), timeout=30)  # fail loud, don't hang
            tools = await load_mcp_tools(session)                     # MCP -> LangChain tools
            agent = create_react_agent(ChatOpenAI(model="gpt-4o-mini", temperature=0), tools)
            result = await asyncio.wait_for(
                agent.ainvoke({"messages": [("user", goal)]}), timeout=120)
            return result["messages"][-1].content

def have(mod):
    import importlib.util
    return importlib.util.find_spec(mod) is not None

def run_async(coro):
    """Run a coroutine from anywhere, including a Jupyter notebook.

    A plain script has no event loop, so asyncio.run() just works. But a Jupyter
    cell ALREADY runs inside an event loop, and asyncio.run() refuses to start a
    nested one ("cannot be called from a running event loop").

    The fix is NOT nest_asyncio: on Windows, spawning a subprocess (our stdio MCP
    server) needs a ProactorEventLoop, and nest_asyncio's re-entrant loop can't
    reliably drive Proactor's subprocess pipes -> initialize() hangs forever.
    Instead we run the coroutine in a SEPARATE THREAD with its own fresh loop.
    That thread has no running loop (so run_until_complete is legal) and gets a
    real ProactorEventLoop that can spawn the server.
    """
    import asyncio, threading
    try:
        asyncio.get_running_loop()          # raises if no loop -> we're a script
        in_loop = True
    except RuntimeError:
        in_loop = False
    if not in_loop:
        return asyncio.run(coro)

    box = {}
    def worker():
        loop = asyncio.new_event_loop()     # ProactorEventLoop on Windows
        asyncio.set_event_loop(loop)
        try:
            box["value"] = loop.run_until_complete(coro)
        except BaseException as exc:        # re-raise on the calling thread
            box["error"] = exc
        finally:
            loop.close()
    t = threading.Thread(target=worker)
    t.start()
    t.join()
    if "error" in box:
        raise box["error"]
    return box["value"]

if os.getenv("OPENAI_API_KEY") and have("mcp") and have("langgraph") and have("langchain_openai"):
    goal = ("Assess host 10.0.0.5: scan it, look up CVEs for the services you find, "
            "and give me a short risk report.")
    print(run_async(run_live_agent(goal)))
else:
    print("Live agent skipped (needs OPENAI_API_KEY + mcp + langgraph + langchain-openai).")
    print("Set the key and `python mcp_server.py` is launched automatically over stdio.")
    print("\nThe agent would: port_scan(10.0.0.5) -> lookup_cve(each service) -> grounded report,")
    print("choosing each tool call itself instead of following a fixed script.")'''
)

# ---- Final comparison + summary --------------------------------------------
slide("\U0001F525 The Whole Course in One Table", [
    "Stage 1 Chains: orchestration ✅, data = LLM memory, fixed",
    "Stage 2 RAG: + real CVE data, grounded, still fixed",
    "Stage 3 Agent+MCP: dynamic decisions, standardized tools",
    "Accuracy: medium → high → high",
    "Automation: low → medium → high",
])
script(
    "Let's step back and see the arc whole. Stage 1 gave us orchestration with chains, but the "
    "facts came from the model's memory and the pipeline was fixed. Stage 2 kept the structure but "
    "grounded the facts in real CVE documents through RAG, trading guesses for citations. Stage 3 "
    "broke the fixed pipeline open: an agent decides the steps at runtime, and MCP gives it a "
    "standardized, swappable toolbox so the system can grow. Read across the table and you can "
    "narrate the entire course in one breath. The one-line story to leave students with: we start "
    "by using LLMs to *interpret* security data, then make them *accurate* with real knowledge, "
    "and finally make them *autonomous* with agents and standardized tools."
)
code(
    r'''rows = [
    ("Orchestration",   "Chains",      "Chains",          "Agents"),
    ("Data source",     "LLM memory",  "RAG (real CVEs)", "RAG + MCP tools"),
    ("Accuracy",        "medium",      "high",            "high"),
    ("Automation",      "low",         "medium",          "high"),
    ("Flexibility",     "fixed",       "fixed",           "dynamic"),
    ("Tool integration","manual",      "manual+retrieval","autonomous (agent+MCP)"),
]
print(f"  {'CAPABILITY':18s}{'LECTURE 1':16s}{'LECTURE 2':18s}{'LECTURE 3'}")
print("  " + "-" * 70)
for r in rows:
    print(f"  {r[0]:18s}{r[1]:16s}{r[2]:18s}{r[3]}")
print("\n  Story: interpret (chains) -> accurate (RAG) -> autonomous (agents + MCP).")'''
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

with open("cybersecurity_automation.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Wrote cybersecurity_automation.ipynb with {len(cells)} cells.")
