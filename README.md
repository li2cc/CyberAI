# Applied AI for Cybersecurity (IT7075C)

Course materials for **IT7075C — Applied Artificial Intelligence for Cybersecurity**, a graduate
course in the School of Information Technology, University of Cincinnati. Instructor: **Chengcheng
Li**.

This repository holds the hands-on lecture notebooks, runnable examples, and project scaffolding
for the course. It explores how AI — machine learning, LLMs, RAG, and agents — strengthens
**defensive** cybersecurity: identifying vulnerabilities, detecting attacks, modeling threats, and
automating security operations. Every module is built to *run in class*: most notebooks work fully
offline with open-source models, and the steps that call a hosted LLM are guarded so the rest still
runs without a key.

> ⚠️ **Ethics & scope.** All offensive or dual-use activity in this course is restricted to
> isolated lab environments, instructor-approved VMs, student-created apps, approved repositories,
> and public datasets. Never scan, test, or collect data from systems outside the approved scope.
> Keep API keys, credentials, and secrets out of public repositories.

---

## Course learning outcomes

1. Conduct security assessments using AI-enhanced tools and methodologies.
2. Perform threat modeling and map attack surfaces using AI-assisted techniques.
3. Develop AI/ML models to identify cyber risks and support mitigation.
4. Evaluate vulnerabilities and design AI-driven mitigation strategies.
5. Implement AI techniques to automate and improve security operations.
6. Produce clear reports with analysis and actionable recommendations.
7. Apply frameworks for AI-based threat intelligence.
8. Explain and apply principles of Explainable AI in cybersecurity.

---

## Repository map

The course is organized by module. Each module maps to a folder with its own README.

| Module | Topic | Folder |
|--------|-------|--------|
| M1 | Introduction & AI-for-Cyber Landscape | [Introduction_to_AI/](Introduction_to_AI/) |
| M2 | Tools & Environment | *(setup — see this README + each module's setup)* |
| M3 | LLMs on Local & Cloud | [Host_LLMs/](Host_LLMs/) |
| M4 | LLM & RAG Foundations | [RAG/](RAG/) |
| M5 | LangChain | [LangChain/](LangChain/) |
| M6 | LangGraph | *(agent loop covered in [MCP/](MCP/); dedicated material planned)* |
| M7 | Model Context Protocol | [MCP/](MCP/) |
| M8 | Cybersecurity Orchestration | [MCP/](MCP/) — the pentest-automation capstone |
| M9 | Vibe Coding & Web App Vulnerability Analysis | [VideCoding/](VideCoding/) |
| M10+ | AI-Assisted ML for Cybersecurity | [AI_Assisted_ML_for_Cybersecurity/](AI_Assisted_ML_for_Cybersecurity/) |

Most notebooks follow the same teaching format: each topic is three cells — a **slide** (bullets to
project), an **instructor script** (narration to read aloud), and a **runnable code** cell with
clean output.

---

## Modules & detailed topics

The topic lists below reflect what is actually taught in the notebooks and slides in each folder.

### M1 — Introduction & AI-for-Cyber Landscape  ·  [Introduction_to_AI/](Introduction_to_AI/)
A motivating first contact with cloud LLMs on a real security task: classifying a suspicious-login
alert with **Claude and OpenAI side-by-side**.
- The AI-for-cyber landscape; ML vs. LLMs vs. RAG vs. agentic AI as tool categories
- Dual-use concerns, responsible-use expectations, NIST AI RMF / MITRE ATLAS orientation
- A first cloud LLM call: benign-vs-suspicious alert triage (`SimpleAlertClassifier.ipynb`)
- Safe credential handling via a repository-root `.env`

### M3 — LLMs on Local & Cloud  ·  [Host_LLMs/](Host_LLMs/)
Running an open-source LLM **locally on a GPU** and comparing it to the cloud.
- Cloud vs. local vs. Colab-based model experimentation
- Loading open-source models with Hugging Face `transformers`
- GPU inference and generation settings (`max_new_tokens`)
- Capability, privacy, latency, and cost trade-offs

### M4 — LLM & RAG Foundations  ·  [RAG/](RAG/)
How embeddings turn text into meaning, and how to assemble a full retrieval-augmented generation
pipeline. Concepts notebook (`embedding.ipynb`) + worked example (`rag_example.ipynb`).
- What an embedding is; classical vectorization, TF-IDF, embeddings vs. hashing
- Static vs. contextual embeddings; measuring similarity; fixed dimensions
- Choosing an embedding model; vector-space intuition
- Chunking documents and overlapping chunks
- Building a searchable index; top-k retrieval; vector databases & ANN
- Re-ranking and why two stages; the full RAG pipeline
- Real-world use cases and common mistakes
- Worked example: load → connect store → ingest → retrieve → build chain → ask → **RAG vs. pure LLM**

### M5 — LangChain  ·  [LangChain/](LangChain/)
Composing LLM applications from reusable components, then rebuilding RAG "the LangChain way."
- What LangChain is; the **Runnable** interface (`invoke` / `batch` / `stream`)
- Models: LLMs vs. chat models; prompt templates; output parsers
- **LCEL** and the `|` pipe; your first chain
- Chain vs. raw API calls — why a chain helps
- Worked example: a 7-step LangChain RAG pipeline over a cybersecurity KB

### M7 — Model Context Protocol  ·  [MCP/](MCP/)
A standardized way for AI clients to call external tools, with a real, runnable MCP server.
- Why MCP? The M×N integration problem; what MCP is
- Architecture: host, client, server; primitives (tools, resources, prompts)
- The protocol on the wire (JSON-RPC); transports (stdio vs. HTTP)
- Building a server with **FastMCP**; connecting a client to the real server
- AI agents: the **reason → act → observe** loop; agents + MCP as a standard toolbox
- LangChain/LangGraph managing MCP; chain vs. agent vs. agent+MCP
- Security: the risks of giving an LLM tools

### M8 — Cybersecurity Orchestration  ·  [MCP/](MCP/) (capstone notebook)
`cybersecurity_automation.ipynb` builds one pentest assistant **three times** so students feel each
limitation and its fix:
- **Stage 1 — Chains:** `nmap → parse → analyze → report` (the LLM guesses from memory)
- **Stage 2 — RAG:** retrieve real CVEs before analyzing (answers now cite real CVE IDs)
- **Stage 3 — Agent + MCP:** the agent *decides* which tools to call, via the MCP server
- Scope enforcement, simulated tools, and human-oversight themes throughout

### M9 — Vibe Coding & Web App Vulnerability Analysis  ·  [VideCoding/](VideCoding/)
AI-assisted app building and LLM-assisted code review, in a classroom-only scope.
- LLM-assisted application generation and code review
- Hardcoded secrets, weak authentication, input validation, debug exposure
- Introductory OWASP Web Top 10 and OWASP LLM Top 10 concepts
- Manual review vs. AI-assisted review; the planted-vulnerability / `CANARY_` secret exercise

### M10+ — AI-Assisted ML for Cybersecurity  ·  [AI_Assisted_ML_for_Cybersecurity/](AI_Assisted_ML_for_Cybersecurity/)
Traditional ML on cybersecurity datasets, consolidated into one module (foundations → applied →
advanced → deep learning → capstone). See the [module README](AI_Assisted_ML_for_Cybersecurity/)
for the full subtopic breakdown.

---

## Projects

The course is project-centered. Projects are listed here in course-timeline order.

1. **Cybersecurity Framework RAG** — build a RAG assistant over real framework documents (MITRE
   ATT&CK / ATLAS, NIST, OWASP) and evaluate whether answers are grounded in retrieved evidence.
   *(See [RAG/](RAG/).)*
2. **Automated SOC** — design an AI-supported SOC workflow with intake, triage, enrichment,
   recommendations, and a human approval gate.
3. **Vibe Coding Security** — generate a simple web app with planted vulnerabilities and a hidden
   secret, then analyze approved classmates' repositories with LLM-assisted and manual review.
   *(See [VideCoding/](VideCoding/).)*
4. **AI-Assisted ML Capstone** — an end-to-end ML project on an up-to-date cybersecurity dataset
   from [kaggle.com](https://www.kaggle.com/datasets), aiming for high-ranking results with AI
   assistance. *(Tied to [AI_Assisted_ML_for_Cybersecurity/](AI_Assisted_ML_for_Cybersecurity/).)*

> Grading weights and rubrics are maintained in the official syllabus and on Canvas.

---

## Getting started

```bash
# 1. Clone
git clone https://github.com/li2cc/CyberAI.git
cd CyberAI

# 2. (Recommended) create a virtual environment
python -m venv .venv
# Windows:  .venv\Scripts\activate
# macOS/Linux:  source .venv/bin/activate

# 3. Install per-module dependencies (each module has its own requirements)
pip install -r RAG/requirements.txt        # for example
```

### API keys

Cloud-LLM steps read keys from a **`.env` file in the repository root** (already git-ignored):

```
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

Every notebook that needs a key is guarded — if no key is set, that step prints a notice and skips,
so the offline material still runs. **Never commit `.env` or hardcode keys in notebooks.**

### Running notebooks

Open any `.ipynb` in Jupyter, VS Code, or Google Colab and run top to bottom. First runs may
download a small embedding model (~90 MB) or open-source LLM weights and cache them.

---

## Resources

### Course textbooks (from the syllabus)
- **[MLS]** *Machine Learning and Security* — Clarence Chio & David Freeman (O'Reilly)
- **[HOML]** *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow* — Aurélien Géron (O'Reilly)
- **[HOLLM]** *Hands-On Large Language Models* — Jay Alammar & Maarten Grootendorst (O'Reilly)
- **[DLPT]** *Deep Learning with PyTorch* — Eli Stevens, Luca Antiga & Thomas Viehmann (Manning)
- Framework docs: NIST AI RMF, MITRE ATLAS, OWASP Web Top 10, OWASP Top 10 for LLM Applications,
  LangChain, LangGraph, the MCP specification, and the OpenAI / Claude API docs.

### Additional resources
- **Book — *Agentic AI for Cybersecurity: Building Autonomous Defenders and Adversaries*** by Omar
  Santos (Addison-Wesley Professional, May 2026; 368 pp., Intermediate).
  <https://learning.oreilly.com/library/view/agentic-ai-for/9780135589861/>
- **Book — *Artificial Intelligence for Cybersecurity*** by Bojan Kolosnjaji, Huang Xiao, Peng Xu &
  Apostolis Zarras (Packt, October 2024; 364 pp., Beginner–Intermediate).
  <https://learning.oreilly.com/library/view/artificial-intelligence-for/9781805124962/>
- **LinkedIn Learning — *RAG, AI Apps, and AI Agents for Cybersecurity and Networking*** (AI agents
  and agentic RAG for cybersecurity).
  <https://www.linkedin.com/learning/rag-ai-apps-and-ai-agents-for-cybersecurity-and-networking/ai-agents-and-agentic-rag-for-cybersecurity-introduction-26554229?u=2133849>

---

*The instructor reserves the right to update course materials as the class progresses. Official
announcements, assignments, and submission instructions are posted on Canvas.*
