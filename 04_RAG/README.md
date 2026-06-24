# Embeddings, Vector Databases & RAG

A graduate lecture module for the *Applied AI for Cybersecurity* course (Module 4). It teaches how
embeddings turn text into meaning-bearing vectors, how a **vector database** stores and searches
them, and how to assemble a complete **RAG** pipeline that answers questions from your own
documents — all **framework-free** (plain Python, `sentence-transformers`, `chromadb`). **No
LangChain and no TF-IDF**; LangChain is the next module.

The module follows the ordering of **Omar Santos's** LinkedIn Learning course and book, and is two
Jupyter notebooks:

- **[embeddings_and_vector_db.ipynb](embeddings_and_vector_db.ipynb)** — *part 1, the engine*: what
  RAG is, embeddings & embedding models (local vs. OpenAI, **MTEB**), a real 1,000-CVE dataset,
  similarity / nearest neighbors, **chunking**, installing and operating a **vector database
  (ChromaDB)** — create, add, query, filter — indexing (why vector DBs scale), and visualization
  (PCA / TensorFlow Embedding Projector).
- **[rag_example.ipynb](rag_example.ipynb)** — *part 2, the pipeline*: a basic RAG system over
  security docs — load → chunk → embed → **ChromaDB** → retrieve (with a distance threshold) →
  augment → generate a grounded, tagged answer, with an honest fallback on out-of-domain questions.

Each topic is presented as three cells: a **slide** (bullets to project), an **instructor script**
(narration to read aloud), and a **runnable code** cell with clean, **output-rich** results.

> **Credit & sources.** This module is built from **Omar Santos** — LinkedIn Learning course *RAG,
> AI Apps, and AI Agents for Cybersecurity and Networking*; book *Agentic AI for Cybersecurity*
> (Chapter 2); and his repo
> [github.com/santosomar/AI-agents-for-cybersecurity](https://github.com/santosomar/AI-agents-for-cybersecurity).
> The CVE dataset, `ssrf.txt`, and `llm_cheatsheet.md` come from that repo. His `basic_rag` examples
> use LangChain + Chroma; here we use **`chromadb` directly** so every step is visible and
> framework-free.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) API key

Both notebooks run **fully offline** — `sentence-transformers` (embeddings) and `chromadb` (vector
store) are local. Only the optional generation/embedding cells call OpenAI. To enable them, set
`OPENAI_API_KEY` (e.g. in a `.env` file in the project root):

```
OPENAI_API_KEY=sk-your-openai-key-here
```

### 3. Open a notebook

Open either `.ipynb` in Jupyter, VS Code, or Google Colab and run top to bottom (do part 1 first).
The first run downloads a small (~90 MB) embedding model and caches it. If matplotlib is blocked on
your machine, the visualization cell prints a note and points you to the TensorFlow Embedding
Projector — the rest still runs.

## Files

- `embeddings_and_vector_db.ipynb` — part 1: embeddings, CVE data, chunking, ChromaDB, indexing, viz.
- `rag_example.ipynb` — part 2: a framework-free RAG pipeline over security docs (ChromaDB).
- `rag_sample.ipynb` — a minimal copy-paste RAG template.
- `CVE_vectors_1000.tsv`, `CVE_metadata_1000.tsv` — the 1,000-CVE embeddings dataset
  (Embedding-Projector format; from Omar Santos's repo, credited above).
- `ssrf.txt`, `llm_cheatsheet.md` — security documents used as the RAG knowledge base (from the repo).
- `cybersecurity_kb.md` — an additional local knowledge base (one topic per `#` header).
- `_build_embeddings_vectordb.py` — generator for `embeddings_and_vector_db.ipynb`.
- `_build_rag_example.py` — generator for `rag_example.ipynb`.
- `_build_rag_sample.py` — generator for `rag_sample.ipynb`.
- `requirements.txt` — Python dependencies.

## Editing the notebooks

The notebooks are **generated from the `_build_*.py` scripts**, not edited by hand. To change a
lecture, edit the build script and regenerate, then re-execute to refresh outputs:

```bash
python _build_embeddings_vectordb.py
python _build_rag_example.py
jupyter nbconvert --to notebook --execute --inplace embeddings_and_vector_db.ipynb
jupyter nbconvert --to notebook --execute --inplace rag_example.ipynb
```

## How It Works

Part 1 builds the **retrieval engine**: text → embeddings → similarity → chunking → a Chroma vector
store you create, fill, and query → indexing and visualization. Part 2 assembles the full **RAG
pipeline** over `ssrf.txt` + `cybersecurity_kb.md`:

1. **Load & chunk** the documents into overlapping passages.
2. **Embed & store** the chunks in a ChromaDB collection (cosine space, with source metadata).
3. **Retrieve** the top-k closest chunks for a query, with a distance threshold.
4. **Augment** a prompt with the retrieved context (answers tagged `[RAG]` vs. `[LLM]`).
5. **Generate** a grounded answer (OpenAI if a key is set; otherwise the assembled prompt is shown,
   or point it at your Module 3 local model).
6. **Complete RAG** — an `ask()` loop showing grounded answers in-domain and an honest fallback
   out-of-domain.

## Mini-Project 2 — Cybersecurity Framework Local RAG

This module's mini-project (Module 4, Week 2), building on the two notebooks. Students build a
**fully local, offline RAG assistant over real cybersecurity framework documents** and evaluate
whether its answers are actually grounded in the retrieved evidence — no cloud API.

- **Choose a framework corpus:** MITRE ATT&CK, MITRE ATLAS, NIST AI RMF / NIST CSF, or the OWASP
  Top 10 (Web and/or LLM). Ingest the official documents.
- **Keep it local:** embed with a local model (e.g. `all-MiniLM-L6-v2`) and a local vector store
  (ChromaDB) so the whole pipeline runs offline.
- **Build the pipeline:** load → chunk → embed → store → retrieve (with a threshold) → prompt →
  answer, reusing the patterns from `rag_example.ipynb`.
- **Ground and cite:** answers must reference the retrieved sections, not the model's memory. Tag
  responses `[RAG]` vs. `[LLM]` and surface the supporting passages.
- **Evaluate retrieval quality:** test queries with strong evidence and queries with *no* good
  evidence; show grounding vs. graceful "not found" vs. hallucination, and discuss the failure modes.
- **Deliverables:** a reproducible notebook, a short report on retrieval quality and limitations,
  and a brief AI-use statement.

> **Scope:** use only approved, public framework documents. Frame the assistant as a defensive
> analysis aid, and keep any API keys in the repository-root `.env`.
