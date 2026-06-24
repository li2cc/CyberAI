"""A teaching MCP server exposing SIMULATED cybersecurity tools.

This is a real Model Context Protocol (MCP) server built with the FastMCP API
from the official `mcp` Python SDK. It exposes three tools and one resource that
an MCP client (or an LLM agent) can discover and call.

    Tools:
      - port_scan(target)   : simulated nmap-style port/service scan
      - lookup_cve(service) : look up known CVEs for a service in the local KB
      - list_targets()      : list the demo targets this server knows about
    Resource:
      - kb://cve            : the full CVE knowledge base (Markdown text)

SAFETY / ETHICS
---------------
`port_scan` does NOT touch the network. It returns canned, realistic-looking
output for a few fictional lab hosts so the lecture is reproducible and safe.
Real scanning (e.g., shelling out to `nmap`) is shown in a comment only — and
you must run it ONLY against systems you are explicitly authorized to test.

Run it directly (stdio transport, the MCP default):

    python mcp_server.py

Or let a client spawn it over stdio (see mcp.ipynb / cybersecurity_automation.ipynb).
"""
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# log_level="WARNING" keeps the server quiet so client cell output stays clean.
mcp = FastMCP("cyber-recon", log_level="WARNING")

# --- Simulated environment (safe, offline, fictional lab hosts) --------------
# Each "host" maps to realistic nmap-style service/version banners. Versions are
# chosen so lookup_cve() finds matching entries in cve_knowledge_base.md.
_SIMULATED_HOSTS = {
    "10.0.0.5": [
        "21/tcp   open  ftp      vsftpd 2.3.4",
        "22/tcp   open  ssh      OpenSSH 7.2p2 Ubuntu",
        "80/tcp   open  http     Apache httpd 2.4.49",
    ],
    "10.0.0.8": [
        "139/tcp  open  netbios-ssn Samba smbd 3.5.0",
        "445/tcp  open  microsoft-ds Samba smbd 3.5.0",
        "3306/tcp open  mysql    MySQL 5.5.40",
    ],
    "10.0.0.12": [
        "23/tcp   open  telnet   Linux telnetd",
        "443/tcp  open  ssl/http Apache httpd 2.2.8 (OpenSSL 1.0.1)",
        "6379/tcp open  redis    Redis key-value store 4.0.9",
    ],
}

_KB_PATH = Path(__file__).with_name("cve_knowledge_base.md")


def _load_kb_sections():
    """Parse the CVE knowledge base into {title: full_section_text}."""
    if not _KB_PATH.exists():
        return {}
    text = _KB_PATH.read_text(encoding="utf8")
    sections = {}
    for chunk in text.split("#"):
        chunk = chunk.strip()
        if chunk:
            title = chunk.splitlines()[0].strip()
            sections[title] = chunk
    return sections


@mcp.tool()
def port_scan(target: str) -> str:
    """Run a (simulated) network port scan of a target host and return open
    ports with detected service names and versions, in nmap style.

    SIMULATED: returns canned data for known lab hosts; no packets are sent.
    """
    if target in _SIMULATED_HOSTS:
        lines = _SIMULATED_HOSTS[target]
        header = f"Nmap scan report for {target}\nPORT     STATE SERVICE  VERSION"
        return header + "\n" + "\n".join(lines)
    return (f"Nmap scan report for {target}\n"
            "PORT     STATE SERVICE  VERSION\n"
            "(no open ports in the simulated environment for this host)")

    # --- Real scan (authorized targets ONLY) ---
    # import subprocess
    # return subprocess.run(["nmap", "-sV", target],
    #                       capture_output=True, text=True, timeout=120).stdout


@mcp.tool()
def lookup_cve(service: str) -> str:
    """Look up known vulnerabilities (CVEs) for a service or product name
    (e.g. 'vsftpd 2.3.4', 'Apache 2.4.49', 'Samba', 'telnet') in the local
    knowledge base. Returns the matching entries, or a 'not found' message.
    """
    sections = _load_kb_sections()
    q = service.lower()
    q_tokens = [t for t in q.replace("/", " ").split() if t]
    hits = []
    for title, body in sections.items():
        hay = (title + " " + body).lower()
        # Match if the title is referenced, or several query tokens appear.
        if title.lower() in q or sum(tok in hay for tok in q_tokens) >= 2:
            hits.append(body)
    if hits:
        return "\n\n".join(hits)
    return f"No known CVEs for '{service}' in the local knowledge base."


@mcp.tool()
def list_targets() -> str:
    """List the demo hosts this server can scan (simulated lab environment)."""
    return "Known simulated targets: " + ", ".join(_SIMULATED_HOSTS.keys())


@mcp.resource("kb://cve")
def cve_kb() -> str:
    """The full CVE knowledge base as Markdown text (an MCP *resource*)."""
    return _KB_PATH.read_text(encoding="utf8") if _KB_PATH.exists() else ""


if __name__ == "__main__":
    # Default transport is stdio: the client launches this script as a subprocess
    # and talks to it over stdin/stdout. Use mcp.run(transport="streamable-http")
    # to serve over HTTP instead.
    mcp.run()
