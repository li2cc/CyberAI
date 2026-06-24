# Applied AI for Cybersecurity (IT7075C)

Course materials for **IT7075C — Applied Artificial Intelligence for Cybersecurity**, a graduate
course in the School of Information Technology, University of Cincinnati. Instructor: **Chengcheng
Li**.

This repository holds the hands-on lecture notebooks, runnable examples, and project scaffolding
for the course. It explores how AI — LLMs, RAG, agents (LangChain, LangGraph), and the Model
Context Protocol — strengthens **defensive** cybersecurity, and finishes with traditional ML for
security. Every module is built to *run in class*: notebooks work offline where possible, and steps
that call a hosted LLM are guarded so the rest still runs without a key.

> ⚠️ **Ethics & scope.** All offensive or dual-use activity is restricted to isolated lab VMs,
> instructor-approved or explicitly-authorized targets, student-created apps, and public datasets.
> Never scan, test, or collect data from systems outside the approved scope. Keep API keys and
> secrets out of public repositories.

---

## Course structure

Ten modules. The core **RAG → LangChain → LangGraph → MCP** sequence is built from **Omar Santos's**
*Agentic AI for Cybersecurity* (book), his LinkedIn Learning course, and his
[GitHub repo](https://github.com/santosomar/AI-agents-for-cybersecurity); those four are **2-week
modules**. Modules 1–3, Vibe Coding, and the ML capstone are not from Omar's material.

| # | Module | Folder | Source | Wks | Project |
|---|--------|--------|--------|-----|---------|
| 1 | Introduction & AI-for-Cyber Landscape | [01_Introduction_to_AI/](01_Introduction_to_AI/) | — | 1 | — |
| 2 | Tools & Environment | [02_Tools_and_Environment/](02_Tools_and_Environment/) | — | 1 | — |
| 3 | LLMs on Local & Cloud | [03_LLMs_Local_and_Cloud/](03_LLMs_Local_and_Cloud/) | — | — | **MP1 — Compare LLM hosting** |
| 4 | RAG | [04_RAG/](04_RAG/) | Omar | 2 | **MP2 — RAG** |
| 5 | LangChain | [05_LangChain/](05_LangChain/) | Omar | 2 | **MP3 — LangChain RAG** (AI-framework dataset) |
| 6 | LangGraph | [06_LangGraph/](06_LangGraph/) | Omar | 2 | **MP4 — LangGraph agent** |
| 7 | Model Context Protocol (MCP) | [07_MCP/](07_MCP/) | Omar | 2 | **MP5 — MCP server/client** |
| 8 | Cybersecurity Orchestration (Pen-Test) | [08_Cybersecurity_Orchestration/](08_Cybersecurity_Orchestration/) | adapted | — | **MP6 — orchestrated pen-test** |
| 9 | Vibe Coding & Web-App Vuln. Analysis | [09_VibeCoding/](09_VibeCoding/) | — | — | **MP7 — vibe coding** |
| 10 | AI-Assisted ML for Cybersecurity (capstone) | [10_AI_Assisted_ML_for_Cybersecurity/](10_AI_Assisted_ML_for_Cybersecurity/) | — | — | **Capstone — ML on a Kaggle dataset** |

**Each Omar module (4–7) follows the same shape:** one lecture **slide deck** · **two lecture
notebooks** (Part 1 + Part 2) · **one sample-code notebook** · a **week-1 concept assignment** · a
**week-2 mini-project** · one discussion-forum topic. Notebooks use the slide → instructor-script →
runnable-code rhythm.

### The seven mini-projects (+ capstone)
1. **Compare LLM hosting** (Module 3) — API vs. local vs. Colab GPU.
2. **RAG** (Module 4) — a framework-free retrieval pipeline over security docs.
3. **LangChain RAG** (Module 5) — RAG *with* a framework, over a **synthetic cybersecurity-AI-framework
   dataset** (built from a framework named in the CLOs, e.g., NIST AI RMF / MITRE ATLAS / OWASP LLM Top 10).
4. **LangGraph agent** (Module 6) — a stateful, tool-using security agent.
5. **MCP server/client** (Module 7) — implement MCP server + client functions.
6. **Orchestrated pen-test** (Module 8) — MCP-orchestrated recon→triage against an isolated
   Metasploitable VM and an authorized online web target.
7. **Vibe coding** (Module 9) — build, break, and harden an AI-generated web app.
- **Capstone** (Module 10) — an end-to-end ML project on an up-to-date Kaggle cybersecurity dataset.

---

## Course learning outcomes

1. Conduct security assessments using AI-enhanced tools and methodologies.
2. Perform threat modeling and map attack surfaces using AI-assisted techniques.
3. Develop AI/ML models to identify cyber risks and support mitigation.
4. Evaluate vulnerabilities and design AI-driven mitigation strategies.
5. Implement AI techniques to automate and improve security operations.
6. Produce clear reports with analysis and actionable recommendations.
7. Apply frameworks for AI-based threat intelligence (e.g., NIST AI RMF, MITRE ATLAS, OWASP LLM Top 10).
8. Explain and apply principles of Explainable AI in cybersecurity.

---

## Getting started

```bash
git clone https://github.com/li2cc/CyberAI.git
cd CyberAI
python -m venv .venv            # Windows: .venv\Scripts\activate
pip install -r 04_RAG/requirements.txt   # each module has its own requirements
```

Cloud-LLM steps read keys from a **`.env` file in the repo root** (git-ignored):

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

Every notebook that needs a key is guarded — without one, that step prints a notice and skips, so
offline material still runs. Open any `.ipynb` in Jupyter, VS Code, or Google Colab.

---

## Resources

### Textbooks
- **Book — *Agentic AI for Cybersecurity: Building Autonomous Defenders and Adversaries*** by Omar
  Santos (Addison-Wesley, 2026). The RAG/LangChain/LangGraph/MCP modules are built from it.
  <https://learning.oreilly.com/library/view/agentic-ai-for/9780135589861/>
- **Book — *Artificial Intelligence for Cybersecurity*** by Bojan Kolosnjaji et al. (Packt, 2024).
  <https://learning.oreilly.com/library/view/artificial-intelligence-for/9781805124962/>
- **LinkedIn Learning — *RAG, AI Apps, and AI Agents for Cybersecurity and Networking*** (Omar Santos).
  <https://www.linkedin.com/learning/rag-ai-apps-and-ai-agents-for-cybersecurity-and-networking/>
- **Companion repo:** <https://github.com/santosomar/AI-agents-for-cybersecurity>

---

*The instructor may update materials as the course progresses. Announcements, assignments, and
submission instructions are posted on Canvas.*
