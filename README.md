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

| Module | Topic | Folder | Project |
|--------|-------|--------|---------|
| M1 | Introduction & AI-for-Cyber Landscape | [01_Introduction_to_AI/](01_Introduction_to_AI/) | — |
| M2 | Tools & Environment | *(setup — see this README + each module's setup)* | — |
| M3 | LLMs on Local & Cloud | [02_Host_LLMs/](02_Host_LLMs/) | — |
| M4 | LLM & RAG Foundations | [03_RAG/](03_RAG/) | — |
| M5 | LLM Application Frameworks: LangChain, LangGraph & MCP | [04_LangChain/](04_LangChain/) + [05_MCP/](05_MCP/) | **Project 1 — Cybersecurity Framework Local RAG** |
| M6 | Cybersecurity Orchestration | [05_MCP/](05_MCP/) — the pentest-automation capstone | **Project 2 — Orchestrating a Pen-Test Workflow** |
| M7 | Vibe Coding & Web App Vulnerability Analysis | [06_VibeCoding/](06_VibeCoding/) | **Project 3 — Detect & Harden Vibe-Coded Apps** |
| M8 | AI-Assisted ML for Cybersecurity | [07_AI_Assisted_ML_for_Cybersecurity/](07_AI_Assisted_ML_for_Cybersecurity/) | **Project 4 — AI-Assisted Prediction Models** |

*Modules 5–7 combine the former LangChain, LangGraph, and Model Context Protocol modules into one
LLM-application-frameworks module; the rest are renumbered accordingly.*

Most notebooks follow the same teaching format: each topic is three cells — a **slide** (bullets to
project), an **instructor script** (narration to read aloud), and a **runnable code** cell with
clean output.

---

## Modules & key topics

Key knowledge points per module. Full detail lives in each folder's own README.

### M1 — Introduction & AI-for-Cyber Landscape  ·  [01_Introduction_to_AI/](01_Introduction_to_AI/)
- AI-for-cyber landscape; ML vs. LLMs vs. RAG vs. agentic AI
- Dual-use concerns, responsible use; NIST AI RMF / MITRE ATLAS
- First cloud LLM call: benign-vs-suspicious alert triage (Claude + OpenAI)
- Safe credential handling via `.env`

### M2 — Tools & Environment  ·  *(setup)*
- VS Code, Jupyter, Colab, Git/GitHub, Docker, Kali Linux
- Local LLM tooling (LM Studio / Ollama)
- Python for security data
- Secret handling & repository hygiene

### M3 — LLMs on Local & Cloud  ·  [02_Host_LLMs/](02_Host_LLMs/)
- Cloud vs. local vs. Colab models
- Hugging Face `transformers`; GPU inference (`max_new_tokens`)
- Tokens, context windows, embeddings, inference settings
- Capability, privacy, latency, and cost trade-offs

### M4 — LLM & RAG Foundations  ·  [03_RAG/](03_RAG/)
- Embeddings; classical vectorization, TF-IDF, embeddings vs. hashing
- Static vs. contextual embeddings; similarity; fixed dimensions
- Chunking and overlapping chunks
- Searchable index; top-k retrieval; vector databases & ANN
- Re-ranking; the full RAG pipeline; common mistakes

### M5 — LLM Application Frameworks: LangChain, LangGraph & MCP  ·  [04_LangChain/](04_LangChain/) + [05_MCP/](05_MCP/)
*Combines the former LangChain, LangGraph, and Model Context Protocol modules.*
- LangChain **Runnable** interface (`invoke` / `batch` / `stream`)
- Prompt templates, chat models, output parsers; **LCEL** and the `|` pipe
- Chains vs. raw API calls; RAG "the LangChain way"
- LangGraph: stateful graphs, nodes/edges, conditional routing, human-in-the-loop
- Agents: the **reason → act → observe** loop
- MCP: the M×N problem; host/client/server; tools, resources, prompts
- JSON-RPC; transports (stdio vs. HTTP); **FastMCP** server
- LangChain/LangGraph managing MCP; security of giving an LLM tools

### M6 — Cybersecurity Orchestration  ·  [05_MCP/](05_MCP/)
- One pen-test assistant built three ways: chains → RAG → agent + MCP
- Chains: `nmap → parse → analyze → report`
- RAG: retrieve real CVEs (cite CVE IDs)
- Agent + MCP: the agent decides which tools to call
- Scope enforcement, simulated tools, human oversight

### M7 — Vibe Coding & Web App Vulnerability Analysis  ·  [06_VibeCoding/](06_VibeCoding/)
- LLM-assisted app generation & code review
- Hardcoded secrets, weak auth, input validation, debug exposure
- OWASP Web Top 10 & OWASP LLM Top 10
- Manual vs. AI-assisted review; planted-vuln / `CANARY_` exercise

### M8 — AI-Assisted ML for Cybersecurity  ·  [07_AI_Assisted_ML_for_Cybersecurity/](07_AI_Assisted_ML_for_Cybersecurity/)
- Foundations: clean, feature-engineer, split, data leakage
- Applied detection: confusion matrix, precision/recall/F1, ROC-AUC, thresholds
- Advanced analytics: random forest, gradient boosting, imbalance, clustering, anomaly detection
- Deep learning: PyTorch MLP, training loop, baseline benchmark, overfitting

---

## Projects

The course is project-centered. Each project follows the module that prepares it.

### Project 1 — Cybersecurity Framework Local RAG  *(with M5)*
Build a **fully local, offline** RAG assistant over real cybersecurity framework documents — MITRE
ATT&CK / ATLAS, NIST AI RMF / CSF, or the OWASP Top 10. Ingest and chunk the corpus, embed it with
a local model, and answer questions grounded in retrieved passages with citations — no cloud API.
Using the LangChain + RAG patterns from M4–M5, compare grounded `[RAG]` answers against the model's
own knowledge, test queries with strong and with missing evidence, and report retrieval quality,
failure modes, and limitations. *(See [03_RAG/](03_RAG/) and [04_LangChain/](04_LangChain/).)*

### Project 2 — Orchestrating a Penetration-Test Workflow  *(after M6)*
Compose an agent-driven workflow that orchestrates approved penetration-testing tools through MCP
and LangGraph against an isolated, **authorized** lab VM. The agent reasons about which tool to call
(recon → service enumeration → CVE lookup → report), observes results, and chooses the next step —
with scope allowlists, logging, fail-closed behavior, and a human approval gate. Extend the MCP
server with an additional tool, map automation choices to MITRE ATLAS / NIST AI RMF, and produce a
grounded risk report. *(Builds on [05_MCP/](05_MCP/).)*

### Project 3 — Detecting & Hardening Vibe-Coded Applications  *(after M7)*
Starting from an AI-generated ("vibe-coded") web app, hunt for the vulnerabilities rapid generation
tends to introduce — hardcoded secrets, weak authentication, missing input validation, debug
exposure, injection — using both LLM-assisted and manual review of approved class repositories. Then
**harden** the app: patch each finding, remove leaked `CANARY_` secrets, add validation and safe
defaults, and document before/after evidence. Findings map to the OWASP Web and LLM Top 10.
*(See [06_VibeCoding/](06_VibeCoding/).)*

### Project 4 — AI-Assisted Prediction Models for Cybersecurity Datasets  *(after M8)*
An end-to-end ML project on an up-to-date cybersecurity dataset from
[kaggle.com](https://www.kaggle.com/datasets) (or an approved source such as NSL-KDD, CIC-IDS2017,
or Loghub). Run the full workflow from the AI-Assisted ML module — data preparation and leakage
checks, baseline and ensemble models, imbalance handling, evaluation with SOC-relevant metrics, and
an optional deep-learning comparison — using AI tools as assistants to push for high-ranking results.
Deliver a reproducible notebook, a technical report, and an AI-use statement.
*(Tied to [07_AI_Assisted_ML_for_Cybersecurity/](07_AI_Assisted_ML_for_Cybersecurity/).)*

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
pip install -r 03_RAG/requirements.txt        # for example
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

### Textbooks
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
