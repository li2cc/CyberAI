# Module 8 — Cybersecurity Orchestration (Pen-Test)

Students combine what they've learned (agents + MCP + tools) to **orchestrate a controlled,
authorized penetration-testing workflow** — recon → enumerate → look up CVEs → report — with strong
guardrails: scope/allowlists, logging and auditability, and human-in-the-loop approval. The focus is
responsible automation, not unrestricted offensive activity.

**Contents:**
- `cybersecurity_automation.ipynb` — the foundation notebook: one pen-test assistant built three
  ways (chains → RAG → agent + MCP), showing why each step matters.
- **Slides:** `Module8_Orchestration.pptx` (instructor folder) — scope/legality, the recon→triage
  workflow, scope-enforcing tools, allowlisting, logging, ethics.
- **Mini-Project 6** (week 2): an **MCP-orchestrated pen-test** against an isolated **Metasploitable**
  VM, plus an **authorized** online web target (e.g., OWASP Juice Shop self-hosted, PortSwigger Web
  Security Academy, Acunetix `testphp.vulnweb.com`, or a TryHackMe/Hack The Box box). Students extend
  the MCP toolset from Module 7.

> ⚠️ **Ethics & scope:** all activity is confined to isolated lab VMs and explicitly authorized
> targets. Never scan or attack systems outside the approved scope.

> Status: foundation notebook present; the MCP-orchestrated pen-test project is to be built.
