# LangChain: Building Applications on Top of LLMs

A ~40-minute graduate lecture module for the *AI for Cybersecurity* course. It teaches the core
LangChain building blocks — prompts, models, output parsers, and runnables — and how to compose
them into chains, then rebuilds a RAG system the LangChain way. It is the natural follow-on to the
[RAG](../RAG/) module.

The module is two Jupyter notebooks:

- **[langchain.ipynb](langchain.ipynb)** — the *concepts* lecture (~30 min, 7 focused topics):
  what LangChain is, the **Runnable** interface (`invoke`/`batch`/`stream`), the three core
  building blocks (**prompt templates, chat models, output parsers**), composing them with LCEL
  (the `|` pipe), and a **chain vs. raw API** comparison explaining why a chain helps.
- **[langchain_example.ipynb](langchain_example.ipynb)** — a *worked example*: a six-step RAG
  system built with LangChain components, ending with a live step that swaps in a real model.

Each topic is presented as three cells: a **slide** (bullets to project), an **instructor
script** (narration to read aloud), and a **runnable code** cell with clean output.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) API key for the live step

`langchain.ipynb` and Steps 1–6 of `langchain_example.ipynb` run **fully offline** — no key needed.
They use a small deterministic *stand-in* chat model so every chain executes without a network
call. Only **Step 7** of `langchain_example.ipynb` calls the OpenAI API. To run it, set
`OPENAI_API_KEY` (e.g. in a `.env` file in the project root):

```
OPENAI_API_KEY=sk-your-openai-key-here
```

If no key is set, Step 7 prints a notice and skips, so the rest of the notebook still runs.

### 3. Open a notebook

Open either `.ipynb` in Jupyter, VS Code, or Google Colab and run the cells top to bottom. The
example notebook downloads a small (~90 MB) embedding model on first run and caches it.

## Files

- `langchain.ipynb` — concepts lecture (runs offline; ships with outputs).
- `langchain_example.ipynb` — worked LangChain RAG example (Steps 1–6 offline; Step 7 needs a key).
- `cybersecurity_kb.md` — the knowledge base the example retrieves from (one topic per `#` header).
- `_build_langchain_notebook.py` — generator script that writes `langchain.ipynb`.
- `_build_langchain_example.py` — generator script that writes `langchain_example.ipynb`.
- `requirements.txt` — Python dependencies.

## Editing the notebooks

The notebooks are **generated from the `_build_*.py` scripts**, not edited by hand. To change a
lecture, edit the build script and regenerate:

```bash
python _build_langchain_notebook.py     # -> langchain.ipynb
python _build_langchain_example.py       # -> langchain_example.ipynb
```

To re-embed fresh outputs in the concepts notebook after regenerating:

```bash
jupyter nbconvert --to notebook --execute --inplace langchain.ipynb
```

## How It Works

`langchain.ipynb` introduces the framework one component at a time — the Runnable interface, then
prompt templates, chat models, and output parsers — and shows how they compose into the workhorse
pattern `prompt | model | parser`, ending with why a chain beats hand-written glue code. Every
example is offline and cybersecurity-flavored (alert triage). `langchain_example.ipynb` then
assembles a full RAG pipeline over `cybersecurity_kb.md`:

1. **Load & chunk** the KB into LangChain `Document` objects.
2. **Connect** a vector store (`InMemoryVectorStore`) with an embeddings wrapper.
3. **Ingest** — `add_documents` embeds and indexes every chunk.
4. **Retrieve** context with `get_context` (relevance threshold) and a `retriever`.
5. **Build** the RAG chain `get_rag_chain`: `{context, query} | prompt | model | parser`.
6. **Ask** questions; answers are tagged `[RAG]` (from the docs) or `[LLM]` (model's own knowledge).
7. **Go live** — swap the offline stand-in for `ChatOpenAI` with no other code change.

This example is adapted (in English, with a larger dataset) from a Chinese-language LangChain +
**Milvus** + **Qwen** tutorial; it keeps the original's `get_context()` and `get_rag_chain()`
function names and shows the Milvus + hosted-LLM **production equivalent** in comments.
