# Module 8 — Cybersecurity Orchestration (Pen-Test)

Students combine what they've learned (agents + MCP + tools) to **orchestrate a controlled,
authorized penetration-testing workflow** — recon → enumerate → look up CVEs → report — with strong
guardrails: scope/allowlists, logging and auditability, and human-in-the-loop approval. The focus is
responsible automation, not unrestricted offensive activity.

**Contents:**
- `cybersecurity_automation.ipynb` — the foundation notebook: one pen-test assistant built three
  ways (chains → RAG → agent + MCP) over a **simulated `nmap`** of fictional lab hosts. Uses the
  local `mcp_server.py` (`port_scan`, `lookup_cve`) and `cve_knowledge_base.md`.
- `web_pentest_automation.ipynb` — a **concrete, real-data** companion that runs the same three
  stages over **real, authorized** sites. The default target is **`scanme.nmap.org`** (published by
  the Nmap Project for testing scanning tools); the Acunetix `vulnweb.com` family is also allowed.
  Recon is non-intrusive (one HTTP GET per call) with an offline cached fallback, so it runs anywhere.
    - `web_recon_server.py` — the Stage-3 MCP server: `fetch_headers`, `check_security_headers`,
      `get_robots`, `lookup_guidance`, plus the `kb://websec` resource. Authorization-guarded to the
      allowed hosts only.
    - `web_security_kb.md` — the RAG knowledge base (OWASP categories + remediation) the web
      notebook and server retrieve from.
- **Slides:** `Module8_Orchestration.pptx` (instructor folder) — scope/legality, the recon→triage
  workflow, scope-enforcing tools, allowlisting, logging, ethics.
- **Mini-Project 6** (week 2): an **MCP-orchestrated pen-test** against an isolated **Metasploitable**
  VM, plus an **authorized** online web target (e.g., OWASP Juice Shop self-hosted, PortSwigger Web
  Security Academy, Acunetix `testphp.vulnweb.com`, or a TryHackMe/Hack The Box box). Students extend
  the MCP toolset from Module 7.

> ⚠️ **Ethics & scope:** all activity is confined to isolated lab VMs and explicitly authorized
> targets. Never scan or attack systems outside the approved scope.

> Status: foundation notebook present; the MCP-orchestrated pen-test project is to be built.
