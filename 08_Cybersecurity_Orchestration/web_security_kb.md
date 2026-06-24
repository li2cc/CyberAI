# Missing Strict-Transport-Security (HSTS) header
OWASP A05:2021 – Security Misconfiguration (also relates to A02 Cryptographic Failures).
The HTTP Strict-Transport-Security header tells browsers to only ever contact the site over
HTTPS, preventing protocol-downgrade and SSL-stripping man-in-the-middle attacks. When it is
absent, an attacker on the network can force a victim onto plaintext HTTP and intercept traffic.
Detection: the response has no `Strict-Transport-Security` header.
Remediation: send `Strict-Transport-Security: max-age=31536000; includeSubDomains` over HTTPS, and
redirect all HTTP traffic to HTTPS. Reference: OWASP Secure Headers Project.

# Missing Content-Security-Policy (CSP) header
OWASP A05:2021 – Security Misconfiguration; a key defense-in-depth control against A03 Injection
(Cross-Site Scripting). A Content-Security-Policy restricts which sources of scripts, styles, and
other resources the browser will load, so that even if an attacker injects markup, the malicious
script is blocked from executing. Detection: the response has no `Content-Security-Policy` header.
Remediation: define a restrictive policy such as `Content-Security-Policy: default-src 'self';
object-src 'none'; frame-ancestors 'none'` and tighten it per page. Reference: OWASP XSS Prevention.

# Missing X-Frame-Options header (clickjacking)
OWASP A05:2021 – Security Misconfiguration. Without `X-Frame-Options` (or a CSP `frame-ancestors`
directive), the page can be embedded in an attacker's hidden iframe and used for clickjacking —
tricking a logged-in user into clicking controls they cannot see. Detection: no `X-Frame-Options`
header and no `frame-ancestors` in CSP. Remediation: send `X-Frame-Options: DENY` (or `SAMEORIGIN`)
and/or `Content-Security-Policy: frame-ancestors 'none'`. Reference: OWASP Clickjacking Defense.

# Missing X-Content-Type-Options header (MIME sniffing)
OWASP A05:2021 – Security Misconfiguration. When `X-Content-Type-Options: nosniff` is absent, some
browsers will "sniff" a response body and execute it as a different content type than declared —
for example treating an uploaded text file as JavaScript. Detection: no `X-Content-Type-Options`
header. Remediation: always send `X-Content-Type-Options: nosniff`. Reference: OWASP Secure Headers.

# Server and technology version disclosure
OWASP A05:2021 – Security Misconfiguration (information leakage). Headers such as `Server`,
`X-Powered-By`, `X-AspNet-Version`, and `X-Generator` reveal the exact web server, language, and
framework versions. This lets an attacker look up version-specific exploits and skip the
fingerprinting step. Detection: a `Server` or `X-Powered-By` header containing a product version.
Remediation: suppress or genericize these headers (e.g. nginx `server_tokens off;`, remove
`X-Powered-By`). Reference: OWASP Testing Guide – Fingerprint Web Server.

# Outdated PHP (end of life)
OWASP A06:2021 – Vulnerable and Outdated Components. PHP 5.x reached end of life on 2018-12-31 and
receives no security patches; PHP 5.6 in particular has numerous known CVEs in the interpreter and
bundled extensions. Running it exposes the application to publicly documented, unpatched flaws.
Detection: `X-Powered-By: PHP/5.x` (or a 5.x banner). Remediation: upgrade to a supported PHP
release (8.x), and subscribe to vulnerability feeds for all components. Reference: php.net
supported versions; OWASP A06.

# Cleartext HTTP without TLS
OWASP A02:2021 – Cryptographic Failures. Serving the site over `http://` rather than `https://`
means credentials, session cookies, and form data travel in plaintext and can be read or modified
by anyone on the network path. Detection: the URL scheme is `http` and/or no redirect to HTTPS.
Remediation: obtain a TLS certificate, serve everything over HTTPS, redirect HTTP to HTTPS, and add
HSTS. Reference: OWASP Transport Layer Security Cheat Sheet.

# SQL Injection
OWASP A03:2021 – Injection. When user input is concatenated into SQL queries without
parameterization, an attacker can alter the query to read or modify the database, bypass
authentication, or extract every record. The Acunetix `testphp.vulnweb.com` demo is intentionally
vulnerable in parameters such as `artist`, `cat`, and the login form. Detection: error-based or
boolean/time-based probes on parameters (manual or with a scanner) — only on authorized targets.
Remediation: use parameterized queries / prepared statements and least-privilege DB accounts.
Reference: OWASP SQL Injection Prevention Cheat Sheet.

# Cross-Site Scripting (XSS)
OWASP A03:2021 – Injection. If the application reflects or stores user input in a page without
output-encoding, an attacker can inject script that runs in other users' browsers to steal sessions
or perform actions as the victim. Intentionally vulnerable demo apps like the vulnweb family expose
reflected XSS in search and query parameters. Detection: input is echoed into the response
unencoded. Remediation: context-aware output encoding, input validation, and a strong CSP.
Reference: OWASP XSS Prevention Cheat Sheet.

# Directory and resource exposure via robots.txt
OWASP A05:2021 – Security Misconfiguration. A `robots.txt` file that lists `Disallow` paths can
unintentionally advertise sensitive directories (admin panels, backups) to an attacker, who reads
it precisely to find them. Detection: fetch `/robots.txt` and review disallowed paths. Remediation:
do not rely on robots.txt for security; protect sensitive paths with authentication and remove
references to them. Reference: OWASP Testing Guide – Review Webserver Metafiles.
