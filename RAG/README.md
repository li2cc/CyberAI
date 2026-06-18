# Embeddings & Retrieval-Augmented Generation (RAG)

A ~40-minute graduate lecture module for the *AI for Cybersecurity* course. It teaches how
embeddings turn text into meaning-bearing vectors and how to assemble those vectors into a
complete RAG pipeline that answers questions from your own documents.

The module is two Jupyter notebooks:

- **[embedding.ipynb](embedding.ipynb)** — the *concepts* lecture: what embeddings are, how they
  differ from hashing and bag-of-words, similarity metrics, chunking, vector indexes, retrieval,
  re-ranking, and the full RAG pipeline.
- **[rag_example.ipynb](rag_example.ipynb)** — a *worked example*: a six-step RAG system over a
  cybersecurity knowledge base, ending with a live step that compares RAG vs. a pure LLM.

Each topic is presented as three cells: a **slide** (bullets to project), an **instructor
script** (narration to read aloud), and a **runnable code** cell with clean output.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) API key for the live step

`embedding.ipynb` and Steps 1–6 of `rag_example.ipynb` run **fully offline** with open-source
models (`sentence-transformers`, `faiss`) — no key needed. Only **Step 7** of `rag_example.ipynb`
calls the OpenAI API. To run it, set `OPENAI_API_KEY` (e.g. in a `.env` file in the project root):

```
OPENAI_API_KEY=sk-your-openai-key-here
```

### 3. Open a notebook

Open either `.ipynb` in Jupyter, VS Code, or Google Colab and run the cells top to bottom. The
first run downloads a small (~90 MB) embedding model and caches it.

## Files

- `embedding.ipynb` — concepts lecture (runs offline; ships with outputs).
- `rag_example.ipynb` — worked RAG example (Steps 1–6 offline; Step 7 needs an API key).
- `cybersecurity_kb.md` — the knowledge base the example retrieves from (one topic per `#` header).
- `_build_notebook.py` — generator script that writes `embedding.ipynb`.
- `_build_rag_example.py` — generator script that writes `rag_example.ipynb`.
- `requirements.txt` — Python dependencies.

## Editing the notebooks

The notebooks are **generated from the `_build_*.py` scripts**, not edited by hand. To change a
lecture, edit the build script and regenerate:

```bash
python _build_notebook.py        # -> embedding.ipynb
python _build_rag_example.py     # -> rag_example.ipynb
```

To re-embed fresh outputs in the concepts notebook after regenerating:

```bash
jupyter nbconvert --to notebook --execute --inplace embedding.ipynb
```

## How It Works

`embedding.ipynb` builds intuition from the ground up — text → vectors → similarity → chunking →
retrieval → re-ranking — and ends by assembling the full pipeline. `rag_example.ipynb` then puts
it to work over `cybersecurity_kb.md`:

1. **Load & chunk** the Markdown KB into passages.
2. **Connect** an in-memory vector store (FAISS).
3. **Ingest** — embed and index every chunk.
4. **Retrieve** the top chunks for a query, with a relevance threshold.
5. **Build** a prompt that injects the retrieved context.
6. **Ask** questions; answers are tagged `[RAG]` (from the docs) or `[LLM]` (model's own knowledge).
7. **Compare** RAG against a pure OpenAI LLM and let an LLM judge score the answers.

Each offline step also shows its **production equivalent** (a managed vector DB like Milvus, a
hosted LLM) in comments, so the same code scales beyond the classroom.

## Project — Cybersecurity Framework RAG

The course project tied to this module. Students build a **RAG assistant over real cybersecurity
framework documents** and evaluate whether its answers are actually grounded in the retrieved
evidence.

- **Choose a framework corpus:** MITRE ATT&CK, MITRE ATLAS, NIST AI RMF / NIST CSF, or the OWASP
  Top 10 (Web and/or LLM). Ingest the official documents.
- **Build the pipeline:** load → chunk → embed → index → retrieve (with a relevance threshold) →
  prompt → answer, reusing the patterns from `rag_example.ipynb`.
- **Ground and cite:** answers must quote or reference the retrieved sections, not the model's
  memory. Tag responses `[RAG]` vs. `[LLM]` and surface the supporting passages.
- **Evaluate retrieval quality:** test queries with strong evidence and queries with *no* good
  evidence; show how the system behaves (correct grounding vs. graceful "not found" vs.
  hallucination) and discuss the failure modes.
- **Deliverables:** a reproducible notebook, a short report on retrieval quality and limitations,
  and a brief AI-use statement.

> **Scope:** use only approved, public framework documents. Frame the assistant as a defensive
> analysis aid, and keep any API keys in the repository-root `.env`.

