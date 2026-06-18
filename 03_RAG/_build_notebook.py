"""Generator for embedding.ipynb — a graduate-level RAG teaching notebook.

Each topic is rendered as three cells:
  1. A slide-style markdown cell (bullet points).
  2. An "Instructor Script" markdown cell (80-150 words of narration).
  3. A runnable code cell with a well-designed, printed output.

Run:  python _build_notebook.py   ->  writes embedding.ipynb
"""
import json

cells = []


def md(source: str):
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    })


def code(source: str):
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.rstrip("\n").splitlines(keepends=True),
    })


def slide(title, bullets):
    md(f"# {title}\n\n" + "\n".join(f"- {b}" for b in bullets))


def script(text):
    md("> ### \U0001F3A4 Instructor Script\n>\n> " + text.replace("\n", "\n> "))


# ----------------------------------------------------------------------------
# Title / Course framing
# ----------------------------------------------------------------------------
md(
    "# Embeddings & Retrieval-Augmented Generation (RAG)\n"
    "### A Graduate-Level, Hands-On Teaching Notebook\n\n"
    "**Audience:** Graduate students in CS / Data Science / Cybersecurity AI.\n\n"
    "**Format:** Each topic has three parts —\n"
    "1. \U0001F4CA a *slide* (bullet points) you can project,\n"
    "2. \U0001F3A4 an *instructor script* to read and explain, and\n"
    "3. \U0001F4BB a *runnable code example* with clean output.\n\n"
    "**Design choice:** All examples run **locally and offline** using open-source "
    "models (`sentence-transformers`, `scikit-learn`, `faiss`). No API keys are required, "
    "so the notebook is fully reproducible in class.\n\n"
    "---\n\n"
    "## Learning Objectives\n"
    "By the end of this notebook, students will be able to:\n"
    "- Explain what an embedding is and how it differs from hashing and classical vectorization.\n"
    "- Distinguish static vs. contextual embeddings and the role of attention.\n"
    "- Measure semantic similarity and reason about vector geometry.\n"
    "- Chunk documents, build a vector index, retrieve, and **re-rank** results.\n"
    "- Assemble a complete RAG pipeline and recognize common failure modes."
)

# ----------------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------------
md("## \U0001F6E0️ Setup — Install & Import\n\n"
   "Run this once. The first model download is ~90 MB and is cached afterward.")

code(
    "# If running locally / Colab, uncomment to install:\n"
    "# !pip install -q sentence-transformers scikit-learn faiss-cpu matplotlib numpy\n\n"
    "import numpy as np\n"
    "import matplotlib.pyplot as plt\n\n"
    "np.set_printoptions(precision=3, suppress=True)\n"
    "print('Core libraries loaded.')"
)

code(
    "# Load a small, fast, high-quality sentence-embedding model (384 dims).\n"
    "# This is the workhorse for the rest of the notebook.\n"
    "from sentence_transformers import SentenceTransformer\n\n"
    "model = SentenceTransformer('all-MiniLM-L6-v2')\n"
    "print('Model loaded:', model.get_sentence_embedding_dimension(), 'dimensions')"
)

# ----------------------------------------------------------------------------
# 1. What is an embedding
# ----------------------------------------------------------------------------
slide("\U0001F9E0 1 — What is an Embedding?", [
    "Text → vector (a list of numbers)",
    "**Fixed-length** representation",
    "Captures **semantic meaning**, not spelling",
    "Similar meaning → nearby vectors",
    "The foundation of modern AI retrieval",
])
script(
    "An embedding converts human language into numbers so a machine can reason about "
    "*meaning* mathematically. Instead of treating words as isolated symbols, we map them "
    "into a high-dimensional vector space where distance reflects similarity in meaning. "
    "The words “cat” and “dog” land near each other, while “cat” and "
    "“car” sit far apart. This lets us do similarity search, clustering, "
    "classification, and retrieval with simple geometry. Embeddings power semantic search, "
    "recommendation engines, and the retrieval step of RAG. The single idea I want students "
    "to keep: **embeddings represent meaning, not text**. Everything else in this notebook "
    "builds on that one shift in perspective."
)
code(
    "vec = model.encode('cat')\n"
    "print('Type          :', type(vec).__name__)\n"
    "print('Dimensions    :', vec.shape[0])\n"
    "print('First 5 values:', vec[:5])\n"
    "print('Vector norm   :', round(float(np.linalg.norm(vec)), 4))"
)

# ----------------------------------------------------------------------------
# 2. Classical vectorization (one-hot / BoW)
# ----------------------------------------------------------------------------
slide("\U0001F520 2 — From Text to Numbers: Classical Vectorization", [
    "One-hot: 1 dimension per word, mostly zeros",
    "Bag-of-Words (BoW): counts of words",
    "**Sparse** & **high-dimensional**",
    "No notion of meaning or word order",
    "The pre-deep-learning baseline",
])
script(
    "Before neural embeddings, we turned text into numbers with counting. One-hot encoding "
    "gives each vocabulary word its own dimension — a vector that is all zeros except a "
    "single 1. Bag-of-Words extends this to counts across a document. These representations "
    "are *sparse* (mostly zeros), *huge* (one dimension per vocabulary word), and crucially "
    "they encode **identity, not meaning**: “great” and “excellent” are as "
    "different as “great” and “banana.” There is no similarity structure. "
    "Understanding this baseline matters because it shows precisely what dense embeddings buy "
    "us: a compact space where geometric closeness equals semantic closeness."
)
code(
    "from sklearn.feature_extraction.text import CountVectorizer\n\n"
    "corpus = ['the cat sat', 'the dog sat', 'the car drove']\n"
    "cv = CountVectorizer()\n"
    "X = cv.fit_transform(corpus)\n\n"
    "print('Vocabulary:', cv.get_feature_names_out())\n"
    "print('\\nBag-of-Words matrix (rows = docs):')\n"
    "print(X.toarray())\n"
    "print('\\nNote: shape =', X.shape, '-> 1 column per unique word, mostly zeros.')"
)

# ----------------------------------------------------------------------------
# 3. TF-IDF
# ----------------------------------------------------------------------------
slide("\U0001F4C8 3 — TF-IDF: Smarter Counting", [
    "Term Frequency × Inverse Document Frequency",
    "Down-weights common words (“the”, “is”)",
    "Up-weights rare, distinctive words",
    "Still sparse, still no semantics",
    "A strong, cheap retrieval baseline (BM25 cousin)",
])
script(
    "TF-IDF improves on raw counts by asking: how *distinctive* is this word? Term frequency "
    "rewards words that appear often in a document; inverse document frequency penalizes words "
    "that appear in *every* document. The product highlights terms that characterize a specific "
    "document — “backpropagation” matters more than “the.” TF-IDF and its "
    "ranking cousin BM25 still power production search and remain a strong baseline you should "
    "always compare against. But notice the ceiling: it matches on *words*, not *meaning*. A "
    "query for “automobile” will not match a document about “cars.” That gap "
    "is exactly what dense embeddings close."
)
code(
    "from sklearn.feature_extraction.text import TfidfVectorizer\n\n"
    "docs = ['the cat sat on the mat',\n"
    "        'the dog sat on the log',\n"
    "        'neural networks learn representations']\n"
    "tfidf = TfidfVectorizer()\n"
    "M = tfidf.fit_transform(docs).toarray()\n\n"
    "import numpy as np\n"
    "vocab = tfidf.get_feature_names_out()\n"
    "for i, row in enumerate(M):\n"
    "    top = np.argsort(row)[::-1][:3]\n"
    "    terms = [(vocab[j], round(row[j], 2)) for j in top if row[j] > 0]\n"
    "    print(f'Doc {i}: top terms ->', terms)"
)

# ----------------------------------------------------------------------------
# 4. Embeddings vs hashing
# ----------------------------------------------------------------------------
slide("\U0001F510 4 — Embeddings vs Hashing", [
    "Both: variable input → fixed-length output",
    "Hashing = **identity** (security, lookup)",
    "Embeddings = **meaning** (similarity)",
    "Tiny input change → totally different hash",
    "Tiny meaning change → nearby embedding",
])
script(
    "Students often conflate embeddings with hashing because both map variable-length input to "
    "a fixed-length output. The *purpose* is opposite. A cryptographic hash is designed so that "
    "changing one character scrambles the entire output — there is deliberately **no** "
    "similarity between the hashes of “cat” and “cats.” That is what makes "
    "hashing good for integrity checks and dictionary lookups. Embeddings are designed for the "
    "reverse: small changes in meaning produce small changes in the vector, so “cat” "
    "and “cats” land almost on top of each other. The conceptual shift is from "
    "**exact match** to **semantic similarity** — and that shift is what makes modern "
    "search possible."
)
code(
    "import hashlib\n\n"
    "def sha(s):\n"
    "    return hashlib.sha256(s.encode()).hexdigest()[:12]\n\n"
    "print('--- Hashing: no similarity ---')\n"
    "print('cat :', sha('cat'))\n"
    "print('cats:', sha('cats'), '<- completely different\\n')\n\n"
    "from numpy import dot\n"
    "from numpy.linalg import norm\n"
    "a, b = model.encode('cat'), model.encode('cats')\n"
    "cos = dot(a, b) / (norm(a) * norm(b))\n"
    "print('--- Embedding: high similarity ---')\n"
    "print('cosine(cat, cats) =', round(float(cos), 3), '<- nearly identical meaning')"
)

# ----------------------------------------------------------------------------
# 5. Static vs contextual
# ----------------------------------------------------------------------------
slide("⚙️ 5 — Static vs Contextual Embeddings", [
    "Word2Vec/GloVe: one fixed vector per word (**static**)",
    "Problem: “bank” (money) vs “bank” (river)",
    "Transformers: vector depends on **context**",
    "**Attention** mixes in surrounding words",
    "Today we embed *sentences*, not just words",
])
script(
    "Early models like Word2Vec gave every word a single fixed vector — “bank” had "
    "one representation regardless of context. That breaks on polysemy: a financial “bank” "
    "and a river “bank” are unrelated, yet share a vector. Transformer models produce "
    "*contextual* embeddings: the representation of a word is computed from the whole sentence "
    "through the **attention mechanism**, which lets each token ‘look at’ the others. "
    "So “bank” near “money” and “bank” near “river” get "
    "different vectors. Sentence-transformer models pool these token vectors into a single "
    "sentence embedding. The takeaway: modern embeddings represent **meaning in context**, "
    "which is why they handle real, ambiguous language so well."
)
code(
    "pairs = [\n"
    "    ('I deposited money at the bank',   'the bank approved my loan'),\n"
    "    ('I deposited money at the bank',   'we sat on the river bank'),\n"
    "]\n"
    "for s1, s2 in pairs:\n"
    "    e1, e2 = model.encode([s1, s2])\n"
    "    cos = float(np.dot(e1, e2) / (np.linalg.norm(e1) * np.linalg.norm(e2)))\n"
    "    print(f'{cos:.3f}  | {s1!r}  vs  {s2!r}')\n"
    "print('\\nSame word \\'bank\\', but financial vs river context scores lower similarity.')"
)

# ----------------------------------------------------------------------------
# 6. Measuring similarity
# ----------------------------------------------------------------------------
slide("\U0001F4CF 6 — Measuring Similarity", [
    "**Cosine similarity**: angle between vectors, range [-1, 1]",
    "1 = same direction (meaning), 0 = unrelated",
    "Dot product: cosine when vectors are normalized",
    "Euclidean distance: straight-line gap",
    "Cosine is the default for text retrieval",
])
script(
    "Embeddings are only useful once we can compare them. The dominant metric for text is "
    "**cosine similarity**, the cosine of the angle between two vectors. It focuses on "
    "*direction* — which encodes meaning — and ignores magnitude, so longer texts "
    "aren’t unfairly favored. A score near 1 means ‘almost the same meaning,’ "
    "near 0 means ‘unrelated,’ and negative means ‘opposed.’ When vectors are "
    "L2-normalized, cosine and dot product are equivalent, which is why vector databases often "
    "store normalized vectors and use a fast dot product. Euclidean distance is an alternative "
    "but is sensitive to magnitude. Similarity metrics are what turn a pile of numbers into "
    "actionable ranking."
)
code(
    "def cosine(a, b):\n"
    "    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))\n\n"
    "words = ['cat', 'kitten', 'dog', 'car']\n"
    "embs = model.encode(words)\n\n"
    "print('Cosine similarity to \"cat\":')\n"
    "for w, e in zip(words, embs):\n"
    "    bar = '#' * int(cosine(embs[0], e) * 20)\n"
    "    print(f'  cat <-> {w:7s}: {cosine(embs[0], e):.3f}  {bar}')"
)

# ----------------------------------------------------------------------------
# 7. Fixed dimensions
# ----------------------------------------------------------------------------
slide("\U0001F9E9 7 — Why Fixed Dimensions?", [
    "Every vector has the **same length** (e.g. 384, 768, 1536)",
    "Enables uniform storage & fast comparison",
    "Independent of input length",
    "More dims = richer meaning, higher cost",
    "A model design tradeoff",
])
script(
    "Every embedding from a given model has the same number of dimensions — 384 for "
    "MiniLM, 768 for many BERT models, 1536 for some commercial APIs — regardless of whether "
    "the input is one word or a paragraph. This uniformity is what makes vectors comparable and "
    "storable in a single matrix or index; you cannot take the cosine of two vectors of different "
    "lengths. Dimensionality is a capacity knob: more dimensions can encode finer distinctions but "
    "cost more memory and compute and can need more data to use well. The practical lesson: pick a "
    "dimensionality that balances accuracy against storage and latency for your system."
)
code(
    "samples = ['hi', 'machine learning', 'a much longer sentence about neural retrieval systems']\n"
    "for s in samples:\n"
    "    e = model.encode(s)\n"
    "    print(f'len(input_words)={len(s.split()):2d}  ->  embedding dims = {e.shape[0]}')\n"
    "print('\\nInput length varies; output dimensionality is constant.')"
)

# ----------------------------------------------------------------------------
# 8. Model comparison
# ----------------------------------------------------------------------------
slide("\U0001F30D 8 — Choosing an Embedding Model", [
    "Open-source: MiniLM (384), BGE, E5 — free, local",
    "Commercial APIs: often 768–3072 dims",
    "Each model has its **own vector space**",
    "Vectors from different models are **not** comparable",
    "Choose on accuracy, cost, latency, privacy",
])
script(
    "There is no single ‘best’ embedding model; there is a best fit for your "
    "constraints. Open-source models such as MiniLM, BGE, and E5 run locally for free and keep "
    "data private — ideal for teaching and for sensitive domains like security. Commercial "
    "APIs may offer higher accuracy at the cost of money, latency, and sending data off-site. The "
    "critical gotcha: **each model defines its own vector space.** An embedding from model A is "
    "meaningless to model B, so you must embed your queries and your documents with the *same* "
    "model, and you must re-embed everything if you switch models. Evaluate candidates on a "
    "benchmark like MTEB plus your own data before committing."
)
code(
    "# Conceptual comparison (no downloads needed)\n"
    "models_info = [\n"
    "    ('all-MiniLM-L6-v2', 384,  'fast, local, great default'),\n"
    "    ('all-mpnet-base-v2', 768, 'higher quality, slower'),\n"
    "    ('bge-large-en-v1.5', 1024,'top open-source retrieval'),\n"
    "    ('text-embedding-3-small', 1536, 'commercial API'),\n"
    "]\n"
    "print(f\"{'model':24s}{'dims':>6s}  notes\")\n"
    "print('-' * 60)\n"
    "for name, dims, note in models_info:\n"
    "    print(f'{name:24s}{dims:6d}  {note}')"
)

# ----------------------------------------------------------------------------
# 9. Vector space intuition / visualization
# ----------------------------------------------------------------------------
slide("\U0001F9ED 9 — Vector Space Intuition", [
    "Embeddings live in high-dimensional space",
    "Distance ≈ difference in meaning",
    "Related concepts form **clusters**",
    "We use PCA/t-SNE to visualize in 2-D",
    "Geometry is the mental model to keep",
])
script(
    "It helps to *see* the space. Real embeddings have hundreds of dimensions, which we cannot "
    "draw, so we project them down to two dimensions with PCA. When we do, structure appears: "
    "animals cluster together, vehicles cluster elsewhere, and unrelated concepts sit far apart. "
    "Each axis after projection no longer has a clean human label, but the *relative* positions "
    "are meaningful — neighbors share meaning. This geometric picture is the mental model I "
    "want students to carry: retrieval is just ‘find my nearest neighbors in this space,’ "
    "clustering is ‘find dense groups,’ and classification is ‘which region am I "
    "in.’ The plot below makes that concrete."
)
code(
    "from sklearn.decomposition import PCA\n\n"
    "terms = ['cat','dog','kitten','puppy','car','truck','bus','python','java','banana','apple']\n"
    "E = model.encode(terms)\n"
    "pts = PCA(n_components=2).fit_transform(E)\n\n"
    "plt.figure(figsize=(7,5))\n"
    "plt.scatter(pts[:,0], pts[:,1])\n"
    "for (x,y), t in zip(pts, terms):\n"
    "    plt.annotate(t, (x,y), fontsize=11, xytext=(4,4), textcoords='offset points')\n"
    "plt.title('Embeddings projected to 2-D (PCA) — related words cluster')\n"
    "plt.xlabel('PC 1'); plt.ylabel('PC 2'); plt.grid(alpha=0.3)\n"
    "plt.tight_layout(); plt.show()"
)

# ----------------------------------------------------------------------------
# 10. Chunking
# ----------------------------------------------------------------------------
slide("\U0001F4DA 10 — Chunking Documents", [
    "Don’t embed a whole document as one vector",
    "One vector = an **average** of all topics (blurry)",
    "Split into chunks (~100–500 tokens)",
    "Each chunk → its own embedding",
    "Enables precise, passage-level retrieval",
])
script(
    "If you embed an entire document into a single vector, you get the *average* of everything "
    "it discusses — a blurry centroid that matches nothing sharply. The fix is **chunking**: "
    "split the document into smaller passages, typically a few hundred tokens, and embed each one "
    "separately. Now a query about a narrow topic can match the specific passage that covers it, "
    "instead of competing with the whole document’s mixed signal. Chunking is one of the "
    "highest-leverage practical decisions in RAG: too large and retrieval is imprecise; too small "
    "and you lose context. The right size depends on your content and model, and it is worth "
    "tuning empirically."
)
code(
    "def chunk_words(text, size=8):\n"
    "    words = text.split()\n"
    "    return [' '.join(words[i:i+size]) for i in range(0, len(words), size)]\n\n"
    "doc = ('Neural networks are trained with backpropagation. '\n"
    "       'Gradients flow backward to update weights. '\n"
    "       'Embeddings map text into vector space for retrieval.')\n"
    "chunks = chunk_words(doc, size=6)\n"
    "for i, c in enumerate(chunks):\n"
    "    print(f'chunk {i}: {c!r}')\n"
    "print(f'\\n{len(chunks)} chunks -> {len(chunks)} embeddings of dim {model.encode(chunks).shape[1]}')"
)

# ----------------------------------------------------------------------------
# 11. Overlapping chunks
# ----------------------------------------------------------------------------
slide("\U0001F501 11 — Overlapping Chunks", [
    "Add overlap between consecutive chunks",
    "Prevents losing ideas split at boundaries",
    "Typical overlap: 10–20% of chunk size",
    "Improves recall & continuity",
    "Costs a little extra storage",
])
script(
    "A naive split can cut a sentence or idea exactly at a chunk boundary, leaving neither chunk "
    "with the full thought. The remedy is **overlapping windows**: let each chunk repeat the last "
    "few tokens of the previous one. With overlap, a concept that straddles the boundary appears "
    "intact in at least one chunk, so retrieval still finds it. A common setting is 10–20% "
    "overlap. The cost is modest — slightly more chunks and storage — but the recall and "
    "continuity gains are usually worth it. This is a small, easy-to-miss detail that "
    "meaningfully improves real systems, so I always have students implement it explicitly."
)
code(
    "def chunk_overlap(text, size=6, overlap=2):\n"
    "    words = text.split(); out = []; step = size - overlap\n"
    "    for i in range(0, len(words), step):\n"
    "        piece = words[i:i+size]\n"
    "        if piece: out.append(' '.join(piece))\n"
    "        if i + size >= len(words): break\n"
    "    return out\n\n"
    "doc = 'training uses backpropagation to update the network weights efficiently every step'\n"
    "for i, c in enumerate(chunk_overlap(doc, size=6, overlap=2)):\n"
    "    print(f'chunk {i}: {c!r}')\n"
    "print('\\nNote how the last words of each chunk reappear at the start of the next.')"
)

# ----------------------------------------------------------------------------
# 12. Build a corpus index (numpy)
# ----------------------------------------------------------------------------
slide("\U0001F5C3️ 12 — Building a Searchable Index", [
    "Embed every chunk → a matrix [N × dim]",
    "Normalize vectors for fast cosine via dot product",
    "Store alongside the original text",
    "This matrix *is* your knowledge base",
    "Next: search it",
])
script(
    "To search, we first turn our corpus into an index. Concretely, we embed every chunk and "
    "stack the vectors into an N-by-dimension matrix, keeping a parallel list of the original "
    "texts so we can return human-readable results. If we L2-normalize each row, a single matrix "
    "multiplication against a normalized query vector yields all cosine similarities at once — "
    "fast and simple. For a few thousand chunks this brute-force approach is perfectly adequate "
    "and easy to reason about. The matrix we build here is the knowledge base the rest of the "
    "pipeline queries; everything downstream is just ‘compare the query to these rows and "
    "rank.’"
)
code(
    "corpus = [\n"
    "    'The capital of France is Paris.',\n"
    "    'Photosynthesis converts sunlight into chemical energy in plants.',\n"
    "    'Backpropagation trains neural networks by computing gradients.',\n"
    "    'The Great Wall of China is visible as a long stone fortification.',\n"
    "    'Cosine similarity measures the angle between two vectors.',\n"
    "    'Transformers use attention to model relationships between tokens.',\n"
    "]\n"
    "emb = model.encode(corpus, normalize_embeddings=True)\n"
    "print('Index matrix shape:', emb.shape, '(rows = chunks, cols = dims)')\n"
    "print('Row norms (≈1.0 after normalization):', np.round(np.linalg.norm(emb, axis=1), 3))"
)

# ----------------------------------------------------------------------------
# 13. Retrieval
# ----------------------------------------------------------------------------
slide("\U0001F50D 13 — Retrieval (Top-k Search)", [
    "Embed the query with the **same** model",
    "Compute similarity vs every chunk",
    "Return the top-k highest scores",
    "Fast, scalable, **approximate**",
    "Step 1 of the two-stage pipeline",
])
script(
    "Retrieval is the first search stage. We embed the user’s query with the *same* model "
    "used for the corpus, compute its similarity to every stored chunk, and return the top-k "
    "matches. With normalized vectors this is one dot product against the index matrix — "
    "milliseconds for thousands of chunks, and scalable to billions with approximate nearest "
    "neighbor indexes. The crucial property is that retrieval is *fast but approximate*: it casts "
    "a wide, cheap net to find plausibly relevant passages. It does not deeply judge each "
    "candidate — that is the job of the next stage, re-ranking. Watch how the relevant chunk "
    "rises to the top below."
)
code(
    "def retrieve(query, k=3):\n"
    "    q = model.encode(query, normalize_embeddings=True)\n"
    "    scores = emb @ q                      # cosine via dot product\n"
    "    idx = np.argsort(scores)[::-1][:k]\n"
    "    return [(float(scores[i]), corpus[i]) for i in idx]\n\n"
    "query = 'How are neural networks trained?'\n"
    "print('Query:', query, '\\n')\n"
    "for rank, (s, text) in enumerate(retrieve(query), 1):\n"
    "    print(f'{rank}. ({s:.3f}) {text}')"
)

# ----------------------------------------------------------------------------
# 14. Vector databases
# ----------------------------------------------------------------------------
slide("\U0001F5C4️ 14 — Vector Databases & ANN", [
    "Brute force is O(N) per query — fine for thousands",
    "Billions of vectors need **Approximate NN**",
    "Indexes: IVF (clustering), HNSW (graph)",
    "Trade a little accuracy for huge speed",
    "Tools: FAISS, Milvus, Pinecone, pgvector",
])
script(
    "Computing similarity against every vector is linear in corpus size — fine for thousands, "
    "hopeless for billions. Vector databases solve this with **Approximate Nearest Neighbor** "
    "indexes. IVF partitions vectors into clusters and searches only the nearest few; HNSW builds "
    "a navigable small-world graph you can traverse in roughly logarithmic time. Both trade a "
    "sliver of recall for orders-of-magnitude speedups, and both expose knobs to tune that "
    "tradeoff. Production tools — FAISS, Milvus, Pinecone, Weaviate, pgvector — wrap "
    "these algorithms with persistence, metadata filtering, and scaling. The mental model stays "
    "the same as our numpy index; the database just makes nearest-neighbor search fast at scale."
)
code(
    "# FAISS exact index — same results as numpy, but production-grade.\n"
    "# (Falls back to numpy if faiss isn't installed.)\n"
    "try:\n"
    "    import faiss\n"
    "    index = faiss.IndexFlatIP(emb.shape[1])   # inner product = cosine (normalized)\n"
    "    index.add(emb.astype('float32'))\n"
    "    q = model.encode('attention mechanism in transformers',\n"
    "                     normalize_embeddings=True).astype('float32')\n"
    "    D, I = index.search(q.reshape(1, -1), 3)\n"
    "    print('FAISS top-3:')\n"
    "    for score, i in zip(D[0], I[0]):\n"
    "        print(f'  ({score:.3f}) {corpus[i]}')\n"
    "except ImportError:\n"
    "    print('faiss not installed — numpy retrieve() above is the equivalent.')"
)

# ----------------------------------------------------------------------------
# 15. Re-ranking
# ----------------------------------------------------------------------------
slide("\U0001F9E0 15 — Re-ranking", [
    "Refines the retrieved candidate set",
    "**Cross-encoder**: reads query + chunk *together*",
    "Far more accurate than independent embeddings",
    "Slow → apply only to top candidates",
    "Step 2 of the two-stage pipeline",
])
script(
    "Retrieval scores the query and each chunk *independently* — fast, but it can miss "
    "nuance. **Re-ranking** fixes the ordering with a more powerful model. A cross-encoder takes "
    "the query and a candidate chunk *together* as one input and predicts a relevance score, so "
    "it can model fine interactions a single embedding cannot. The price is speed: a cross-encoder "
    "must run once per candidate, so you never run it over the whole corpus — only over the "
    "small top-k that retrieval already surfaced. The pattern is ‘retrieve 50 cheaply, "
    "re-rank to the best 3 carefully.’ Below, watch the re-ranker reorder the candidates and "
    "sharpen the top result."
)
code(
    "from sentence_transformers import CrossEncoder\n"
    "reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')\n\n"
    "query = 'How are neural networks trained?'\n"
    "candidates = [c for _, c in retrieve(query, k=4)]   # from retrieval stage\n"
    "pairs = [(query, c) for c in candidates]\n"
    "scores = reranker.predict(pairs)\n\n"
    "ranked = sorted(zip(scores, candidates), reverse=True)\n"
    "print('Re-ranked results:')\n"
    "for rank, (s, c) in enumerate(ranked, 1):\n"
    "    print(f'{rank}. (rerank={s:6.2f}) {c}')"
)

# ----------------------------------------------------------------------------
# 16. Why two stages
# ----------------------------------------------------------------------------
slide("⚖️ 16 — Why Two Stages?", [
    "Scale vs. accuracy tradeoff",
    "Retrieval = cheap, wide net (recall)",
    "Re-ranking = expensive, precise (precision)",
    "Together: fast *and* accurate",
    "Standard production architecture",
])
script(
    "Why not just run the powerful re-ranker on everything? Cost. A cross-encoder over millions "
    "of documents per query is computationally impossible in real time. So we split the problem to "
    "play each model to its strength. Retrieval is a cheap, high-recall filter: from millions of "
    "chunks it cheaply proposes a few dozen plausible candidates. Re-ranking is an expensive, "
    "high-precision judge: it carefully orders just those candidates. The composition gives us "
    "both scalability and quality — fast where we need breadth, accurate where we need "
    "judgment. This retrieve-then-rerank pattern is the backbone of modern search and RAG, and "
    "recognizing it lets students reason about almost any production system."
)
code(
    "stages = [\n"
    "    ('Corpus',          1_000_000, 'all chunks'),\n"
    "    ('After retrieval',         50, 'cheap bi-encoder, milliseconds'),\n"
    "    ('After re-ranking',         3, 'expensive cross-encoder, on 50 only'),\n"
    "]\n"
    "print(f\"{'stage':18s}{'count':>10s}  method\")\n"
    "print('-'*55)\n"
    "for name, n, how in stages:\n"
    "    print(f'{name:18s}{n:10,d}  {how}')\n"
    "print('\\nFunnel: wide-and-cheap  ->  narrow-and-accurate')"
)

# ----------------------------------------------------------------------------
# 17. Full RAG pipeline
# ----------------------------------------------------------------------------
slide("\U0001F9F1 17 — The Full RAG Pipeline", [
    "1. Chunk + embed corpus (offline)",
    "2. Retrieve top candidates for a query",
    "3. Re-rank to the best few",
    "4. Stuff them into an LLM prompt as **context**",
    "5. LLM generates a **grounded** answer",
])
script(
    "Now we assemble the whole pipeline. Offline, we chunk and embed our corpus into an index. At "
    "query time we retrieve candidate chunks, re-rank them to the most relevant few, and then "
    "*augment* the language model’s prompt by pasting those chunks in as context. The model "
    "answers using that supplied evidence rather than only its parametric memory — this is "
    "the ‘retrieval-augmented’ idea. The payoff is grounded, up-to-date, citable answers "
    "and far fewer hallucinations, because the facts come from your documents. Below we build the "
    "context string a real system would send to the LLM; the final generation call is shown as a "
    "commented template so the notebook stays offline and reproducible."
)
code(
    "def build_rag_context(query, k_retrieve=4, k_final=2):\n"
    "    cands = [c for _, c in retrieve(query, k=k_retrieve)]\n"
    "    scores = reranker.predict([(query, c) for c in cands])\n"
    "    top = [c for _, c in sorted(zip(scores, cands), reverse=True)[:k_final]]\n"
    "    return top\n\n"
    "query = 'Explain how transformers relate tokens to each other.'\n"
    "context = build_rag_context(query)\n\n"
    "prompt = f'''Answer the question using ONLY the context below.\n\n"
    "Context:\n"
    "{chr(10).join(f\"- {c}\" for c in context)}\n\n"
    "Question: {query}\n"
    "Answer:'''\n"
    "print(prompt)\n\n"
    "# --- Generation step (template; needs an API key or local LLM) ---\n"
    "# from anthropic import Anthropic\n"
    "# client = Anthropic(api_key=...)\n"
    "# msg = client.messages.create(model='claude-haiku-4-5-20251001', max_tokens=200,\n"
    "#         messages=[{'role':'user','content': prompt}])\n"
    "# print(msg.content[0].text)"
)

# ----------------------------------------------------------------------------
# 18. Use cases
# ----------------------------------------------------------------------------
slide("\U0001F9EA 18 — Real-World Use Cases", [
    "Semantic search over docs / code / logs",
    "Q&A chatbots grounded in private data",
    "Recommendation & deduplication",
    "Clustering & topic discovery",
    "Security: log triage, threat-intel search",
])
script(
    "Embeddings and RAG show up everywhere. Semantic search lets users find documents, code, or "
    "log lines by meaning instead of keywords. Grounded chatbots answer from a company’s "
    "private knowledge base, with citations. Recommendation systems find ‘similar items,’ "
    "and the same nearest-neighbor logic powers near-duplicate detection. Clustering reveals "
    "latent topics in large corpora without labels. In cybersecurity — directly relevant to "
    "this course — embeddings help triage alerts, search threat intelligence by semantic "
    "similarity, and surface anomalous log entries that don’t match known-benign patterns. "
    "Once students see meaning as geometry, they start spotting these applications on their own."
)
code(
    "examples = ['benign: scheduled nightly backup completed',\n"
    "            'benign: user logged in from office IP',\n"
    "            'malicious: 200 failed SSH logins then a success from a foreign IP']\n"
    "bank = model.encode(examples, normalize_embeddings=True)\n\n"
    "alert = 'repeated failed authentication followed by successful login'\n"
    "q = model.encode(alert, normalize_embeddings=True)\n"
    "scores = bank @ q\n"
    "best = int(np.argmax(scores))\n"
    "print('Incoming alert:', alert)\n"
    "print(f'\\nClosest known pattern ({scores[best]:.3f}):\\n  {examples[best]}')"
)

# ----------------------------------------------------------------------------
# 19. Common mistakes
# ----------------------------------------------------------------------------
slide("\U0001F3AF 19 — Common Mistakes", [
    "Embedding whole documents (no chunking)",
    "No chunk overlap → lost boundary info",
    "Mixing vectors from different models",
    "Skipping re-ranking → mediocre top results",
    "Forgetting to normalize before dot-product cosine",
])
script(
    "Let me consolidate the traps, because students hit the same ones. First, embedding entire "
    "documents instead of chunks — you get blurry averages. Second, chunking with no overlap, "
    "so ideas at boundaries vanish. Third, and most insidious, mixing models: query embeddings "
    "from one model against document embeddings from another live in incompatible spaces and "
    "produce garbage similarities. Fourth, relying on retrieval alone and skipping re-ranking, "
    "which leaves accuracy on the table. Fifth, computing cosine as a dot product without "
    "normalizing first, silently corrupting your scores. None of these throw errors — they "
    "just quietly degrade quality, which is why I make students audit each step explicitly."
)
code(
    "# Demonstration: forgetting normalization changes the ranking math.\n"
    "a = model.encode('how to train a neural network')        # not normalized\n"
    "b = model.encode('neural network training procedure')\n"
    "raw_dot = float(a @ b)\n"
    "true_cos = float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))\n"
    "print(f'Raw dot product (wrong as cosine): {raw_dot:.3f}')\n"
    "print(f'Properly normalized cosine       : {true_cos:.3f}')\n"
    "print('\\nLesson: normalize, or use a cosine function — do not mix them up.')"
)

# ----------------------------------------------------------------------------
# 20. Summary
# ----------------------------------------------------------------------------
slide("✅ 20 — Summary & Key Takeaways", [
    "Embeddings = vectors that encode **meaning**",
    "Different from hashing (identity) & BoW (counts)",
    "Context + attention → modern embeddings",
    "Cosine similarity ranks relevance",
    "Chunk → retrieve → re-rank → generate = **RAG**",
])
script(
    "To wrap up: embeddings turn language into vectors whose geometry encodes meaning, unlike "
    "hashing, which encodes identity, or bag-of-words, which encodes counts. Contextual "
    "transformer models, driven by attention, give us representations that respect ambiguity and "
    "context. Cosine similarity converts those vectors into relevance rankings. To build a real "
    "system we chunk documents with overlap, embed them into an index, retrieve candidates "
    "cheaply, re-rank them precisely, and feed the best passages to an LLM to generate a grounded "
    "answer — that pipeline *is* RAG. Master these building blocks and the failure modes we "
    "covered, and you can design, debug, and reason about virtually any retrieval-augmented AI "
    "system you will encounter."
)
code(
    "print('RAG pipeline in one line:')\n"
    "print('  documents -> chunk -> embed -> [vector DB] -> retrieve -> re-rank -> LLM -> answer')\n"
    "print('\\nYou now understand every arrow in that pipeline. ')"
)

# ----------------------------------------------------------------------------
# Assemble notebook
# ----------------------------------------------------------------------------
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

with open("embedding.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Wrote embedding.ipynb with {len(cells)} cells.")
