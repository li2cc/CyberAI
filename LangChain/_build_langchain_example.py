"""Generator for langchain_example.ipynb — an end-to-end RAG system built with LangChain.

Adapted (in English, new domain, richer data, US-teachable) from a Chinese
LangChain + Milvus + Qwen example. We keep the original's structure and the
names of its two key functions -- `get_context()` and `get_rag_chain()` -- so
students can map our code to the source, but we:
  * translate everything to English and tag answers [RAG] / [LLM]
    (the original used the Chinese tags 【RAG】 / 【大模型】),
  * swap Milvus for an offline `InMemoryVectorStore` (Milvus shown in comments),
  * swap the Qwen LLM for an offline stand-in, with a live ChatOpenAI step,
  * use a larger, realistic cybersecurity knowledge base.

Presentation style matches RAG/rag_example.ipynb: each step = slide +
instructor script + runnable code. Steps 1-6 run OFFLINE with
sentence-transformers; the final live step calls the OpenAI API.

Run:  python _build_langchain_example.py   ->  writes langchain_example.ipynb
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
    "# Building a RAG System with LangChain\n"
    "### Retrieval-Augmented Generation over a Cybersecurity Knowledge Base (LCEL)\n\n"
    "**Audience:** Graduate students who have completed `langchain.ipynb` (LangChain concepts) "
    "and `rag_example.ipynb` (a framework-free RAG pipeline).\n\n"
    "**Goal:** Rebuild the RAG pipeline you already understand, this time using **LangChain "
    "components and the LCEL pipe** — loaders, a vector store, a retriever, a prompt template, "
    "a model, and an output parser, all composed into one chain.\n\n"
    "We follow the same **six-step RAG recipe**, then add a live step:\n"
    "1. \U0001F4C4 Load & chunk the data into `Document`s\n"
    "2. \U0001F5C4️ Connect a vector store + embeddings\n"
    "3. \U0001F4E5 Ingest (embed + index) the chunks\n"
    "4. \U0001F50D Retrieve relevant context (`get_context` + a retriever)\n"
    "5. \U0001F517 Build the RAG chain (`get_rag_chain`: prompt | model | parser)\n"
    "6. \U0001F4AC Ask questions with the chain (offline stand-in model)\n\n"
    "7. \U0001F680 Go live: swap in `ChatOpenAI` and answer for real\n\n"
    "> **Provenance:** This example is adapted from a Chinese-language LangChain + **Milvus** + "
    "**Qwen** tutorial. We translate it to English, tag answers `[RAG]` / `[LLM]` (the original "
    "used 【RAG】 / 【大模型】), and keep its `get_context()` and `get_rag_chain()` functions so the "
    "mapping is clear.\n\n"
    "> **Reproducibility:** Steps 1-6 run **offline** with `sentence-transformers` + LangChain's "
    "`InMemoryVectorStore` and an offline stand-in model — no server, no API key. Each step shows "
    "the **production equivalent** (Milvus + a hosted LLM) in comments. **Step 7 calls the OpenAI "
    "API**, so it needs `OPENAI_API_KEY` set."
)

# ---- The original source ----------------------------------------------------
md(
    "## \U0001F4DC The Original Example (for reference)\n\n"
    "Here is the core of the Chinese tutorial we are adapting. Read it once; we will rebuild "
    "each piece in English below, keeping the same function names.\n\n"
    "```python\n"
    "from langchain_milvus import Milvus\n"
    "from models import get_embed, get_qwen_llm\n"
    "from langchain_core.prompts import ChatPromptTemplate\n"
    "from langchain_core.output_parsers import StrOutputParser\n\n"
    "llm = get_qwen_llm()\n"
    "str_parser = StrOutputParser()\n"
    "embed_fn = get_embed()\n\n"
    "db = Milvus(embedding_function=embed_fn, auto_id=True,\n"
    "            index_params={\"index_type\": \"HNSW\", \"metric_type\": \"L2\"},\n"
    "            connection_args={\"host\": \"localhost\", \"port\": 19530})\n\n"
    "def get_context(query, score_threshold=0.80):\n"
    "    docs = db.similarity_search_with_relevance_scores(query=query, k=6, ...)\n"
    "    # accumulate page_content for docs whose score >= threshold\n"
    "    ...\n\n"
    "prompt = ChatPromptTemplate.from_messages([(\"system\", \"...【RAG】/【大模型】...\"), (\"user\", \"{query}\")])\n\n"
    "def get_rag_chain():\n"
    "    return prompt | llm | str_parser\n"
    "```\n\n"
    "**Our changes:** `Milvus` → `InMemoryVectorStore` (offline), `get_embed` → a "
    "`SentenceTransformer` wrapper, `get_qwen_llm` → an offline stand-in then `ChatOpenAI`, "
    "Chinese prompt/tags → English `[RAG]`/`[LLM]`, and a bigger knowledge base."
)

# ---- Setup ------------------------------------------------------------------
md("## \U0001F6E0️ Setup")
code(
    r'''# If needed, install dependencies:
# !pip install -q langchain langchain-core sentence-transformers
# Optional, only for the live Step 7:
# !pip install -q langchain-openai

from typing import List
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings

print("Imports ready.")'''
)
md("### An embeddings wrapper (`get_embed` in the original)\n\n"
   "LangChain talks to any embedding model through the `Embeddings` interface: two methods, "
   "`embed_documents` (for the corpus) and `embed_query` (for the question). We wrap the same "
   "offline `all-MiniLM-L6-v2` model used in the embeddings notebook. This is the only place the "
   "embedding model is named — exactly as in the original `get_embed()` helper.")
code(
    r'''class SentenceTransformerEmbeddings(Embeddings):
    """Adapt a SentenceTransformer model to LangChain's Embeddings interface.

    Mirrors the original example's get_embed(): one model used for BOTH the
    documents and the query, so they live in the same vector space.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode(text, normalize_embeddings=True).tolist()


embed_fn = SentenceTransformerEmbeddings()   # == get_embed()
DIM = len(embed_fn.embed_query("test"))
print("Embeddings ready -", DIM, "dimensions (all-MiniLM-L6-v2)")'''
)

# ---- Step 1 -----------------------------------------------------------------
slide("\U0001F4C4 Step 1 — Load & Chunk into Documents", [
    "Read the Markdown knowledge base from disk",
    "Split on `#` section headers — one topic per chunk",
    "Wrap each chunk in a LangChain `Document`",
    "`Document` = `page_content` + `metadata`",
    "Metadata (here: the title) travels with the text",
])
script(
    "Every RAG system begins with data. We load a Markdown knowledge base of cybersecurity topics "
    "and split it on `#` headers, so each section becomes one clean, self-contained chunk — the "
    "same header-based semantic chunking we used in `rag_example.ipynb`. The new ingredient is "
    "LangChain's `Document` type: instead of bare strings, we wrap each chunk as a `Document` with "
    "`page_content` and a `metadata` dictionary. Here we store the section title in metadata; in "
    "real systems metadata carries source paths, timestamps, access tags, and more, and it follows "
    "each chunk all the way through retrieval so you can cite or filter by it. LangChain also ships "
    "document loaders and text splitters for PDFs, HTML, and code, but a simple split is clearest "
    "here."
)
code(
    r'''from langchain_core.documents import Document

FILE_NAME = "cybersecurity_kb.md"
with open(FILE_NAME, mode="r", encoding="utf8") as f:
    text = f.read()

sections = [s.strip() for s in text.split("#") if s.strip()]
documents = [
    Document(page_content=s, metadata={"title": s.splitlines()[0], "source": FILE_NAME})
    for s in sections
]

print(f"Loaded {len(documents)} Document objects from {FILE_NAME}\n")
for i, d in enumerate(documents[:8]):
    print(f"  doc {i:2d}: {d.metadata['title']}")
print("  ...")

# --- Production equivalent (loaders + splitters) ---
# from langchain_community.document_loaders import TextLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# raw = TextLoader(FILE_NAME, encoding="utf8").load()
# documents = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100).split_documents(raw)'''
)

# ---- Step 2 -----------------------------------------------------------------
slide("\U0001F5C4️ Step 2 — Connect a Vector Store", [
    "A vector store holds embeddings + their `Document`s",
    "We use LangChain's in-memory store for teaching",
    "Cosine similarity, no server required",
    "Production: `Milvus` (the original), Pinecone, pgvector",
    "Same LangChain interface — only the engine changes",
])
script(
    "Next we create the store that will hold our vectors. For class we use LangChain's "
    "`InMemoryVectorStore`, which needs no server and computes cosine similarity directly — the "
    "right metric for normalized text embeddings. The original tutorial connected to **Milvus**, a "
    "production vector database that persists data, scales to billions of vectors, and offers fast "
    "approximate indexes like HNSW. I have kept that Milvus connection code in comments so you can "
    "see the conceptual step — 'create a place to store and search vectors' — is identical; only "
    "the engine changes. Because both implement LangChain's vector-store interface, the code that "
    "ingests, retrieves, and builds the chain downstream is the same regardless of which backend "
    "you choose."
)
code(
    r'''from langchain_core.vectorstores import InMemoryVectorStore

vector_store = InMemoryVectorStore(embedding=embed_fn)
print("Created an empty InMemoryVectorStore (cosine similarity).")

# --- Production equivalent (the original used Milvus) ---
# from langchain_milvus import Milvus
# vector_store = Milvus(
#     embedding_function=embed_fn,
#     auto_id=True,
#     index_params={"index_type": "HNSW", "metric_type": "L2"},
#     connection_args={"host": "localhost", "port": 19530},
# )'''
)

# ---- Step 3 -----------------------------------------------------------------
slide("\U0001F4E5 Step 3 — Ingest: Embed & Index the Documents", [
    "`add_documents` embeds every chunk and indexes it",
    "The store calls `embed_fn` for us — one line",
    "Original text + metadata stay attached",
    "This is the offline, one-time cost of RAG",
    "After this, the store *is* the knowledge base",
])
script(
    "Now we populate the store. A single call, `add_documents`, asks the vector store to embed "
    "every chunk with our embeddings object and index the resulting vectors, keeping each "
    "`Document`'s text and metadata attached. Compare this to the framework-free notebook, where "
    "we embedded a matrix and managed a parallel list of texts by hand; LangChain hides that "
    "bookkeeping behind one method. This embedding pass is the one-time, offline cost of RAG — you "
    "pay it once when documents change, not on every query. After this step the vector store is "
    "our searchable knowledge base, and the very same call works unchanged if the backend is Milvus "
    "instead of the in-memory store."
)
code(
    r'''ids = vector_store.add_documents(documents)
print(f"Ingested {len(ids)} documents into the vector store.")
print("Each was embedded to", DIM, "dimensions and indexed for similarity search.")

# --- Production equivalent ---
# vector_store.add_documents(documents)   # identical call on Milvus, Pinecone, pgvector, ...'''
)

# ---- Step 4 -----------------------------------------------------------------
slide("\U0001F50D Step 4 — Retrieve Relevant Context", [
    "Embed the query with the **same** model (via the store)",
    "`similarity_search_with_score` → top-k (doc, score)",
    "Apply a **score threshold** to drop weak matches",
    "Join survivors into one `context` string (`get_context`)",
    "Or expose a `retriever` Runnable for the chain",
])
script(
    "Retrieval is the heart of RAG. The vector store embeds the query with the same model, finds "
    "the nearest chunks, and returns them with similarity scores. We reproduce the original's "
    "`get_context` function: take the top-k results, keep only those above a relevance threshold, "
    "and join them into one context block — returning a clear 'no context' sentinel when nothing "
    "is relevant, so the model never gets fed noise. As in the embeddings notebook, the threshold "
    "is model-specific: the original used 0.80 with Milvus's L2 metric, but with MiniLM cosine "
    "scores good matches sit around 0.4–0.8, so we use 0.35. LangChain also wraps all of this as a "
    "`retriever`, a Runnable whose `invoke` returns documents — the form the chain will consume in "
    "the next step."
)
code(
    r'''def get_context(query: str, k: int = 6, score_threshold: float = 0.35) -> str:
    """Retrieve chunks above a relevance threshold and join them into one context block.

    English re-implementation of the original get_context(); InMemoryVectorStore
    exposes cosine similarity via similarity_search_with_score (higher = better).
    """
    results = vector_store.similarity_search_with_score(query, k=k)
    kept = [doc.page_content for doc, score in results if score >= score_threshold]
    return "\n\n".join(kept) if kept else "No relevant context found."


query = "What are the four phases of incident response?"
print("Query:", query, "\n")
print("Top matches (title : score):")
for doc, score in vector_store.similarity_search_with_score(query, k=4):
    print(f"  {score:.3f}  {doc.metadata['title']}")

print("\n=== RETRIEVED CONTEXT (get_context) ===\n")
print(get_context(query)[:400], "...")'''
)
md("LangChain can also hand us a **retriever** — a Runnable we can drop straight into a chain:")
code(
    r'''retriever = vector_store.as_retriever(search_kwargs={"k": 6})
hits = retriever.invoke("how does ransomware extortion work?")
print("retriever.invoke returned", len(hits), "Documents:")
for d in hits[:3]:
    print("  -", d.metadata["title"])'''
)

# ---- Step 5 -----------------------------------------------------------------
slide("\U0001F517 Step 5 — Build the RAG Chain (`get_rag_chain`)", [
    "Prompt template with a **system role** + `{context}`",
    "Tag answers `[RAG]` (from docs) or `[LLM]` (own knowledge)",
    "Wire context in with `{context: get_context, query: passthrough}`",
    "Chain: prompt | model | `StrOutputParser`",
    "An offline stand-in model lets it run with no key",
])
script(
    "Now we design the prompt and assemble the chain — the heart of the original example. The "
    "system message gives the model its role, injects the retrieved context, and sets the output "
    "rule we borrowed from the source: tag the answer `[RAG]` when it relies on the supplied "
    "context and `[LLM]` when it falls back to general knowledge. That tag makes grounding visible. "
    "Then we compose the chain with LCEL. The original wrote `prompt | llm | str_parser` and passed "
    "context in separately; we wire retrieval directly into the chain using the parallel-branch "
    "pattern from `langchain.ipynb` — one branch runs `get_context`, the other passes the question "
    "through — so the chain takes just a question string. We plug in an offline stand-in model so "
    "the chain runs in class; Step 7 swaps in a real one."
)
code(
    r'''from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.messages import AIMessage

# Prompt: English translation of the original system prompt, with [RAG]/[LLM] tags.
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "# Role\n"
     "You are a cybersecurity Q&A expert. Use the CONTEXT below to answer the question.\n\n"
     "# Output format\n"
     "1. If the CONTEXT is empty or lacks the answer, answer from your own knowledge and "
     "prefix your reply with [LLM].\n"
     "2. If the answer is in the CONTEXT, answer using it and prefix your reply with [RAG].\n\n"
     "# Context\n{context}"),
    ("user", "{query}"),
])
str_parser = StrOutputParser()


def _offline_llm(prompt_value):
    """Offline stand-in for get_qwen_llm(): no API key needed.

    It reads the assembled prompt, decides [RAG] vs [LLM] from whether context
    was found, and returns an EXTRACTIVE answer (the retrieved text). A real
    model writes a fluent answer instead -- that is Step 7.
    """
    text = prompt_value.to_string() if hasattr(prompt_value, "to_string") else str(prompt_value)
    context = text.split("# Context", 1)[-1].split("Human:", 1)[0].strip()
    if context and "No relevant context found." not in context:
        snippet = " ".join(context.split())[:300]
        return AIMessage(content="[RAG] " + snippet + " ...")
    return AIMessage(content="[LLM] No relevant context in the knowledge base; "
                             "answering from general knowledge.")

offline_llm = RunnableLambda(_offline_llm)


def get_rag_chain(llm):
    """Build the RAG chain. Mirrors the original get_rag_chain() = prompt | llm | str_parser,
    but wires retrieval (get_context) into the chain so it takes just a query string."""
    return (
        {"context": RunnableLambda(get_context), "query": RunnablePassthrough()}
        | prompt
        | llm
        | str_parser
    )


rag_chain = get_rag_chain(offline_llm)
print("RAG chain built:", " | ".join(["{context, query}", "prompt", "llm", "StrOutputParser"]))

# --- Production equivalent (the original, with a hosted LLM) ---
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)   # == get_qwen_llm()
# rag_chain = get_rag_chain(llm)'''
)

# ---- Step 6 -----------------------------------------------------------------
slide("\U0001F4AC Step 6 — Ask Questions with the Chain", [
    "Call `rag_chain.invoke(question)` — retrieval is built in",
    "In-domain query → context found → `[RAG]`",
    "Out-of-domain query → no context → `[LLM]`",
    "One chain object handles the whole flow",
    "Swap the model for a real one in Step 7",
])
script(
    "Now we run the chain. Because retrieval is wired in, we just call `invoke` with a question "
    "string and the chain handles everything: fetch context, fill the prompt, call the model, parse "
    "the output. Watch the contrast between two queries. An in-domain question about incident "
    "response retrieves real passages, so the answer is tagged `[RAG]` and grounded in our "
    "knowledge base. An off-topic question about French geography retrieves nothing above "
    "threshold, so the chain falls back and tags the answer `[LLM]`. That difference is the whole "
    "point of RAG — it grounds answers in your data when your data is relevant, and gets out of the "
    "way when it is not. The offline model here is extractive; the real model in Step 7 will write "
    "a fluent answer over the same retrieved context."
)
code(
    r'''print("--- In-domain query (expect [RAG]) ---")
print(rag_chain.invoke("What are the four phases of incident response?"))

print("\n--- In-domain query (expect [RAG]) ---")
print(rag_chain.invoke("How does ransomware double extortion work?"))

print("\n--- Out-of-domain query (expect [LLM]) ---")
print(rag_chain.invoke("What is the capital of France?"))'''
)

# ---- Step 7 -----------------------------------------------------------------
slide("\U0001F680 Step 7 — Go Live with ChatOpenAI", [
    "Swap the offline stand-in for a real `ChatOpenAI`",
    "**Nothing else changes** — same `get_rag_chain`",
    "Now the model *writes* a fluent grounded answer",
    "Compare RAG vs. a pure LLM (no context)",
    "Needs the `OPENAI_API_KEY` environment variable",
])
script(
    "Finally, we prove the framework's promise: portability. We swap the offline stand-in for a "
    "real `ChatOpenAI` model — one line — and rebuild the chain with the very same `get_rag_chain` "
    "function. Everything upstream, the loader, vector store, retriever, prompt, and parser, is "
    "untouched. Now the model actually writes a fluent answer grounded in the retrieved context, "
    "and tags it `[RAG]`. For contrast we also run a pure-LLM chain with no retrieval, which "
    "answers from the model's own memory. On an in-domain question the RAG answer is specific and "
    "citable; on an out-of-domain question RAG correctly declines while the pure LLM falls back to "
    "general knowledge. This step needs an OpenAI API key; if none is set, it prints a notice and "
    "skips, so the rest of the notebook still runs offline."
)
code(
    r'''import os

if not os.getenv("OPENAI_API_KEY"):
    print("OPENAI_API_KEY not set — skipping the live step.")
    print("Set it (e.g. in your .env or shell) to run a real model here.")
else:
    from langchain_openai import ChatOpenAI

    # The ONLY change from offline: a real model object.
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)   # == get_qwen_llm()
    live_chain = get_rag_chain(llm)                         # same builder, real model

    # Pure-LLM chain for comparison: no retrieval, model's own knowledge.
    from langchain_core.prompts import ChatPromptTemplate as CPT
    plain_chain = (
        CPT.from_messages([("system", "You are a helpful expert. Answer concisely."),
                           ("user", "{query}")])
        | llm | StrOutputParser()
    )

    for q in ["What are the four phases of incident response in the NIST framework?",
              "What is the capital of France?"]:
        print("=" * 76)
        print("Q:", q)
        print("\n[RAG chain]   ", live_chain.invoke(q))
        print("\n[Pure LLM]    ", plain_chain.invoke({"query": q}))
        print()'''
)

# ---- Summary ----------------------------------------------------------------
slide("✅ Summary — RAG, the LangChain Way", [
    "Load → `Document`s → vector store → retriever",
    "`get_context`: retrieve with a relevance threshold",
    "`get_rag_chain`: `{context, query} | prompt | model | parser`",
    "Offline stand-in ↔ real model: a **one-line** swap",
    "Same recipe scales to Milvus + a hosted LLM",
])
script(
    "We rebuilt a complete RAG system using LangChain. The components map one-to-one onto the "
    "framework-free pipeline you already knew: documents and a vector store replace the raw matrix, "
    "a retriever and `get_context` replace manual top-k search, and the LCEL chain "
    "`{context, query} | prompt | model | parser` replaces hand-wired prompting. The biggest lesson "
    "is composability and portability: swapping the offline stand-in for `ChatOpenAI`, or the "
    "in-memory store for Milvus, is a one-line change because every component shares the same "
    "interface. Keep the fundamentals from the embeddings notebook — chunk for precision, embed "
    "queries and documents with the same model, threshold your retrieval, make grounding visible — "
    "and LangChain becomes the clean scaffolding that turns those ideas into a maintainable, "
    "production-ready application."
)
code(
    r'''print("RAG with LangChain:")
print("  documents -> vector store -> retriever -> {context, query} | prompt | model | parser")
print("\nOffline stand-in or ChatOpenAI, InMemoryVectorStore or Milvus: same chain, same recipe.")'''
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

with open("langchain_example.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Wrote langchain_example.ipynb with {len(cells)} cells.")
