"""Generator for langchain.ipynb — a graduate-level LangChain teaching notebook.

Companion to RAG/embedding.ipynb. Same three-cell rhythm per topic:
  1. A slide-style markdown cell (bullet points).
  2. An "Instructor Script" markdown cell (~80-150 words of narration).
  3. A runnable code cell with clean, printed output.

Design choice: every example runs LOCALLY and OFFLINE on LangChain core using a
small deterministic stand-in chat model (a RunnableLambda) — no API key needed,
so the lecture is fully reproducible in class. Each topic shows the one-line
swap to a real model (ChatOpenAI / ChatAnthropic) in a comment.

Scope: the core building blocks (Runnable, prompt, model, parser) and how to
compose them into a chain — seven focused topics sized for a 30-minute class.

Run:  python _build_langchain_notebook.py   ->  writes langchain.ipynb
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
    "# LangChain: Building Applications on Top of LLMs\n"
    "### A Graduate-Level, Hands-On Teaching Notebook\n\n"
    "**Audience:** Graduate students in CS / Data Science / Cybersecurity AI who have seen "
    "the `embedding.ipynb` and `rag_example.ipynb` notebooks.\n\n"
    "**Format:** Each topic has three parts —\n"
    "1. \U0001F4CA a *slide* (bullet points) you can project,\n"
    "2. \U0001F3A4 an *instructor script* to read and explain, and\n"
    "3. \U0001F4BB a *runnable code example* with clean output.\n\n"
    "**Design choice:** Every example runs **locally and offline** on `langchain-core` using a "
    "small deterministic **stand-in chat model** — no API key is required, so the whole lecture "
    "is reproducible in class. Each topic also shows the *one-line swap* to a real model "
    "(`ChatOpenAI`, `ChatAnthropic`) in a comment.\n\n"
    "---\n\n"
    "## Learning Objectives (this 30-minute lecture)\n"
    "By the end of this notebook, students will be able to:\n"
    "- Explain what LangChain is and the problem it solves over raw API calls.\n"
    "- Describe the **Runnable** interface (`invoke` / `batch` / `stream`) shared by every component.\n"
    "- Use the three core building blocks: **prompt templates, chat models, and output parsers**.\n"
    "- Compose them into a **chain** with the LCEL pipe operator (`|`).\n"
    "- Explain *why* a chain helps — what it gives you over hand-written glue code.\n\n"
    "> Retrieval, memory, tools/agents, and tracing build directly on these seven ideas; once the "
    "core clicks, those are just more stages added to the same pipe."
)

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------
md("## \U0001F6E0️ Setup — Install & Import\n\n"
   "Run this once. LangChain core is pure Python — there are **no model downloads** and "
   "**no API key** needed for this notebook.")

code(
    "# If running locally / Colab, uncomment to install:\n"
    "# !pip install -q langchain langchain-core\n\n"
    "import langchain_core\n"
    "from langchain_core.messages import AIMessage, HumanMessage, SystemMessage\n\n"
    "print('LangChain core version:', langchain_core.__version__)"
)

md("### A reusable offline stand-in for a chat model\n\n"
   "A real chat model is just a *Runnable*: give it a prompt, get back an `AIMessage`. "
   "We define a tiny deterministic stand-in so every chain in this notebook runs without a "
   "network call. It does crude keyword routing over the assembled prompt and returns a "
   "short, SOC-analyst-style verdict — enough to see the **mechanics** of LangChain clearly. "
   "In production you replace this one object with a real model and **nothing else changes**.")

code(
    r'''from langchain_core.runnables import RunnableLambda


def _mock_chat(prompt_value):
    """Deterministic stand-in for a real chat model (no API key needed).

    Reads the fully assembled prompt and returns a short, rule-based
    cybersecurity 'analysis' so chains produce sensible, input-dependent
    output offline. A real model would reason far better -- but it plugs in
    exactly the same way (see the swap comment below).
    """
    text = prompt_value.to_string() if hasattr(prompt_value, "to_string") else str(prompt_value)
    low = text.lower()
    if "ransomware" in low or "encrypted" in low:
        verdict = "[CRITICAL] Malware / ransomware. Isolate the host and engage incident response."
    elif "phish" in low or "credential" in low and "email" in low:
        verdict = "[HIGH] Phishing / social engineering. Reset credentials and hunt for similar emails."
    elif "failed login" in low or "brute" in low or "authentication" in low:
        verdict = "[HIGH] Brute-force / credential access. Lock the account and enable MFA."
    elif "port scan" in low or "scan" in low or "reconnaissance" in low:
        verdict = "[MEDIUM] Reconnaissance. Monitor the source and check firewall rules."
    elif "backup" in low or "patch" in low or "update" in low:
        verdict = "[INFO] Routine maintenance activity. No action required."
    else:
        verdict = "[LOW] Unclassified event. Route to an analyst for review."
    return AIMessage(content=verdict)


# Our offline 'model'. Anywhere you see `mock_llm`, a real model would slot in:
#   from langchain_openai import ChatOpenAI
#   mock_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# or
#   from langchain_anthropic import ChatAnthropic
#   mock_llm = ChatAnthropic(model="claude-haiku-4-5-20251001")
mock_llm = RunnableLambda(_mock_chat)

print("Offline stand-in chat model ready:", type(mock_llm).__name__)
print("Quick test ->", mock_llm.invoke("100 failed login attempts then a success").content)'''
)

# ---------------------------------------------------------------------------
# 1. What is LangChain
# ---------------------------------------------------------------------------
slide("\U0001F517 1 — What is LangChain?", [
    "An open-source **framework** for building apps on top of LLMs",
    "Provides standard, swappable **components**",
    "Glues them into **pipelines** ('chains')",
    "Same code works across model providers",
    "Today we focus on the **core four**: prompt, model, parser, runnable",
])
script(
    "LangChain is a framework for building applications powered by large language models. A raw "
    "LLM only does one thing: text in, text out. Real applications need much more — formatted "
    "prompts, output you can parse, and a clean way to wire steps together. LangChain supplies "
    "each of these as a standard, interchangeable component. The payoff is that your code is built "
    "from reusable parts and is portable: swapping OpenAI for Anthropic is usually a one-line "
    "change because every component implements the same interface. LangChain also ships retrieval, "
    "memory, tools, and tracing — we list them below so you know they exist — but today we focus "
    "on the **core four** building blocks and how to compose them, which is the foundation "
    "everything else is built on."
)
code(
    r'''components = [
    ("Prompt templates", "turn variables into a well-formed prompt",   "TODAY"),
    ("Models",           "LLMs and chat models (the reasoning engine)", "TODAY"),
    ("Output parsers",   "turn model text into strings / JSON / objects","TODAY"),
    ("Runnables + LCEL", "compose components with the `|` pipe operator","TODAY"),
    ("Retrievers",       "fetch relevant documents for RAG",            "later"),
    ("Memory",           "carry conversation history across turns",     "later"),
    ("Tools + agents",   "let the model call functions / APIs",         "later"),
    ("Callbacks",        "trace, log, and debug every step",            "later"),
]
print("LangChain building blocks")
print("-" * 64)
for name, role, when in components:
    mark = "->" if when == "TODAY" else "  "
    print(f" {mark} {name:18s} {role:42s} [{when}]")'''
)

# ---------------------------------------------------------------------------
# 2. The Runnable interface
# ---------------------------------------------------------------------------
slide("\U0001F9E9 2 — The Runnable: One Interface for Every Component", [
    "Every component is a **Runnable**",
    "`.invoke(x)` — run on one input",
    "`.batch([...])` — run on many inputs",
    "`.stream(x)` — yield output incrementally",
    "Because they share this interface, they **snap together**",
])
script(
    "The single most important idea in modern LangChain is the **Runnable**. Prompts, models, "
    "parsers — every piece implements the same small interface, so they all behave alike and snap "
    "together. The core method is `invoke`, which runs the component on one input. For free you "
    "also get `batch` to process many inputs efficiently and `stream` to receive output as it is "
    "produced. The key consequence: because everything shares this contract, a chain you build "
    "from several Runnables is *itself* a Runnable with the same methods. Hold onto that idea — it "
    "is exactly why, in a few minutes, we can compose components with a single pipe character and "
    "the result behaves just like any other component."
)
code(
    r'''from langchain_core.runnables import RunnableLambda

# Any Python function becomes a Runnable. Here: normalize a raw log line.
normalize = RunnableLambda(lambda s: s.strip().lower())

print("invoke ->", normalize.invoke("  FAILED LOGIN from 10.0.0.5  "))
print("batch  ->", normalize.batch(["  ALERT A  ", "Alert B"]))
print("stream ->", list(normalize.stream("  Streamed Event  ")))
print("\nEvery LangChain component supports this same .invoke / .batch / .stream interface.")'''
)

# ---------------------------------------------------------------------------
# 3. Models: LLMs vs Chat Models
# ---------------------------------------------------------------------------
slide("\U0001F916 3 — Models: LLMs vs Chat Models", [
    "**Chat models** are the modern default: messages in, message out",
    "Messages have roles: `system`, `human`, `ai`",
    "Older **text LLMs**: plain string in, string out",
    "Output is an `AIMessage` (text + metadata), **not** a bare string",
    "Providers differ; the **interface** is the same",
])
script(
    "LangChain wraps two kinds of models. Text LLMs take a string and return a string — the "
    "classic completion API. Chat models, which dominate today, take a list of role-tagged "
    "*messages* (system, human, assistant) and return an `AIMessage`. The system message sets "
    "behavior, human messages carry user input, and the model replies as the assistant. Crucially, "
    "every provider's model exposes the same Runnable interface, so your application code does not "
    "care whether it is talking to OpenAI, Anthropic, or a local model. Below we call our offline "
    "stand-in with explicit messages. Notice it returns an `AIMessage` *object*, not a plain "
    "string — remember that, because it is exactly why we will add an output parser in Topic 5."
)
code(
    r'''messages = [
    SystemMessage(content="You are a Tier-1 SOC analyst. Classify the alert."),
    HumanMessage(content="200 failed SSH logins from a foreign IP, then one success."),
]

response = mock_llm.invoke(messages)
print("Type returned :", type(response).__name__)
print("response.content:", response.content)

# --- Real model (one-line swap; needs a key) ---
# from langchain_openai import ChatOpenAI
# real_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
# response = real_llm.invoke(messages)'''
)

# ---------------------------------------------------------------------------
# 4. Prompt templates
# ---------------------------------------------------------------------------
slide("\U0001F4DD 4 — Prompt Templates", [
    "Don't hand-build prompt strings — use a **template**",
    "`PromptTemplate`: a single text string with `{variables}`",
    "`ChatPromptTemplate`: a list of role-tagged messages",
    "Fill the variables at call time; reuse the structure",
    "Keeps prompts consistent, testable, and versionable",
])
script(
    "Hard-coding prompt strings with f-strings scattered through your code gets unmaintainable "
    "fast. A prompt template separates the fixed structure from the variable parts. "
    "`PromptTemplate` handles a single string with named placeholders; `ChatPromptTemplate` builds "
    "the list of role-tagged messages that chat models expect. You define the template once — with "
    "the system instructions and a slot for user input — and fill it with different values on every "
    "call. This keeps prompts consistent, testable, and easy to version. Calling the template "
    "produces a *PromptValue*, which can render either as a message list or as a plain string, so "
    "it feeds cleanly into either kind of model. This is the first stage of the chain we build next."
)
code(
    r'''from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}. Classify the security alert and recommend an action."),
    ("user", "Alert: {alert}"),
])

filled = prompt.invoke({"role": "SOC analyst", "alert": "Ransomware note found; files encrypted."})
print("Filled prompt as messages:")
for m in filled.to_messages():
    print(f"  [{m.type:6s}] {m.content}")

print("\nSame prompt, rendered as a single string:")
print(filled.to_string())'''
)

# ---------------------------------------------------------------------------
# 5. Output parsers
# ---------------------------------------------------------------------------
slide("\U0001F9FE 5 — Output Parsers", [
    "Models return messages/text — apps need **clean data**",
    "`StrOutputParser`: pull the plain string out of an `AIMessage`",
    "`JsonOutputParser`: parse a JSON reply into a dict",
    "Parsers are Runnables too → they go on the **end of a chain**",
    "They make LLM output *programmable*",
])
script(
    "A chat model hands you an `AIMessage`, but your program usually wants a plain string or a "
    "structured object. Output parsers do that final conversion, and because they are Runnables "
    "they slot onto the end of a chain. The simplest, `StrOutputParser`, extracts the `.content` "
    "string so downstream code gets text, not an object. When you ask a model to reply in JSON, "
    "`JsonOutputParser` turns that reply into a Python dictionary your code can index into. So the "
    "three core pieces are now in hand: a prompt produces the input, a model produces an "
    "`AIMessage`, and a parser turns that message into the type the rest of your application "
    "expects. In the next topic we connect all three into a single chain."
)
code(
    r'''from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

ai_msg = AIMessage(content='{"severity": "high", "category": "brute-force", "action": "lock account"}')

# StrOutputParser: AIMessage -> str
print("StrOutputParser  ->", repr(StrOutputParser().invoke(ai_msg)))

# JsonOutputParser: a JSON reply -> dict your code can use
parsed = JsonOutputParser().invoke(ai_msg)
print("JsonOutputParser ->", parsed)
print("Programmatic access -> severity =", parsed["severity"], "| action =", parsed["action"])'''
)

# ---------------------------------------------------------------------------
# 6. LCEL — your first chain
# ---------------------------------------------------------------------------
slide("\U0001F517 6 — LCEL: Your First Chain (the `|` pipe)", [
    "LCEL = **LangChain Expression Language**",
    "Compose Runnables with the pipe: `a | b | c`",
    "Output of each step feeds the next (like Unix pipes)",
    "The classic chain: `prompt | model | parser`",
    "The result is itself a Runnable you call with `.invoke`",
])
script(
    "Now we connect the three pieces. LangChain Expression Language, or LCEL, lets you compose "
    "Runnables with the pipe operator, exactly like Unix pipes: the output of one stage flows into "
    "the next. The canonical chain is `prompt | model | parser` — fill the template, send it to the "
    "model, parse the reply into a clean string. Read the pipe left to right as a data-flow "
    "pipeline. You build it once and then call `invoke` on it like any other Runnable, passing just "
    "the template variables; the chain feeds them through all three stages for you. This "
    "three-stage chain is the workhorse pattern you will reuse constantly — every more advanced "
    "feature in LangChain is just additional stages added to this same idea."
)
code(
    r'''from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a SOC analyst. Classify the alert and recommend an action."),
    ("user", "{alert}"),
])

# Compose three Runnables into one chain:
chain = prompt | mock_llm | StrOutputParser()

print(chain.invoke({"alert": "Files renamed with .locked extension; ransom note dropped."}))
print(chain.invoke({"alert": "Nightly database backup completed successfully."}))
print("\nThe chain is itself a Runnable:", type(chain).__name__)'''
)

# ---------------------------------------------------------------------------
# 7. Chain vs raw API calls (the comparison)
# ---------------------------------------------------------------------------
slide("⚖️ 7 — Why a Chain? Chain vs. Raw API Calls", [
    "Without a framework you wire each step **by hand**",
    "Format prompt → call model → parse output → repeat everywhere",
    "A chain encapsulates that glue into **one reusable object**",
    "Free: `batch`, `stream`, `async`, retries, callbacks",
    "Swap any component (prompt / model / parser) without touching the rest",
])
script(
    "Why bother with a chain instead of just calling the API yourself? Let's compare directly. "
    "Doing it by hand, you format the prompt, call the model, then pull the text out of the "
    "response — three manual steps you repeat at every call site, each with its own error "
    "handling. The chain packages that exact glue into a single reusable object. And the real win "
    "is what comes for free: the chain inherits `batch`, `stream`, and async from the Runnable "
    "interface, plus built-in retries and callback hooks, and you can swap the prompt, model, or "
    "parser independently. So the framework is not magic — it is disciplined plumbing that removes "
    "boilerplate and makes your pipeline portable and observable. Below, both approaches produce "
    "the identical answer; the chain just gets you there with far less to maintain."
)
code(
    r'''alert = "Repeated failed authentication, then a successful login from a new country."

# --- Approach A: raw, do-it-yourself orchestration ---
filled = prompt.invoke({"alert": alert})   # 1. format
raw = mock_llm.invoke(filled)              # 2. call model  (-> AIMessage)
manual_answer = raw.content.strip()        # 3. parse output yourself

# --- Approach B: the LCEL chain does all three ---
chain_answer = (prompt | mock_llm | StrOutputParser()).invoke({"alert": alert})

print("Manual :", manual_answer)
print("Chain  :", chain_answer)
print("Same result:", manual_answer == chain_answer)
print("\nThe chain also gives you batch/stream/async/retries/callbacks with no extra code.")'''
)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
slide("✅ Summary & Key Takeaways", [
    "LangChain = swappable **components** + a way to **compose** them",
    "Everything is a **Runnable**: `invoke` / `batch` / `stream`",
    "Three core pieces: **prompt → model → parser**",
    "Compose with LCEL: `chain = prompt | model | parser`",
    "A chain beats hand-written glue: reusable, portable, free batch/stream",
])
script(
    "To wrap up these 30 minutes: LangChain gives you standard, interchangeable components and the "
    "LCEL pipe to compose them. The foundation is the Runnable interface — `invoke`, `batch`, "
    "`stream` — shared by everything. The three core building blocks are the prompt template, "
    "which formats the input; the model, which does the reasoning and returns an `AIMessage`; and "
    "the output parser, which converts that message into the type your code needs. Compose them "
    "and you get the workhorse chain `prompt | model | parser`, which is itself a Runnable. The "
    "mental model to keep is data flowing left to right through composable, swappable stages. "
    "Everything beyond today — retrieval for RAG, conversation memory, tools and agents, and "
    "tracing — is just more stages added to this same pipe, and we put it to work next in "
    "`langchain_example.ipynb`."
)
code(
    r'''print("LangChain in one line:")
print("  chain = prompt | model | parser     (everything is a Runnable)")
print("\nNext: langchain_example.ipynb — a complete RAG system over a cybersecurity KB.")'''
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

with open("langchain.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Wrote langchain.ipynb with {len(cells)} cells.")
