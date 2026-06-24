"""A teaching MCP server for NON-INTRUSIVE web reconnaissance of AUTHORIZED
intentionally-vulnerable websites.

Built with FastMCP from the official `mcp` Python SDK. It exposes read-only web
recon as MCP tools that an agent (or any MCP client) can discover and call:

    Tools:
      fetch_headers(url)          : HTTP response status + headers (a single GET)
      check_security_headers(url) : which standard security headers are missing
      get_robots(url)             : the site's /robots.txt, if any
      lookup_guidance(finding)    : OWASP guidance for a finding (from web_security_kb.md)
    Resource:
      kb://websec                 : the full web-security knowledge base (Markdown)

SAFETY / ETHICS
---------------
Recon is limited to AUTHORIZED targets only: `scanme.nmap.org` (published by the
Nmap Project expressly so people can test scanning tools) and the Acunetix
`vulnweb.com` family (published for security-tool testing). Every tool makes at
most one ordinary HTTP GET — no scanning, fuzzing, or exploitation. If the
network is unavailable, the tools fall back to a clearly-labelled cached sample
so the lecture is reproducible offline. Do NOT point these tools at systems you
are not explicitly authorized to test.

Run it directly (stdio transport, the MCP default):
    python web_recon_server.py
Or let a client spawn it over stdio (see web_pentest_automation.ipynb).
"""
import ssl
import urllib.request
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("web-recon", log_level="WARNING")

# Only these hosts may be contacted. scanme.nmap.org is published by the Nmap
# Project expressly for testing scanning tools; the Acunetix vulnweb family is
# published as a legal target for testing security tools.
ALLOWED_HOSTS = {
    "scanme.nmap.org",
    "testphp.vulnweb.com", "testasp.vulnweb.com",
    "testaspnet.vulnweb.com", "testhtml5.vulnweb.com",
}

# Standard security headers we expect a hardened site to send.
SECURITY_HEADERS = [
    "Strict-Transport-Security", "Content-Security-Policy",
    "X-Frame-Options", "X-Content-Type-Options", "Referrer-Policy",
]

# Representative cached responses (publicly-known characteristics of these
# deliberately-vulnerable demo sites). Used only when the live fetch fails so the
# notebook still runs offline. Values are realistic, not a guaranteed live capture.
_CACHED = {
    "http://scanme.nmap.org": {
        "status": 200,
        "headers": {
            "Server": "Apache/2.4.7 (Ubuntu)",
            "Content-Type": "text/html",
            "Connection": "close",
        },
        "robots": "(no robots.txt — server returned 404)",
    },
    "http://testphp.vulnweb.com": {
        "status": 200,
        "headers": {
            "Server": "nginx/1.19.0",
            "Content-Type": "text/html; charset=UTF-8",
            "Connection": "close",
            "X-Powered-By": "PHP/5.6.40",
        },
        "robots": "(no robots.txt — server returned 404)",
    },
    "http://testasp.vulnweb.com": {
        "status": 200,
        "headers": {
            "Server": "Microsoft-IIS/8.5",
            "Content-Type": "text/html",
            "X-Powered-By": "ASP.NET",
            "X-AspNet-Version": "4.0.30319",
        },
        "robots": "(no robots.txt — server returned 404)",
    },
}

_KB_PATH = Path(__file__).with_name("web_security_kb.md")


def _host_of(url: str) -> str:
    return url.split("://", 1)[-1].split("/", 1)[0].split(":", 1)[0]


def _guard(url: str) -> str:
    """Return '' if the URL is an allowed target, else an error message."""
    host = _host_of(url)
    if host not in ALLOWED_HOSTS:
        return (f"Refused: '{host}' is not in the authorized list "
                f"({', '.join(sorted(ALLOWED_HOSTS))}). Recon only authorized targets.")
    return ""


def _http_get(url: str, timeout: int = 8):
    """One ordinary GET. Returns (status, headers_dict, live, error)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "edu-web-recon/1.0"})
        with urllib.request.urlopen(req, timeout=timeout,
                                    context=ssl.create_default_context()) as r:
            return r.status, dict(r.headers), True, ""
    except Exception as e:                       # offline / blocked -> cached fallback
        c = _CACHED.get(url)
        if c:
            return c["status"], dict(c["headers"]), False, str(e)
        return None, {}, False, str(e)


@mcp.tool()
def fetch_headers(url: str) -> str:
    """Fetch the HTTP response status and headers for an AUTHORIZED url (one GET).
    Returns the status line and each header, plus whether the data is live or cached.
    """
    err = _guard(url)
    if err:
        return err
    status, headers, live, error = _http_get(url)
    tag = "LIVE" if live else f"CACHED (live fetch failed: {error})"
    lines = [f"[{tag}] {url}", f"HTTP status: {status}"]
    lines += [f"{k}: {v}" for k, v in headers.items()]
    return "\n".join(lines)


@mcp.tool()
def check_security_headers(url: str) -> str:
    """Report which standard security headers are MISSING from an authorized url,
    and flag version-disclosing headers and cleartext HTTP. Returns one finding per line.
    """
    err = _guard(url)
    if err:
        return err
    status, headers, live, error = _http_get(url)
    present = {k.lower() for k in headers}
    findings = []
    if url.lower().startswith("http://"):
        findings.append("Cleartext HTTP (no TLS)")
    for h in SECURITY_HEADERS:
        if h.lower() not in present:
            findings.append(f"Missing security header: {h}")
    if "server" in present:
        findings.append(f"Server version disclosure: {headers.get('Server')}")
    xpb = headers.get("X-Powered-By") or headers.get("x-powered-by")
    if xpb:
        eol = " (PHP 5.x is end of life)" if "php/5" in xpb.lower() else ""
        findings.append(f"Technology disclosure: {xpb}{eol}")
    tag = "live" if live else "cached"
    return f"Findings for {url} ({tag}):\n" + "\n".join(f"- {f}" for f in findings)


@mcp.tool()
def get_robots(url: str) -> str:
    """Fetch /robots.txt for an authorized url and return its contents (if any)."""
    err = _guard(url)
    if err:
        return err
    base = url.rstrip("/")
    robots_url = base + "/robots.txt"
    status, _, live, error = _http_get(robots_url)
    if live and status == 200:
        # urlopen gives headers above; for the body do a second minimal GET.
        try:
            req = urllib.request.Request(robots_url, headers={"User-Agent": "edu-web-recon/1.0"})
            with urllib.request.urlopen(req, timeout=8,
                                        context=ssl.create_default_context()) as r:
                return r.read(2000).decode("utf-8", "replace")
        except Exception as e:
            error = str(e)
    cached = _CACHED.get(url, {}).get("robots")
    return cached or f"(could not fetch robots.txt: {error or 'not found'})"


def _load_kb_sections():
    if not _KB_PATH.exists():
        return {}
    text = _KB_PATH.read_text(encoding="utf8")
    out = {}
    for chunk in text.split("#"):
        chunk = chunk.strip()
        if chunk:
            out[chunk.splitlines()[0].strip().lower()] = chunk
    return out


@mcp.tool()
def lookup_guidance(finding: str) -> str:
    """Look up OWASP guidance for a web-security finding (e.g. 'Missing
    Content-Security-Policy', 'cleartext HTTP', 'PHP 5.6') in the local knowledge base.
    """
    sections = _load_kb_sections()
    q = finding.lower()
    q_tokens = [t for t in q.replace("-", " ").replace(":", " ").split() if len(t) > 2]
    best, best_score = None, 0
    for title, body in sections.items():
        score = sum(tok in (title + " " + body).lower() for tok in q_tokens)
        if score > best_score:
            best, best_score = body, score
    return best if best else f"No guidance found for: {finding}"


@mcp.resource("kb://websec")
def websec_kb() -> str:
    """The full web-security knowledge base as Markdown (an MCP *resource*)."""
    return _KB_PATH.read_text(encoding="utf8") if _KB_PATH.exists() else ""


if __name__ == "__main__":
    mcp.run()
