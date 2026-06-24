# Final Project — AI-Orchestrated Penetration Test of Metasploitable 2

**Applied AI for Cybersecurity · Comprehensive Final Project**
**Duration:** 2 weeks · **Team size:** individual or groups of up to 3 (scope scales with size)
**Weight:** the course's comprehensive final project (not a mini-project)

---

## 1. Overview

You will perform a **real, authorized, lab-only** penetration test of a **Metasploitable 2** virtual
machine and build an AI assistant that analyzes the results using the three approaches from this
course — **Chains → RAG → Agents + MCP**. This is the same arc you studied in
`cybersecurity_automation.ipynb`, but on **real scan data** from your own VM, and you must **expand
the retrieval knowledge base(s)** so the assistant can ground the vulnerabilities you actually find.

You develop on top of **`final_project_pentest.ipynb`** (your starting scaffold) and submit a
completed notebook, your expanded RAG file(s), your tool integrations, and a **comprehensive
report** comparing the three automation/orchestration approaches.

### Learning outcomes
By completing this project you will be able to:
- Run and parse a real service/version scan and feed it into an LLM pipeline.
- Explain and demonstrate why RAG beats LLM-memory for security facts — by hitting the gaps yourself.
- **Curate and expand a retrieval knowledge base** to cover newly discovered services and tools.
- Integrate multiple security tools and orchestrate them with an agent over **MCP**.
- Critically compare chains, RAG, and agentic orchestration for automating security work.

---

## 2. Rules of engagement (mandatory)

- Test **only** your own Metasploitable 2 VM in an **isolated lab**. No other host is in scope.
- In VirtualBox, set the VM network to **Host-only** (e.g., `vboxnet0`) or **Internal** — **never**
  Bridged or NAT-to-internet. Metasploitable 2 is intentionally, severely vulnerable.
- Acting outside this scope may violate the CFAA and university policy. Document your scope.
- Keep API keys in `.env` / Colab Secrets — never in code, the notebook, or the report.

---

## 3. Environment setup (Part 0)

1. Download **Metasploitable 2** and import the VM into **VirtualBox**.
2. Set its network adapter to **Host-only**. Boot it; log in with `msfadmin` / `msfadmin`.
3. Find its IP (`ip addr` on the VM, or `nmap -sn 192.168.56.0/24` from your host). Record it.
4. Install **nmap** on your host, plus the additional tools you choose in Part 3.
5. Open `final_project_pentest.ipynb` and install the Python deps in the Setup cell.

---

## 4. Required tasks

### Part 1 — Real recon (replace the simulated target)
- Set `TARGET_IP` to your VM's IP (**TODO 1**).
- Run `nmap -sV` against it (**Stage 0**) and parse the services. Capture the full scan output in the
  notebook (run it, or paste a terminal run into `NMAP_OUTPUT`).

### Part 2 — Reproduce the three stages on real data
- **Stage 1 (Chains):** generate the from-memory report. Note its weaknesses.
- **Stage 2 (RAG):** index the knowledge base and run the **coverage check** — identify which real
  services **ground** and which hit a **GAP** ("No known CVEs found").

### Part 3 — Expand the CVE RAG (**TODO 2** — major deliverable)
- For **every GAP**, research the service and add a `# Title` entry to **`project_cve_kb.md`** (what
  it is, the CVE/CWE, severity, remediation, referenced port).
- Re-run the coverage check and show the **before/after**: GAPs that now ground.
- Run the grounded report and confirm it cites real CVE IDs for your VM's services.

> Metasploitable 2 services you will likely need to add: **UnrealIRCd backdoor (CVE-2010-2075)**,
> **distccd (CVE-2004-2687)**, **Samba 3.0.20 usermap (CVE-2007-2447)**, **PostgreSQL 8.3**,
> **Apache Tomcat default credentials**, **NFS `no_root_squash`**, **r-services (rexec/rlogin/rsh)**,
> **ingreslock backdoor (port 1524)**, **Java RMI (port 1099)**, **ProFTPD**.

### Part 4 — Add tools beyond nmap (**TODO 3** — major deliverable)
- Integrate **at least two** other tools appropriate to Metasploitable 2, e.g. `nikto`, `enum4linux`
  / `smbclient`, `gobuster`, `whatweb`, `searchsploit`.
- Wrap each as a Python function and (recommended) an **MCP tool** in your own copy of
  `mcp_server.py`, modeled on the course server's `@mcp.tool()` functions.
- Run them against the VM and feed their findings into the pipeline.

### Part 5 — Expand the RAG further / add a second KB (**TODO 4** — major deliverable)
- Your new tools produce new finding types (web paths, SMB shares, web-app issues). Add grounding for
  them — preferably in a **second** knowledge base (e.g., `project_web_kb.md`, modeled on the course
  `web_security_kb.md`) with its own vector store, retrieved per finding type.

### Part 6 — Maximize coverage & write the report (**TODO 5**)
- Iterate Stages 0–3 until your report covers **as many of the VM's vulnerabilities as possible**,
  each mapped to a CVE/CWE (and OWASP category for web findings). Note anything you could not ground.
- Write a **comprehensive report** (below).

---

## 5. The report (PDF or Markdown, ~6–10 pages)

Must include:
1. **Methodology & scope** — lab setup, target, tools, rules of engagement.
2. **Findings** — a table of services/vulnerabilities found, each with CVE/CWE, severity, and evidence
   (scan/tool output). Breadth matters.
3. **RAG expansion** — what was missing at first (the GAPs), what entries you added and why, and a
   **before/after** showing improved grounding. Discuss how KB quality drives RAG quality.
4. **Tool & MCP integration** — what you added beyond nmap and how the agent uses it.
5. **Comparative analysis (the heart of the report)** — chains vs. RAG vs. agent+MCP across:
   accuracy/groundedness, build effort, scalability to new tools/services, autonomy, and failure
   modes. Use your own results, not generic claims.
6. **Reflection** — limits you hit, what you'd do with more time, ethical considerations.

---

## 6. Deliverables

- [ ] `final_project_pentest.ipynb` — completed, runnable, with real scan output and all TODOs done.
- [ ] `project_cve_kb.md` — your expanded CVE knowledge base (+ a second KB file if you added one).
- [ ] Tool integrations (and your edited `mcp_server.py` if you extended it).
- [ ] The comprehensive report (PDF/MD).
- [ ] A short **AI-use statement** (which AI tools you used and how).

Group submissions: include a **contributions statement** naming who did what.

---

## 7. Grading rubric (100 points)

| # | Criterion | Pts | Full credit means… |
|---|-----------|-----|--------------------|
| 1 | Lab setup & real recon | 10 | Host-only VM; `TARGET_IP` set; real `nmap -sV` output captured and parsed. |
| 2 | Three stages on real data | 15 | Stage 1, 2, 3 all run on your scan; coverage check identifies GAPs correctly. |
| 3 | **CVE RAG expansion** | 20 | GAPs researched and added to `project_cve_kb.md`; clear before/after grounding; entries accurate (right CVE/CWE, remediation). |
| 4 | **Tools beyond nmap (≥2)** | 15 | ≥2 tools integrated and run; findings flow into the pipeline (MCP-wrapped = full credit). |
| 5 | **Second RAG / further expansion** | 10 | A second KB (or substantial further expansion) grounds the new finding types via its own store. |
| 6 | Vulnerability coverage | 15 | Broad, correct coverage of the VM's vulns, each mapped to CVE/CWE (OWASP for web); gaps acknowledged. |
| 7 | Comprehensive report & **comparative analysis** | 15 | All sections present; the chains-vs-RAG-vs-agent comparison is evidence-based and insightful. |
| — | Professionalism (clarity, reproducibility, AI-use statement) | 5 | Clean, runnable, well-documented; scope and ethics respected. |
| ★ | **Bonus:** live LLM agent autonomously chooses tools (LangGraph + MCP) | +5 | A real model drives ≥2 tool calls end-to-end against your lab. |

**Group scaling:** groups of 2–3 are expected to add **more tools and broader coverage** (e.g., 3–4
tools and a deeper second KB) proportional to team size.

---

## 8. Timeline (2 weeks)

- **Week 1:** lab setup, real recon, three stages, and the CVE-RAG expansion (Parts 0–3).
- **Week 2:** additional tools, second KB, maximize coverage, and write the report (Parts 4–6).

> Tip: commit early and often. Start the RAG expansion as soon as you see your first GAPs — that is
> the largest and most instructive part of the project.
