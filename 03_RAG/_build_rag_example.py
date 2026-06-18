"""Generator for rag_example.ipynb — an end-to-end RAG walkthrough.

Adapted (in English, new domain, richer data) from a Chinese LangChain +
Milvus + Qwen example. Mirrors the original 6 steps:
  1. Load data   2. Connect DB   3. Ingest   4. Retrieve   5. Build chain   6. Ask

Presentation style matches embedding.ipynb: each topic = slide + instructor
script + runnable code. Runs offline with sentence-transformers + faiss.

Run:  python _build_rag_example.py   ->  writes rag_example.ipynb
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
    "# Retrieval-Augmented Generation: A Worked Example\n"
    "### Building a RAG System over a Cybersecurity Knowledge Base\n\n"
    "**Audience:** Graduate students who have completed the `embedding.ipynb` notebook.\n\n"
    "**Goal:** Take the concepts (embeddings, chunking, retrieval, re-ranking) and assemble "
    "them into a complete, working RAG pipeline that answers questions from documents.\n\n"
    "We follow the classic **six-step RAG recipe**, then add a step that proves RAG's value:\n"
    "1. \U0001F4C4 Load & chunk the data\n"
    "2. \U0001F5C4️ Connect to a vector store\n"
    "3. \U0001F4E5 Ingest (embed + index) the chunks\n"
    "4. \U0001F50D Retrieve relevant context for a query\n"
    "5. \U0001F517 Build the RAG prompt / chain\n"
    "6. \U0001F4AC Ask questions with RAG\n\n"
    "7. \U0001F52C Compare RAG vs. a pure LLM (OpenAI) and score the answers\n\n"
    "> **Reproducibility note:** Steps 1-6 run **offline** with `sentence-transformers` and "
    "`faiss` so they work in class without any server or API key, and each shows the "
    "**production equivalent** (LangChain + a managed vector database like Milvus) in comments. "
    "**Step 7 calls the OpenAI API**, so it needs the `OPENAI_API_KEY` environment variable set."
)

md("## \U0001F6E0️ Setup")
code(
    r'''# If needed, install dependencies:
# !pip install -q sentence-transformers faiss-cpu numpy

import numpy as np
from sentence_transformers import SentenceTransformer

np.set_printoptions(precision=3, suppress=True)

# One embedding model, used for BOTH documents and queries.
# (Using two different models would put them in incompatible vector spaces!)
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
DIM = embed_model.get_sentence_embedding_dimension()
print("Embedding model ready -", DIM, "dimensions")'''
)

# ---- Step 1 -----------------------------------------------------------------
slide("\U0001F4C4 Step 1 — Load & Chunk the Data", [
    "Read the source document from disk",
    "Split it into **chunks** the model can embed",
    "Here: split a Markdown file on its `#` section headers",
    "Each section becomes one retrievable chunk",
    "Real systems also handle PDFs, HTML, code, etc.",
])
script(
    "Every RAG system begins with data. We load a Markdown knowledge base and split it into "
    "chunks — the unit we will embed and retrieve. Our document is organized by `#` section "
    "headers, so splitting on `#` gives clean, self-contained passages, one per security topic. "
    "This header-based strategy is a simple form of *semantic chunking*: each chunk is already a "
    "coherent idea, which is exactly what we want for precise retrieval. Recall from the "
    "embeddings notebook why we chunk at all: embedding a whole document averages all its topics "
    "into one blurry vector. Chunking keeps each topic sharp so a query can match the specific "
    "passage that answers it."
)
code(
    r'''FILE_NAME = "cybersecurity_kb.md"

with open(FILE_NAME, mode="r", encoding="utf8") as f:
    text = f.read()

# Split on Markdown headers; drop empty fragments and trim whitespace.
chunks = [item.strip() for item in text.split("#") if item.strip()]

print(f"Loaded {len(chunks)} chunks from {FILE_NAME}\n")
for i, c in enumerate(chunks):
    title = c.splitlines()[0]
    print(f"  chunk {i:2d}: {title}")'''
)

# ---- Step 2 -----------------------------------------------------------------
slide("\U0001F5C4️ Step 2 — Connect to the Vector Store", [
    "A vector store holds embeddings + their source text",
    "We use an in-memory **FAISS** index for teaching",
    "Cosine similarity via inner product on normalized vectors",
    "Production: a managed DB (Milvus, Pinecone, pgvector)",
    "Same idea — just persistent and scalable",
])
script(
    "Next we create the container that will hold our vectors. For class we use FAISS, an "
    "in-memory index that needs no server. We choose an inner-product index and will store "
    "normalized vectors, which makes the inner product equal to cosine similarity — the metric "
    "we want for text. In production you would instead connect to a managed vector database such "
    "as Milvus, which persists data, scales to billions of vectors, and offers fast approximate "
    "indexes like HNSW. I have left the original LangChain + Milvus connection code in comments "
    "so you can see that the conceptual step — 'create a place to store and search vectors' — "
    "is identical; only the engine changes."
)
code(
    r'''import faiss

# Inner-product index; with normalized vectors this equals cosine similarity.
index = faiss.IndexFlatIP(DIM)
print("Created empty FAISS index. Vectors stored:", index.ntotal)

# --- Production equivalent (the original Chinese example used Milvus) ---
# from langchain_milvus import Milvus
# from models import get_embed
# embed_fn = get_embed()
# db = Milvus(embedding_function=embed_fn,
#             auto_id=True,
#             index_params={"index_type": "HNSW", "metric_type": "L2"},
#             connection_args={"host": "localhost", "port": 19530})
# db.drop()   # clear any existing collection'''
)

# ---- Step 3 -----------------------------------------------------------------
slide("\U0001F4E5 Step 3 — Ingest: Embed & Index the Chunks", [
    "Embed every chunk into a vector",
    "Normalize so inner product = cosine",
    "Add the vectors to the index",
    "Keep the original text in parallel for lookup",
    "This is your searchable knowledge base",
])
script(
    "Now we populate the store. We embed all chunks in one batch, normalize them, and add them "
    "to the FAISS index; we keep the `chunks` list itself so that, given a matching vector's "
    "position, we can return the human-readable passage. This is the offline, one-time cost of "
    "RAG: embedding the corpus. After this step the index *is* our knowledge base — a matrix of "
    "meaning we can search in milliseconds. Note that we deliberately reuse `embed_model`, the "
    "same model we will use for queries. Mixing models here is a classic and silent bug: the "
    "vectors would live in different spaces and similarity scores would be meaningless."
)
code(
    r'''# Embed all chunks at once (normalized for cosine similarity).
chunk_vectors = embed_model.encode(chunks, normalize_embeddings=True).astype("float32")

index.add(chunk_vectors)
print("Ingested", index.ntotal, "chunks into the index.")
print("Index matrix shape:", chunk_vectors.shape, "(rows = chunks, cols = dims)")

# --- Production equivalent ---
# db.add_texts(texts=chunks)   # LangChain/Milvus embeds + stores in one call'''
)

# ---- Step 4 -----------------------------------------------------------------
slide("\U0001F50D Step 4 — Retrieve Relevant Context", [
    "Embed the query with the **same** model",
    "Search the index for the top-k nearest chunks",
    "Apply a **score threshold** to drop weak matches",
    "Concatenate survivors into a `context` string",
    "This context is what we feed the LLM",
])
script(
    "Retrieval is the heart of RAG. We embed the query with the same model, search the index for "
    "the k nearest chunks, and keep only those above a relevance threshold. The threshold matters: "
    "if nothing is relevant, we would rather return 'no context' than feed the model junk that "
    "invites hallucination. One subtlety carried over from the embeddings notebook — thresholds "
    "are *model-specific*. The original example used 0.7–0.8 with a different model and an L2 "
    "metric; with MiniLM cosine scores, good matches often sit around 0.3–0.6, so we set the "
    "threshold accordingly. Always calibrate the threshold on your own data rather than copying a "
    "number from elsewhere."
)
code(
    r'''def retrieve(query, k=4):
    """Return the top-k (score, chunk) pairs for a query."""
    q = embed_model.encode(query, normalize_embeddings=True).astype("float32")
    scores, idx = index.search(q.reshape(1, -1), k)
    return [(float(s), chunks[i]) for s, i in zip(scores[0], idx[0])]


query = "How can attackers trick employees into giving up passwords?"
print("Query:", query, "\n")
for rank, (s, chunk) in enumerate(retrieve(query, k=4), 1):
    title = chunk.splitlines()[0]
    print(f"{rank}. score={s:.3f}  ->  {title}")'''
)
md("Now wrap retrieval in a `get_context` helper that applies a relevance threshold "
   "(mirroring the original `get_context` function):")
code(
    r'''def get_context(query, k=6, score_threshold=0.35):
    """Retrieve chunks above a relevance threshold and join them into one context block."""
    results = retrieve(query, k=k)
    kept = [chunk for score, chunk in results if score >= score_threshold]
    return "\n\n".join(kept) if kept else "No relevant context found."


query = "What does the never trust, always verify model mean?"
print("Query:", query, "\n")
print("=== RETRIEVED CONTEXT ===\n")
print(get_context(query))'''
)

# ---- Step 5 -----------------------------------------------------------------
slide("\U0001F517 Step 5 — Build the RAG Prompt / Chain", [
    "A prompt template with a **system role** + the context",
    "Instruct the model to answer *from the context*",
    "Tag answers `[RAG]` (from docs) or `[LLM]` (own knowledge)",
    "Chain: prompt → LLM → output parser",
    "Context is injected fresh on every query",
])
script(
    "With retrieval working, we design the prompt that turns context into an answer. The system "
    "message gives the model a role, pastes in the retrieved context, and sets output rules. We "
    "borrow a nice idea from the original example: the model tags its answer `[RAG]` when it "
    "relies on the supplied context, and `[LLM]` when it falls back to its own knowledge because "
    "the context was empty or irrelevant. That tag makes grounding visible to the user and is "
    "great for debugging. In LangChain this is expressed elegantly as a chain — "
    "`prompt | llm | parser` — but conceptually it is just: fill the template, call the "
    "model, parse the text. We build a runnable, framework-free version here."
)
code(
    r'''SYSTEM_PROMPT = (
    "# Role\n"
    "You are a cybersecurity Q&A expert. Use the CONTEXT below to answer the user's question.\n\n"
    "# Output format\n"
    "1. If the CONTEXT is empty or does not contain the answer, answer from your own knowledge "
    "and prefix your reply with [LLM].\n"
    "2. If the answer is found in the CONTEXT, answer using it and prefix your reply with [RAG].\n\n"
    "# Context\n"
    "{context}\n"
)


def build_messages(query, context):
    """Assemble the chat messages a RAG chain would send to the LLM."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT.format(context=context)},
        {"role": "user", "content": query},
    ]


# Preview the fully assembled prompt for one query:
q = "What are the phases of incident response?"
msgs = build_messages(q, get_context(q))
print(msgs[0]["content"])
print("USER:", msgs[1]["content"])

# --- Production equivalent (LangChain) ---
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# from models import get_qwen_llm
# prompt = ChatPromptTemplate.from_messages([("system", SYSTEM_PROMPT), ("user", "{query}")])
# rag_chain = prompt | get_qwen_llm() | StrOutputParser()'''
)

# ---- Step 6 -----------------------------------------------------------------
slide("\U0001F4AC Step 6 — Ask Questions with RAG", [
    "Combine: retrieve context → build prompt → generate",
    "Grounded answers cite your documents, not guesses",
    "Compare an **in-domain** vs **out-of-domain** query",
    "In-domain → `[RAG]`; out-of-domain → `[LLM]`",
    "The generation call is one API line away",
])
script(
    "Finally we run the full loop. For a given question we retrieve context, assemble the prompt, "
    "and send it to an LLM to generate the answer. To keep the notebook offline, the generation "
    "call is shown as a commented template you can enable with any chat model; the runnable code "
    "shows exactly what would be sent. Watch the contrast between two queries: an in-domain "
    "question about incident response pulls real passages and would be answered `[RAG]`, while an "
    "off-topic question about, say, French geography retrieves nothing relevant, so the model "
    "would fall back to `[LLM]`. That difference is the whole point of RAG — it grounds answers "
    "in your data when your data is relevant, and gets out of the way when it is not."
)
code(
    r'''def rag_answer(query, score_threshold=0.35):
    """Full RAG step: retrieve -> build prompt -> (generate)."""
    context = get_context(query, score_threshold=score_threshold)
    messages = build_messages(query, context)

    grounded = context != "No relevant context found."
    print("QUESTION  :", query)
    print("GROUNDED? :", "YES -> expect [RAG]" if grounded else "NO  -> expect [LLM]")
    print("CONTEXT   :", (context[:120] + "...") if grounded else context)

    # --- Real generation (uncomment and set a key to get a live answer) ---
    # from anthropic import Anthropic
    # client = Anthropic(api_key="YOUR_KEY")
    # resp = client.messages.create(
    #     model="claude-haiku-4-5-20251001", max_tokens=300,
    #     system=SYSTEM_PROMPT.format(context=context),
    #     messages=[{"role": "user", "content": query}])
    # print("ANSWER    :", resp.content[0].text)
    return messages


print("--- In-domain query ---")
_ = rag_answer("What are the phases of incident response?")

print("\n--- Out-of-domain query ---")
_ = rag_answer("What is the capital of France?")'''
)

# ---- Step 7 -----------------------------------------------------------------
slide("\U0001F52C Step 7 — RAG vs. Pure LLM: Score & Compare", [
    "Ask **OpenAI** the same question two ways",
    "Pure LLM = model's own knowledge (no context)",
    "RAG = same model, grounded in our knowledge base",
    "An **LLM judge** scores each answer 0–10",
    "Show the winner, labeled with where it came from",
])
script(
    "How do we know RAG actually helps? We test it. For each question we ask the same OpenAI "
    "model twice: once with no context (a pure LLM) and once with our retrieved context (RAG). "
    "Then we use a second model call as an impartial *judge* to score each answer from 0 to 10 "
    "for correctness and helpfulness, and we display the higher-scoring answer prefixed with its "
    "source. The result depends entirely on coverage. When the question is about our domain — "
    "cybersecurity incident response — RAG supplies precise, grounded facts and wins. When the "
    "question is off-topic, our knowledge base has nothing useful, RAG correctly declines, and "
    "the pure LLM's general knowledge wins. This is exactly the evaluation mindset you need: RAG "
    "is not always better, it is better *when your data is relevant*."
)
code(
    r'''import os
from openai import OpenAI

OPENAI_MODEL = "gpt-4o-mini"   # change to a model enabled on your account

# Reads the key from the OPENAI_API_KEY environment variable.
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("OpenAI client ready. Model:", OPENAI_MODEL)'''
)
code(
    r'''import re


def ask_openai(system, user):
    """Single OpenAI chat call -> answer text."""
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
    )
    return resp.choices[0].message.content.strip()


def ask_plain(query):
    """Pure LLM: answer from the model's own knowledge, no retrieval."""
    system = "You are a helpful expert. Answer the question concisely from your own knowledge."
    return ask_openai(system, query)


def ask_rag(query, score_threshold=0.35):
    """RAG: same model, but answer ONLY from the retrieved context."""
    context = get_context(query, score_threshold=score_threshold)
    system = (
        "You are a cybersecurity Q&A expert. Answer the question using ONLY the context below. "
        "If the context does not contain the answer, reply exactly: "
        "'I cannot answer this from the provided documents.'\n\n# Context\n" + context
    )
    return ask_openai(system, query)


def judge(query, answer):
    """LLM-as-judge: rate an answer 0-10 for correctness + helpfulness."""
    system = ("You are a strict evaluator. Given a QUESTION and an ANSWER, rate the ANSWER's "
              "correctness and helpfulness from 0 to 10. Respond with ONLY an integer.")
    raw = ask_openai(system, f"QUESTION: {query}\nANSWER: {answer}")
    m = re.search(r"\d+", raw)
    return int(m.group()) if m else 0


print("Helpers defined: ask_plain, ask_rag, judge")'''
)
code(
    r'''def compare(query, score_threshold=0.35):
    """Answer a query with both methods, score each, and show the winner."""
    plain_ans = ask_plain(query)
    rag_ans = ask_rag(query, score_threshold=score_threshold)
    s_plain = judge(query, plain_ans)
    s_rag = judge(query, rag_ans)

    # Pick the higher-scoring answer (ties go to RAG, since it is grounded/citable).
    if s_rag >= s_plain:
        source, best = "RAG  (grounded in the knowledge base)", rag_ans
    else:
        source, best = "OpenAI API  (pure LLM, no context)", plain_ans

    print("=" * 72)
    print(f"BEST ANSWER FROM -> {source}")          # where the higher response came from
    print(f"Scores  ->  RAG: {s_rag}/10   |   Pure LLM: {s_plain}/10")
    print("=" * 72)
    print("Q:", query)
    print("\nBEST ANSWER:\n" + best + "\n")


# Query 1 — IN-DOMAIN: the knowledge base covers this, so RAG should win.
compare("What are the four phases of incident response in the NIST framework?")

# Query 2 — OUT-OF-DOMAIN: not in our KB, so the pure LLM should win.
compare("Who developed the theory of general relativity, and in what year was it published?")'''
)

# ---- Summary ----------------------------------------------------------------
slide("✅ Summary — The RAG Recipe", [
    "Load → **chunk** the documents",
    "**Embed** chunks → store in a vector index",
    "**Retrieve** top-k context (with a threshold)",
    "Inject context into a **prompt template**",
    "**Generate** a grounded, tagged answer",
])
script(
    "We assembled a complete RAG system in six steps: load and chunk the data, embed and index "
    "the chunks, retrieve relevant context with a calibrated threshold, build a prompt that "
    "injects that context, and generate a grounded answer. The same skeleton scales from this "
    "in-memory FAISS demo to a production system on Milvus or Pinecone with a hosted LLM — only "
    "the components swap out, while the pipeline stays the same. The big ideas to remember: chunk "
    "for precision, always embed queries and documents with the same model, threshold your "
    "retrieval to avoid feeding the model noise, and make grounding visible. Master this recipe "
    "and you can build a question-answering system over any document collection you are given."
)
code(
    r'''print("RAG pipeline:")
print("  documents -> chunk -> embed -> vector store -> retrieve(+threshold) -> prompt -> LLM -> answer")
print("\nYou just built every stage of that pipeline over a real knowledge base.")'''
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

with open("rag_example.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Wrote rag_example.ipynb with {len(cells)} cells.")
