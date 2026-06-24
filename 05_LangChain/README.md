# Module 5 — LangChain

A two-week graduate module for **Applied AI for Cybersecurity (IT7075C)**. It teaches the core
**LangChain** building blocks — prompts, chat models, output parsers, and runnables — and how to
compose them with LCEL (the `|` pipe), then rebuilds a **RAG** system the LangChain way over a
**synthetic cybersecurity AI-framework dataset**. Built from **Omar Santos's** materials (book
*Agentic AI for Cybersecurity*; the *RAG, AI Apps, and AI Agents* LinkedIn course; and the
[AI-agents-for-cybersecurity](https://github.com/santosomar/AI-agents-for-cybersecurity) repo).

It follows [Module 4 — RAG](../04_RAG/) and leads into [Module 6 — LangGraph](../06_LangGraph/).

## Notebooks

- **[langchain_basics.ipynb](langchain_basics.ipynb)** — *Part 1: the building blocks.* The
  **Runnable** interface (`invoke`/`batch`/`stream`), prompt templates, chat models, and output
  parsers, composed into the workhorse pattern `prompt | model | parser`, plus `RunnableBranch`,
  `RunnableParallel`, and `RunnablePassthrough` — all cybersecurity-flavored (alert triage).
- **[langchain_rag.ipynb](langchain_rag.ipynb)** — *Part 2: RAG with LangChain.* A full retrieval
  pipeline (load → chunk → embed → store → retrieve → answer) over `ai_framework_kb.md`, the
  synthetic AI-framework knowledge base, ending with a live step that swaps in a real model.
- **[langchain_sample.ipynb](langchain_sample.ipynb)** — a minimal copy-paste chain template.

Each concept is presented as three cells: a **slide** (bullets to project), an **instructor
script** (narration to read aloud), and a **runnable code** cell.

## The dataset — `ai_framework_kb.md`

A synthetic knowledge base summarizing the cybersecurity-AI frameworks from the course outcomes:
**NIST AI RMF**, **MITRE ATLAS**, the **OWASP Top 10 for LLM Applications**, Google's **SAIF**,
the **Coalition for Secure AI (CoSAI)**, the **EU AI Act**, and **MAESTRO**. It is the corpus for
Mini-Project 3 (a RAG app over this dataset).

## Setup

```bash
pip install -r requirements.txt
```

Part 1 and the offline steps of Part 2 run **with no API key** — real LangChain code is guarded on
`HAS_KEY = bool(os.getenv("OPENAI_API_KEY"))`, with a deterministic stand-in otherwise. To run the
live steps, set `OPENAI_API_KEY` (e.g. a `.env` in the project root); without it, those steps print
a notice and skip. Open any notebook in Jupyter, VS Code, or Colab and run top to bottom.

## Two-week plan

| | Deliverable |
|---|---|
| **Lecture** | `Module5_LangChain.pptx` (slides) + Part 1 & Part 2 notebooks |
| **Week 1** | `Module5_Week1_Concepts` — short concept check |
| **Week 2** | **Mini-Project 3** — a RAG app over the synthetic AI-framework dataset |

*(Slides and assignments are generated under `assignments and projects/` and are not pushed to GitHub.)*

## Files

- `langchain_basics.ipynb`, `langchain_rag.ipynb`, `langchain_sample.ipynb` — the notebooks.
- `ai_framework_kb.md` — the synthetic AI-framework knowledge base the RAG notebook retrieves from.
- `_build_langchain_basics.py`, `_build_langchain_rag.py`, `_build_langchain_sample.py` — generators.
- `requirements.txt` — Python dependencies.

## Editing the notebooks

The notebooks are **generated from the `_build_*.py` scripts**, not edited by hand. To change a
lecture, edit the build script and regenerate, e.g.:

```bash
python _build_langchain_basics.py     # -> langchain_basics.ipynb
```
