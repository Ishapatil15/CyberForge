"""
CyberForge Challenge & Lab Generator
Generates all 15 authentic static/file challenges, genuine artifacts,
metadata, hints, solutions, and 3 vulnerable local web labs.
"""

import base64
import json
import math
import os
import random
import shutil
import struct
import urllib.parse
import zipfile
import zlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CHALLENGES_DIR = BASE_DIR / "challenges"
SOLUTIONS_DIR = BASE_DIR / "solutions"
WEB_LABS_DIR = BASE_DIR / "web-labs"
UPLOADS_DIR = BASE_DIR / "backend" / "uploads"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


# -------------------------------------------------------------
# 1. CHALLENGE 1 — Hidden Header (Web / Easy)
# -------------------------------------------------------------
def build_hidden_header():
    c_dir = ensure_dir(CHALLENGES_DIR / "web" / "hidden-header")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{h3ad3r_1nspect10n_mast3r}"

    content = (
        "HTTP/1.1 200 OK\r\n"
        "Date: Fri, 02 Oct 2026 06:15:32 GMT\r\n"
        "Server: CyberForge-Internal-Gateway/2.4.1\r\n"
        "Content-Type: application/json; charset=utf-8\r\n"
        "Content-Length: 98\r\n"
        "Connection: keep-alive\r\n"
        "X-CyberForge-Diagnostic-Token: CTF{h3ad3r_1nspect10n_mast3r}\r\n"
        "X-Request-Trace-ID: cf-trace-77491-auth\r\n"
        "Cache-Control: no-store, private\r\n\r\n"
        '{"status":"operational","node":"cluster-west-04","telemetry":"active","auth_state":"verified"}\n'
    )
    (files_dir / "response.txt").write_text(content, encoding="utf-8")

    yaml_content = f"""name: Hidden Header
slug: hidden-header
category: WEB
difficulty: EASY
points: 100
description: |
  A network administrator intercepted a response from an internal staging gateway.
  Inspect the captured HTTP response artifact to discover the diagnostic authentication token.
tags:
  - web
  - http-headers
  - curl
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Inspect all custom HTTP headers beginning with X-."
    penalty: 10
files:
  - response.txt
learning_objective: "Learn how to inspect raw HTTP response headers and identify unintentionally exposed debug tokens."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Hidden Header\n\nAnalyze `response.txt` using curl, devtools, or a text editor to recover the flag.", encoding="utf-8")

    sol = f"""# Solution: Hidden Header

## Objective
Identify the diagnostic header exposed in the HTTP response artifact.

## Steps
1. Download the challenge artifact `response.txt`.
2. Inspect the HTTP headers:
   ```bash
   grep -i "X-CyberForge" response.txt
   ```
3. Locate the header:
   ```http
   X-CyberForge-Diagnostic-Token: {flag}
   ```
4. Submit the flag: `{flag}`.
"""
    (SOLUTIONS_DIR / "hidden-header.md").write_text(sol, encoding="utf-8")
    return {"slug": "hidden-header", "flag": flag, "file": files_dir / "response.txt"}


# -------------------------------------------------------------
# 2. CHALLENGE 2 — Parameter Hunt (Web / Easy-Medium)
# -------------------------------------------------------------
def build_parameter_hunt():
    c_dir = ensure_dir(CHALLENGES_DIR / "web" / "parameter-hunt")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{und0cum3nted_param_leak_892}"

    schema = {
        "openapi": "3.0.1",
        "info": {
            "title": "CyberForge Internal Telemetry API",
            "version": "2.4.0",
            "description": "Internal developer specification. Confidential.",
        },
        "paths": {
            "/api/v2/telemetry/heartbeat": {
                "get": {
                    "summary": "Check node status",
                    "responses": {"200": {"description": "Node healthy"}},
                }
            },
            "/api/v2/analytics/query": {
                "get": {
                    "summary": "Query event streams",
                    "parameters": [
                        {"name": "range", "in": "query", "schema": {"type": "string"}},
                        {"name": "filter", "in": "query", "schema": {"type": "string"}},
                    ],
                    "responses": {"200": {"description": "Query results"}},
                }
            },
            "/api/v2/system/debug": {
                "get": {
                    "summary": "Internal Diagnostics Gateway",
                    "parameters": [
                        {
                            "name": "developer_override",
                            "in": "query",
                            "description": f"Internal bypass key: verify against escrow value {flag}",
                            "required": False,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"200": {"description": "Diagnostic dump"}},
                }
            },
        },
    }
    (files_dir / "api_routes.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    yaml_content = f"""name: Parameter Hunt
slug: parameter-hunt
category: WEB
difficulty: EASY
points: 150
description: |
  A client-side service worker leaked an API endpoint schema.
  Investigate the route definitions to discover an undocumented diagnostic parameter.
tags:
  - web
  - api
  - parameter-discovery
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Search the schema for routes with debug or override parameters."
    penalty: 15
files:
  - api_routes.json
learning_objective: "Learn to audit OpenAPI/Swagger schema dumps to uncover unadvertised administrative parameters."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Parameter Hunt\n\nInspect `api_routes.json` for hidden endpoints or debug parameters.", encoding="utf-8")

    sol = f"""# Solution: Parameter Hunt

## Objective
Uncover an undocumented parameter in the API routes specification.

## Steps
1. Download `api_routes.json`.
2. Search for `debug` or `override`:
   ```bash
   grep -B 2 -A 5 "developer_override" api_routes.json
   ```
3. In `/api/v2/system/debug`, observe the parameter description containing the escrow key:
   `{flag}`
4. Submit `{flag}`.
"""
    (SOLUTIONS_DIR / "parameter-hunt.md").write_text(sol, encoding="utf-8")
    return {"slug": "parameter-hunt", "flag": flag, "file": files_dir / "api_routes.json"}


# -------------------------------------------------------------
# 3. CHALLENGE 3 — Broken Access (Web / Medium)
# -------------------------------------------------------------
def build_broken_access():
    c_dir = ensure_dir(CHALLENGES_DIR / "web" / "broken-access")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{b0la_auth_m1sconf1g_7714}"

    transactions = [
        {
            "id": "tx_101",
            "request": {"method": "GET", "url": "/api/v1/invoices/4091", "headers": {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.tenant_a"}},
            "response": {"status": 200, "body": {"invoice_id": 4091, "amount": 120.50, "client": "Tenant Alpha", "status": "PAID"}},
        },
        {
            "id": "tx_102",
            "request": {"method": "GET", "url": "/api/v1/invoices/4092", "headers": {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.tenant_a"}},
            "response": {"status": 200, "body": {"invoice_id": 4092, "amount": 450.00, "client": "Tenant Alpha", "status": "PENDING"}},
        },
        {
            "id": "tx_103",
            "request": {"method": "GET", "url": "/api/v1/invoices/9999", "headers": {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.tenant_a"}},
            "response": {
                "status": 200,
                "body": {
                    "invoice_id": 9999,
                    "amount": 999999.00,
                    "client": "SuperAdmin Escrow",
                    "admin_escrow_key": flag,
                    "audit_note": "Confidential executive escrow account. Access restricted.",
                },
            },
        },
    ]
    (files_dir / "audit_traffic.json").write_text(json.dumps(transactions, indent=2), encoding="utf-8")

    yaml_content = f"""name: Broken Access
slug: broken-access
category: WEB
difficulty: MEDIUM
points: 200
description: |
  A security analyst captured transaction logs showing a user requesting documents outside their assigned tenancy.
  Analyze the API trace to identify the unauthorized object reference and extract the leaked administrative key.
tags:
  - web
  - bola
  - idor
  - api-security
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Look for invoice IDs that do not belong to Tenant Alpha and inspect the returned JSON response."
    penalty: 20
files:
  - audit_traffic.json
learning_objective: "Understand Broken Object Level Authorization (BOLA) and how missing tenancy checks compromise sensitive objects."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Broken Access\n\nAnalyze `audit_traffic.json` for broken object-level authorization and leaked tokens.", encoding="utf-8")

    sol = f"""# Solution: Broken Access

## Objective
Identify the BOLA transaction and extract the leaked escrow key.

## Steps
1. Download `audit_traffic.json`.
2. Inspect the entries. Transaction `tx_103` uses `tenant_a` credentials to access `invoices/9999`.
3. The response body contains:
   `"admin_escrow_key": "{flag}"`
4. Submit `{flag}`.
"""
    (SOLUTIONS_DIR / "broken-access.md").write_text(sol, encoding="utf-8")
    return {"slug": "broken-access", "flag": flag, "file": files_dir / "audit_traffic.json"}


# -------------------------------------------------------------
# 4. CHALLENGE 4 — Suspicious Traffic (Forensics / Easy)
# -------------------------------------------------------------
def build_suspicious_traffic():
    c_dir = ensure_dir(CHALLENGES_DIR / "forensics" / "suspicious-traffic")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{pcap_fl0w_analyz3d_4421}"

    # Construct standard valid PCAP file
    gh = struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)

    packets = []
    t = 1700000000

    # Packet 1: Normal DNS query
    dns_payload = b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07gateway\x08internal\x00\x00\x01\x00\x01"
    eth1 = b"\x00\x50\x56\xaa\xbb\xcc\x00\x0c\x29\x11\x22\x33\x08\x00"
    ip1 = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + 8 + len(dns_payload), 101, 0, 64, 17, 0, b"\xc0\xa8\x01\x2d", b"\x08\x08\x08\x08")
    udp1 = struct.pack("!HHHH", 52140, 53, 8 + len(dns_payload), 0)
    pkt1 = eth1 + ip1 + udp1 + dns_payload
    packets.append((t, pkt1))

    # Packet 2: Suspicious HTTP POST containing exfiltration
    http_body = f"client_id=wkstn_45&status=sync&data={flag}\n".encode("utf-8")
    http_headers = (
        b"POST /api/telemetry/beacon HTTP/1.1\r\n"
        b"Host: c2-collector.darkcyber.net\r\n"
        b"User-Agent: WinExfilAgent/1.0\r\n"
        b"Content-Type: application/x-www-form-urlencoded\r\n"
        b"Content-Length: " + str(len(http_body)).encode("utf-8") + b"\r\n\r\n"
    )
    http_payload = http_headers + http_body

    eth2 = b"\x00\x50\x56\xaa\xbb\xcc\x00\x0c\x29\x11\x22\x33\x08\x00"
    ip2 = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + 20 + len(http_payload), 102, 0, 64, 6, 0, b"\xc0\xa8\x01\x2d", b"\xca\x00\x71\x59")
    tcp2 = struct.pack("!HHIIBBHHH", 49822, 80, 2000, 1, 0x50, 0x18, 16384, 0, 0)
    pkt2 = eth2 + ip2 + tcp2 + http_payload
    packets.append((t + 2, pkt2))

    # Packet 3: Normal NTP sync
    ntp_payload = b"\x1b" + b"\x00" * 47
    eth3 = b"\x00\x50\x56\xaa\xbb\xcc\x00\x0c\x29\x11\x22\x33\x08\x00"
    ip3 = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20 + 8 + len(ntp_payload), 103, 0, 64, 17, 0, b"\xc0\xa8\x01\x2d", b"\x81\x06\x17\x1c")
    udp3 = struct.pack("!HHHH", 52141, 123, 8 + len(ntp_payload), 0)
    pkt3 = eth3 + ip3 + udp3 + ntp_payload
    packets.append((t + 4, pkt3))

    pcap_data = bytearray(gh)
    for ts, pkt in packets:
        pcap_data.extend(struct.pack("<IIII", ts, 0, len(pkt), len(pkt)))
        pcap_data.extend(pkt)

    (files_dir / "suspicious_traffic.pcap").write_bytes(pcap_data)

    yaml_content = f"""name: Suspicious Traffic
slug: suspicious-traffic
category: FORENSICS
difficulty: EASY
points: 100
description: |
  A network intrusion detection system alerted on beaconing behavior from a workstation.
  Examine the supplied packet capture in Wireshark and extract the exfiltrated flag.
tags:
  - forensics
  - wireshark
  - pcap
  - network-analysis
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Filter by http in Wireshark or follow the TCP stream on port 80."
    penalty: 10
files:
  - suspicious_traffic.pcap
learning_objective: "Learn how to use Wireshark to filter packet streams and reconstruct exfiltrated HTTP payloads."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Suspicious Traffic\n\nAnalyze `suspicious_traffic.pcap` with Wireshark or tshark.", encoding="utf-8")

    sol = f"""# Solution: Suspicious Traffic

## Objective
Reconstruct HTTP beacon payload from packet capture.

## Steps
1. Open `suspicious_traffic.pcap` in Wireshark.
2. Apply display filter: `http`.
3. Right-click the HTTP POST packet and select **Follow -> TCP Stream**.
4. The request body contains:
   `client_id=wkstn_45&status=sync&data={flag}`
5. Submit `{flag}`.
"""
    (SOLUTIONS_DIR / "suspicious-traffic.md").write_text(sol, encoding="utf-8")
    return {"slug": "suspicious-traffic", "flag": flag, "file": files_dir / "suspicious_traffic.pcap"}


# -------------------------------------------------------------
# 5. CHALLENGE 5 — Memory Clue (Forensics / Medium)
# -------------------------------------------------------------
def build_memory_clue():
    c_dir = ensure_dir(CHALLENGES_DIR / "forensics" / "memory-clue")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{m3m0ry_str1ngs_unv31l_993}"

    # Build simulated memory dump with realistic process environment block
    dump = bytearray()
    dump.extend(b"\x00" * 4096)  # Zero page
    dump.extend(b"[ELF-SIMULATED-HEADER]\x00\x02\x01\x01\x00" + b"\x90" * 256)
    dump.extend(b"/usr/lib/x86_64-linux-gnu/libc.so.6\x00ld-linux-x86-64.so.2\x00")
    dump.extend(b"\x00" * 1024)

    # Process env segment
    env_block = (
        b"SHELL=/bin/bash\x00"
        b"USER=deploy_bot\x00"
        b"PWD=/opt/services/vault\x00"
        b"LANG=en_US.UTF-8\x00"
        b"CYBERFORGE_VAULT_TOKEN=" + flag.encode("utf-8") + b"\x00"
        b"VAULT_HOST=10.0.8.25\x00"
        b"LOG_LEVEL=DEBUG\x00"
    )
    dump.extend(env_block)
    dump.extend(b"\x00" * 8192)
    dump.extend(b"Heap memory chunk: 0x7ffd98b0 ... malloc allocator tracking active\x00")
    dump.extend(b"\x00" * 4096)

    (files_dir / "memory_minidump.raw").write_bytes(dump)

    yaml_content = f"""name: Memory Clue
slug: memory-clue
category: FORENSICS
difficulty: MEDIUM
points: 200
description: |
  Investigators dumped the memory space of a suspicious background process.
  Extract the secret vault authentication token preserved in the process environment segment.
tags:
  - forensics
  - memory-forensics
  - strings
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Run strings on the memory dump and search for CYBERFORGE or VAULT."
    penalty: 20
files:
  - memory_minidump.raw
learning_objective: "Learn to perform string and environment extraction on raw process memory images."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Memory Clue\n\nAnalyze `memory_minidump.raw` to locate process environment variables.", encoding="utf-8")

    sol = f"""# Solution: Memory Clue

## Objective
Extract the secret vault token from process memory.

## Steps
1. Download `memory_minidump.raw`.
2. Run strings to search for environment keys:
   ```bash
   strings memory_minidump.raw | grep -i "CYBERFORGE"
   ```
3. Output:
   `CYBERFORGE_VAULT_TOKEN={flag}`
4. Submit `{flag}`.
"""
    (SOLUTIONS_DIR / "memory-clue.md").write_text(sol, encoding="utf-8")
    return {"slug": "memory-clue", "flag": flag, "file": files_dir / "memory_minidump.raw"}


# -------------------------------------------------------------
# 6. CHALLENGE 6 — Incident Logs (Forensics / Easy)
# -------------------------------------------------------------
def build_incident_logs():
    c_dir = ensure_dir(CHALLENGES_DIR / "forensics" / "incident-logs")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{l0g_c0rr3lat10n_d3t3ct3d_512}"
    b64_flag = base64.b64encode(flag.encode("utf-8")).decode("utf-8")

    auth_log = """Oct 02 03:12:01 srv-core sshd[18401]: Failed password for invalid user admin from 203.0.113.88 port 48112 ssh2
Oct 02 03:12:05 srv-core sshd[18403]: Failed password for invalid user root from 203.0.113.88 port 48114 ssh2
Oct 02 03:12:12 srv-core sshd[18408]: Accepted password for svc-deploy from 203.0.113.88 port 48120 ssh2
Oct 02 03:12:13 srv-core systemd-logind[912]: New session 42 of user svc-deploy.
Oct 02 03:15:00 srv-core CRON[18450]: (root) CMD (/usr/local/bin/monitor.sh)
"""

    server_log = """198.51.100.12 - - [02/Oct/2026:03:10:00 +0000] "GET /index.html HTTP/1.1" 200 4521 "-" "Mozilla/5.0"
203.0.113.88 - - [02/Oct/2026:03:13:20 +0000] "POST /admin/tools/runner HTTP/1.1" 200 184 "-" "curl/7.81.0"
198.51.100.12 - - [02/Oct/2026:03:14:15 +0000] "GET /assets/style.css HTTP/1.1" 200 1204 "-" "Mozilla/5.0"
"""

    app_log = f"""[2026-10-02 03:13:20] INFO [RunnerService]: Dispatching command from session_ip=203.0.113.88
[2026-10-02 03:13:21] WARN [RunnerService]: Executing unverified staging script: runner.sh
[2026-10-02 03:13:21] DEBUG [RunnerService]: Payload content: echo {b64_flag} | base64 -d
[2026-10-02 03:13:22] INFO [RunnerService]: Command exited with status 0
"""

    zip_path = files_dir / "incident_logs.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("auth.log", auth_log)
        z.writestr("server.log", server_log)
        z.writestr("application.log", app_log)

    yaml_content = f"""name: Incident Logs
slug: incident-logs
category: FORENSICS
difficulty: EASY
points: 150
description: |
  An unknown actor successfully logged into an internal host and executed a staging command.
  Correlate auth.log, server.log, and application.log to identify the intrusion and decode the payload.
tags:
  - forensics
  - log-analysis
  - incident-response
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Find the attacker IP from the accepted SSH login in auth.log, then check application.log for the payload."
    penalty: 15
files:
  - incident_logs.zip
learning_objective: "Learn to correlate multi-source system logs (authentication, web, application) to reconstruct attack steps."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Incident Logs\n\nExtract and cross-reference `auth.log`, `server.log`, and `application.log`.", encoding="utf-8")

    sol = f"""# Solution: Incident Logs

## Objective
Correlate logs to find attacker IP and decode the executed command payload.

## Steps
1. Unzip `incident_logs.zip`.
2. Inspect `auth.log`: `203.0.113.88` successfully logged in as `svc-deploy`.
3. In `server.log`: `203.0.113.88` called `POST /admin/tools/runner`.
4. In `application.log`:
   `echo {b64_flag} | base64 -d`
5. Decode `{b64_flag}`:
   ```bash
   echo "{b64_flag}" | base64 -d
   ```
6. Output: `{flag}`.
"""
    (SOLUTIONS_DIR / "incident-logs.md").write_text(sol, encoding="utf-8")
    return {"slug": "incident-logs", "flag": flag, "file": zip_path}


# -------------------------------------------------------------
# 7. CHALLENGE 7 — Classic Cipher (Crypto / Easy)
# -------------------------------------------------------------
def build_classic_cipher():
    c_dir = ensure_dir(CHALLENGES_DIR / "crypto" / "classic-cipher")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{v1g3n3r3_c1ph3r_unl0ck3d_881}"
    plaintext = f"THE CLASSIFIED CLEARANCE KEY IS: {flag}"
    key = "FORGE"

    # Vigenere encryption preserving non-letters
    ciphertext = []
    key_idx = 0
    for char in plaintext:
        if char.isalpha():
            shift = ord(key[key_idx % len(key)].upper()) - ord("A")
            base = ord("A") if char.isupper() else ord("a")
            cipher_char = chr((ord(char) - base + shift) % 26 + base)
            ciphertext.append(cipher_char)
            key_idx += 1
        else:
            ciphertext.append(char)
    ciphertext_str = "".join(ciphertext)

    (files_dir / "ciphertext.txt").write_text(
        f"Encrypted Field Dispatch:\n\n{ciphertext_str}\n\n[Cipher Type: Polyalphabetic Substitution, Key Length: 5]\n",
        encoding="utf-8",
    )

    yaml_content = f"""name: Classic Cipher
slug: classic-cipher
category: CRYPTOGRAPHY
difficulty: EASY
points: 100
description: |
  An operational memo was encrypted using a polyalphabetic Vigenère cipher with the keyword FORGE.
  Decrypt the ciphertext to uncover the clearance key.
tags:
  - crypto
  - vigenere
  - classic-cipher
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Use CyberChef or Python to decrypt the Vigenère cipher using key 'FORGE'."
    penalty: 10
files:
  - ciphertext.txt
learning_objective: "Understand classic polyalphabetic substitution ciphers and Vigenère decryption with a known key."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Classic Cipher\n\nDecrypt `ciphertext.txt` with keyword `FORGE`.", encoding="utf-8")

    sol = f"""# Solution: Classic Cipher

## Objective
Decrypt the Vigenère ciphertext using the keyword `FORGE`.

## Steps
1. Open `ciphertext.txt`.
2. Notice the ciphertext: `{ciphertext_str}`.
3. Decrypt using Vigenère with key `FORGE` (e.g. on CyberChef or Python):
4. Recovered message: `{plaintext}`.
5. Submit `{flag}`.
"""
    (SOLUTIONS_DIR / "classic-cipher.md").write_text(sol, encoding="utf-8")
    return {"slug": "classic-cipher", "flag": flag, "file": files_dir / "ciphertext.txt"}


# -------------------------------------------------------------
# 8. CHALLENGE 8 — Weak Key (Crypto / Medium)
# -------------------------------------------------------------
def build_weak_key():
    c_dir = ensure_dir(CHALLENGES_DIR / "crypto" / "weak-key")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{sm4ll_pr1m3s_br3ak_rsa_339}"

    # Fermat factorization setup: close primes
    def is_prime(n, k=25):
        if n < 2: return False
        if n in (2, 3): return True
        if n % 2 == 0: return False
        r, s = 0, n - 1
        while s % 2 == 0:
            r += 1
            s //= 2
        for _ in range(k):
            a = random.randrange(2, n - 1)
            x = pow(a, s, n)
            if x in (1, n - 1): continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1: break
            else:
                return False
        return True

    base = 10**40 + 77
    while not is_prime(base):
        base += 2
    p = base
    q = p + 2
    while not is_prime(q):
        q += 2

    n = p * q
    e = 65537
    m = int.from_bytes(flag.encode("utf-8"), "big")
    c = pow(m, e, n)

    info_content = f"""CYBERFORGE CRYPTOGRAPHIC DIAGNOSTIC DUMP
Algorithm: RSA
Modulus (n): {n}
Public Exponent (e): {e}
Ciphertext (c): {c}

Notice: Security audit flagged prime generation randomness. Key components were generated with minimal difference.
"""
    (files_dir / "challenge_info.txt").write_text(info_content, encoding="utf-8")

    yaml_content = f"""name: Weak Key
slug: weak-key
category: CRYPTOGRAPHY
difficulty: MEDIUM
points: 200
description: |
  A custom RSA key generator produced primes that are dangerously close to each other.
  Use Fermat's factorization method to factorize modulus n and decrypt the flag ciphertext.
tags:
  - crypto
  - rsa
  - fermat-factorization
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Because p and q are close, calculate a = isqrt(n); test if a^2 - n is a square."
    penalty: 20
files:
  - challenge_info.txt
learning_objective: "Learn how small prime separation vulnerabilities permit instant factorization via Fermat's method."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Weak Key\n\nAnalyze `challenge_info.txt` and factorize `n` using Fermat's algorithm.", encoding="utf-8")

    sol = f"""# Solution: Weak Key

## Objective
Factorize the close-prime RSA modulus using Fermat's factorization.

## Python Solver
```python
import math

n = {n}
e = {e}
c = {c}

a = math.isqrt(n)
if a * a < n:
    a += 1

while True:
    b2 = a * a - n
    b = math.isqrt(b2)
    if b * b == b2:
        break
    a += 1

p = a - b
q = a + b
phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = pow(c, d, n)
flag = m.to_bytes((n.bit_length() + 7) // 8, "big").lstrip(b"\\x00").decode()
print("Flag:", flag)
```

## Result
`{flag}`
"""
    (SOLUTIONS_DIR / "weak-key.md").write_text(sol, encoding="utf-8")
    return {"slug": "weak-key", "flag": flag, "file": files_dir / "challenge_info.txt"}


# -------------------------------------------------------------
# 9. CHALLENGE 9 — Encoding Chain (Crypto / Easy)
# -------------------------------------------------------------
def build_encoding_chain():
    c_dir = ensure_dir(CHALLENGES_DIR / "crypto" / "encoding-chain")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{mult1_lay3r_d3c0d1ng_pr0}"

    # Step 1: ROT13
    def rot13(s: str) -> str:
        res = []
        for ch in s:
            if "a" <= ch <= "z":
                res.append(chr((ord(ch) - ord("a") + 13) % 26 + ord("a")))
            elif "A" <= ch <= "Z":
                res.append(chr((ord(ch) - ord("A") + 13) % 26 + ord("A")))
            else:
                res.append(ch)
        return "".join(res)

    step1 = rot13(flag)
    # Step 2: Base64
    step2 = base64.b64encode(step1.encode("utf-8")).decode("utf-8")
    # Step 3: Hex
    step3 = step2.encode("utf-8").hex()
    # Step 4: URL Encode
    step4 = urllib.parse.quote(step3)

    (files_dir / "payload.txt").write_text(f"ENCODED EXFILTRATION STREAM:\n{step4}\n", encoding="utf-8")

    yaml_content = f"""name: Encoding Chain
slug: encoding-chain
category: CRYPTOGRAPHY
difficulty: EASY
points: 120
description: |
  An attacker obfuscated their payload by chaining multiple encoding layers.
  Unwrap the encoding transformations in sequence to discover the plaintext flag.
tags:
  - crypto
  - encoding
  - base64
  - rot13
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Reversal sequence: URL Decode -> Hex to ASCII -> Base64 Decode -> ROT13."
    penalty: 10
files:
  - payload.txt
learning_objective: "Differentiate between encryption and encoding, and practice reversing multi-stage encoding chains."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Encoding Chain\n\nDecode `payload.txt` through all encoding stages.", encoding="utf-8")

    sol = f"""# Solution: Encoding Chain

## Objective
Reverse URL-encoding, Hex, Base64, and ROT13.

## Steps
1. URL decode `{step4}` -> `{step3}`.
2. Hex decode `{step3}` -> `{step2}`.
3. Base64 decode `{step2}` -> `{step1}`.
4. ROT13 decode `{step1}` -> `{flag}`.
5. Submit `{flag}`.
"""
    (SOLUTIONS_DIR / "encoding-chain.md").write_text(sol, encoding="utf-8")
    return {"slug": "encoding-chain", "flag": flag, "file": files_dir / "payload.txt"}


# -------------------------------------------------------------
# 10. CHALLENGE 10 — Digital Footprints (OSINT / Easy)
# -------------------------------------------------------------
def build_digital_footprints():
    c_dir = ensure_dir(CHALLENGES_DIR / "osint" / "digital-footprints")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{f00tpr1nt_c0rr3lat10n_succ3ss_104}"

    web_html = """<!doctype html>
<html>
<head><title>NexusForge Aerospace — Internal Archive</title></head>
<body>
<h1>NexusForge Propulsion Division</h1>
<p>Public engineering portal. For questions contact our lead engineer.</p>
<!-- Staging notes: j_reynolds_99 configured the public mirror backup repository -->
<footer>&copy; 2026 NexusForge Systems</footer>
</body>
</html>
"""

    social_txt = """[NexusSocial Feed - Archived Posts]
@j_reynolds_99 (2026-08-14): Finished migrating our verification scripts to our public gist mirror!
@j_reynolds_99 (2026-08-20): Reminder to team: always check metadata.txt for our commit signature.
"""

    profile_txt = """EMPLOYEE DIRECTORY RECORD:
Name: Jonathan Reynolds
Handle: @j_reynolds_99
Department: Secure Propulsion Systems
Location: Sector 7 Staging
Badge ID: NF-88192
"""

    metadata_txt = f"""DOCUMENT METADATA:
Project: NexusForge Secure Staging
Created-By: j_reynolds_99
Commit-ID: commit_99a810f
Verification-Token: {flag}
Integrity-Checksum: sha256:77fa8819001b22
"""

    zip_path = files_dir / "nexusforge_osint.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("website.html", web_html)
        z.writestr("social_feed.txt", social_txt)
        z.writestr("employee_profile.txt", profile_txt)
        z.writestr("metadata.txt", metadata_txt)

    yaml_content = f"""name: Digital Footprints
slug: digital-footprints
category: OSINT
difficulty: EASY
points: 100
description: |
  Fictional aerospace research organization NexusForge left digital traces across public archives.
  Correlate the website comment, social feed, and project metadata in nexusforge_osint.zip to locate the verification token.
tags:
  - osint
  - correlation
  - metadata
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Find the username in website.html, then check metadata.txt for the verification token."
    penalty: 10
files:
  - nexusforge_osint.zip
learning_objective: "Learn open-source intelligence methodology by correlating usernames, comments, and file metadata."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Digital Footprints\n\nExtract `nexusforge_osint.zip` and correlate developer traces.", encoding="utf-8")

    sol = f"""# Solution: Digital Footprints

## Objective
Correlate web comments and metadata records.

## Steps
1. Unzip `nexusforge_osint.zip`.
2. Notice HTML comment in `website.html`: `j_reynolds_99`.
3. Check `social_feed.txt` confirming `j_reynolds_99`'s notes on `metadata.txt`.
4. Inspect `metadata.txt` to find:
   `Verification-Token: {flag}`
5. Submit `{flag}`.
"""
    (SOLUTIONS_DIR / "digital-footprints.md").write_text(sol, encoding="utf-8")
    return {"slug": "digital-footprints", "flag": flag, "file": zip_path}


# -------------------------------------------------------------
# 11. CHALLENGE 11 — The Forgotten Document (OSINT / Medium)
# -------------------------------------------------------------
def build_forgotten_document():
    c_dir = ensure_dir(CHALLENGES_DIR / "osint" / "the-forgotten-document")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{d0cum3nt_arch1v3_unh1dd3n_782}"

    memo = """MEMORANDUM: DECOMMISSIONING NOTICE
Date: 2026-01-15
From: Infrastructure Architecture Committee
To: Operations Team

All services hosted on legacy-backup.internal have been scheduled for migration.
Note that the DNS CNAME record for legacy-backup.internal points to the underlying hardware asset tag.
The decommissioning escrow flag is retained inside the server asset registry.
"""

    dns = """; BIND internal zone file export
$TTL 86400
@   IN  SOA ns1.internal. hostmaster.internal. ( 2026011501 28800 7200 604800 86400 )
    IN  NS  ns1.internal.

gateway.internal.        IN A     10.0.1.1
db-primary.internal.     IN A     10.0.2.10
legacy-backup.internal.  IN CNAME asset-9941.storage.internal.
auth.internal.           IN A     10.0.1.50
"""

    csv_data = f"""asset_tag,hostname,model,status,assigned_dept,escrow_notes
asset-1002,gw-01,Dell R640,ACTIVE,Networking,"Core edge router"
asset-5521,db-01,Dell R740,ACTIVE,Databases,"Postgres production primary"
asset-9941,backup-cold,HP ProLiant,DECOMMISSIONED,Storage,"Decommission recovery key: {flag}"
asset-8812,app-04,Supermicro,ACTIVE,DevOps,"Microservices node"
"""

    zip_path = files_dir / "audit_records.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("decommission_memo.txt", memo)
        z.writestr("dns_zone.txt", dns)
        z.writestr("server_inventory.csv", csv_data)

    yaml_content = f"""name: The Forgotten Document
slug: the-forgotten-document
category: OSINT
difficulty: MEDIUM
points: 180
description: |
  Corporate audit logs contain records of a retired backup host.
  Correlate the decommission memo, internal DNS zone file, and hardware server inventory in audit_records.zip to recover the escrow key.
tags:
  - osint
  - asset-tracking
  - correlation
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Lookup legacy-backup.internal in dns_zone.txt to find the asset tag, then locate it in server_inventory.csv."
    penalty: 15
files:
  - audit_records.zip
learning_objective: "Learn to cross-reference multiple organizational artifacts (memos, DNS records, inventory spreadsheets) to track decommissioned assets."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# The Forgotten Document\n\nCross-reference `decommission_memo.txt`, `dns_zone.txt`, and `server_inventory.csv`.", encoding="utf-8")

    sol = f"""# Solution: The Forgotten Document

## Objective
Trace the decommissioned asset tag to its escrow notes.

## Steps
1. Unzip `audit_records.zip`.
2. `decommission_memo.txt` directs to `legacy-backup.internal`.
3. In `dns_zone.txt`, `legacy-backup.internal` is a CNAME for `asset-9941.storage.internal`.
4. In `server_inventory.csv`, search for `asset-9941`.
5. The `escrow_notes` field reads:
   `Decommission recovery key: {flag}`
6. Submit `{flag}`.
"""
    (SOLUTIONS_DIR / "the-forgotten-document.md").write_text(sol, encoding="utf-8")
    return {"slug": "the-forgotten-document", "flag": flag, "file": zip_path}


# -------------------------------------------------------------
# 12. CHALLENGE 12 — Crack Me (Reverse / Easy)
# -------------------------------------------------------------
def build_crack_me():
    c_dir = ensure_dir(CHALLENGES_DIR / "reverse" / "crack-me")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{str1ngs_and_x0r_r3v3rs1ng_619}"
    passkey = "CyberForgeKey42"

    # Python standalone script that participants can inspect and run
    py_content = f"""#!/usr/bin/env python3
import sys

# CyberForge Safe CTF CrackMe Challenge
SECRET_XOR = bytes([x ^ 0x5A for x in b"{passkey}"])
FLAG_XOR = bytes([x ^ 0x33 for x in b"{flag}"])

def verify(candidate: str):
    cand_bytes = candidate.encode('utf-8')
    obfuscated = bytes([b ^ 0x5A for b in cand_bytes])
    if obfuscated == SECRET_XOR:
        dec_flag = bytes([b ^ 0x33 for b in FLAG_XOR]).decode('utf-8')
        print(f"[+] Access Granted! Flag: {{dec_flag}}")
        return True
    else:
        print("[-] Access Denied: Invalid passkey.")
        return False

if __name__ == '__main__':
    if len(sys.argv) > 1:
        verify(sys.argv[1])
    else:
        user_input = input("Enter Vault Access Passkey: ")
        verify(user_input)
"""

    zip_path = files_dir / "crackme.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("crackme.py", py_content)
        z.writestr("README_TEST.txt", "Run `python crackme.py` and analyze the verification function.")

    yaml_content = f"""name: Crack Me
slug: crack-me
category: REVERSE_ENGINEERING
difficulty: EASY
points: 150
description: |
  A secure access terminal checks user input against an obfuscated validation sequence.
  Analyze the logic in crackme.zip to recover the correct passkey and reveal the flag.
tags:
  - reverse-engineering
  - static-analysis
  - python-reversing
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Inspect SECRET_XOR in crackme.py or XOR each byte with 0x5A to recover the required key 'CyberForgeKey42'."
    penalty: 15
files:
  - crackme.zip
learning_objective: "Understand basic binary/script reverse engineering and XOR deobfuscation techniques."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Crack Me\n\nReverse engineer the verification routine in `crackme.py`.", encoding="utf-8")

    sol = f"""# Solution: Crack Me

## Objective
Reverse engineer the XOR obfuscation to find the passkey and unlock the flag.

## Steps
1. Unzip `crackme.zip`.
2. Inspect `crackme.py`. The passkey check compares `candidate ^ 0x5A` to `SECRET_XOR`.
3. Recover the key:
   ```python
   secret_xor = bytes([x ^ 0x5A for x in b"{passkey}"])
   key = bytes([b ^ 0x5A for b in secret_xor]).decode()
   print("Key:", key)  # CyberForgeKey42
   ```
4. Run:
   ```bash
   python crackme.py CyberForgeKey42
   ```
5. Output: `[+] Access Granted! Flag: {flag}`.
"""
    (SOLUTIONS_DIR / "crack-me.md").write_text(sol, encoding="utf-8")
    return {"slug": "crack-me", "flag": flag, "file": zip_path}


# -------------------------------------------------------------
# 13. CHALLENGE 13 — Hidden Logic (Reverse / Medium)
# -------------------------------------------------------------
def build_hidden_logic():
    c_dir = ensure_dir(CHALLENGES_DIR / "reverse" / "hidden-logic")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{v4l1dat10n_l0g1c_d3c0d3d_941}"
    serial = "CF-9418"  # 7 chars

    # Transformation: target[i] = (ord(c) ^ 0x37) + i * 3
    targets = [(ord(c) ^ 0x37) + i * 3 for i, c in enumerate(serial)]

    validator_py = f"""#!/usr/bin/env python3
import sys

# Hardware license check algorithm
TARGET_ARRAY = {targets}
FLAG_ENC = {list(flag.encode('utf-8'))}

def validate_license(serial: str) -> bool:
    if len(serial) != len(TARGET_ARRAY):
        return False
    for i, ch in enumerate(serial):
        transformed = (ord(ch) ^ 0x37) + i * 3
        if transformed != TARGET_ARRAY[i]:
            return False
    return True

if __name__ == '__main__':
    inp = sys.argv[1] if len(sys.argv) > 1 else input("Enter Hardware License Serial: ")
    if validate_license(inp):
        print(f"[+] License Validated! Registered Flag: {{bytes(FLAG_ENC).decode('utf-8')}}")
    else:
        print("[-] Invalid Serial Key.")
"""

    zip_path = files_dir / "hidden_logic.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("validator.py", validator_py)
        z.writestr("README.txt", "Reverse the state-machine formula in validator.py to derive the serial.")

    yaml_content = f"""name: Hidden Logic
slug: hidden-logic
category: REVERSE_ENGINEERING
difficulty: MEDIUM
points: 220
description: |
  A hardware validation routine enforces licensing keys using a custom arithmetic state transformation.
  Reverse engineer validator.py in hidden_logic.zip to calculate the valid serial and trigger flag output.
tags:
  - reverse-engineering
  - algorithm-reversal
  - math
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Invert the formula: ord(ch) = (TARGET_ARRAY[i] - i * 3) ^ 0x37."
    penalty: 20
files:
  - hidden_logic.zip
learning_objective: "Learn how to invert linear state transformations and solve serial validation routines."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Hidden Logic\n\nReverse the serial validation formula in `validator.py`.", encoding="utf-8")

    sol = f"""# Solution: Hidden Logic

## Objective
Invert the serial calculation algorithm: `transformed = (ord(ch) ^ 0x37) + i * 3`.

## Solver Script
```python
targets = {targets}
serial = "".join([chr((t - i * 3) ^ 0x37) for i, t in enumerate(targets)])
print("Calculated serial:", serial)  # CF-9418
```

## Running
```bash
python validator.py CF-9418
```
Output:
`[+] License Validated! Registered Flag: {flag}`
"""
    (SOLUTIONS_DIR / "hidden-logic.md").write_text(sol, encoding="utf-8")
    return {"slug": "hidden-logic", "flag": flag, "file": zip_path}


# -------------------------------------------------------------
# 14. CHALLENGE 14 — Image Secret (Stego / Easy)
# -------------------------------------------------------------
def build_image_secret():
    c_dir = ensure_dir(CHALLENGES_DIR / "misc" / "image-secret")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{st3g0_png_chUnk_unc0v3r3d_215}"

    # Build genuine 16x16 PNG with tEXt chunk and appended trailing bytes
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr_data = struct.pack("!IIBBBBB", 16, 16, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data)
    ihdr = struct.pack("!I", len(ihdr_data)) + b"IHDR" + ihdr_data + struct.pack("!I", ihdr_crc)

    # 16x16 image raw cyan pixel data
    raw = b""
    for _ in range(16):
        raw += b"\x00" + b"\x00\xd9\xff" * 16
    idat_data = zlib.compress(raw)
    idat_crc = zlib.crc32(b"IDAT" + idat_data)
    idat = struct.pack("!I", len(idat_data)) + b"IDAT" + idat_data + struct.pack("!I", idat_crc)

    # tEXt chunk
    text_data = f"CyberForgeIntel\x00Flag: {flag}".encode("utf-8")
    text_crc = zlib.crc32(b"tEXt" + text_data)
    text_chunk = struct.pack("!I", len(text_data)) + b"tEXt" + text_data + struct.pack("!I", text_crc)

    # IEND chunk
    iend_crc = zlib.crc32(b"IEND")
    iend = struct.pack("!I", 0) + b"IEND" + struct.pack("!I", iend_crc)

    # Trailing steganographic data appended past PNG end
    trailing = f"\n-- [CYBERFORGE STEGO METADATA STREAM]: {flag} --\n".encode("utf-8")

    png_bytes = sig + ihdr + text_chunk + idat + iend + trailing
    (files_dir / "cyber_artifact.png").write_bytes(png_bytes)

    yaml_content = f"""name: Image Secret
slug: image-secret
category: STEGANOGRAPHY
difficulty: EASY
points: 100
description: |
  A digital reconnaissance image contains intelligence concealed within its metadata chunk and trailing file stream.
  Analyze cyber_artifact.png to extract the hidden flag.
tags:
  - steganography
  - metadata
  - png-chunks
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Use strings or exiftool on cyber_artifact.png to inspect embedded text chunks."
    penalty: 10
files:
  - cyber_artifact.png
learning_objective: "Understand PNG chunk structure (tEXt) and how to identify data appended beyond the IEND marker."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Image Secret\n\nAnalyze `cyber_artifact.png` with `strings` or metadata viewers.", encoding="utf-8")

    sol = f"""# Solution: Image Secret

## Objective
Extract hidden text from PNG chunk and trailing data.

## Steps
1. Download `cyber_artifact.png`.
2. Run strings:
   ```bash
   strings cyber_artifact.png | grep "CTF{{"
   ```
3. Output:
   `Flag: {flag}`
4. Submit `{flag}`.
"""
    (SOLUTIONS_DIR / "image-secret.md").write_text(sol, encoding="utf-8")
    return {"slug": "image-secret", "flag": flag, "file": files_dir / "cyber_artifact.png"}


# -------------------------------------------------------------
# 15. CHALLENGE 15 — Strange File (Misc / Medium)
# -------------------------------------------------------------
def build_strange_file():
    c_dir = ensure_dir(CHALLENGES_DIR / "misc" / "strange-file")
    files_dir = ensure_dir(c_dir / "files")
    flag = "CTF{p0lygl0t_m4g1c_byt3s_f1x3d_608}"

    # Build valid ZIP archive in memory
    import io
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("secret_recovery.txt", f"CONGRATULATIONS!\nRecovered Flag: {flag}\n")
    zip_bytes = bytearray(bio.getvalue())

    # Alter magic bytes from 'PK\x03\x04' (50 4b 03 04) to 'XX\x03\x04' (58 58 03 04)
    zip_bytes[0] = 0x58
    zip_bytes[1] = 0x58

    (files_dir / "mystery.bin").write_bytes(zip_bytes)

    yaml_content = f"""name: Strange File
slug: strange-file
category: MISCELLANEOUS
difficulty: MEDIUM
points: 180
description: |
  Forensics responders recovered a file mystery.bin with a corrupted header.
  Analyze the file format structure in a hex editor, repair the magic bytes, and extract the recovery document.
tags:
  - misc
  - file-signatures
  - magic-bytes
flag_format: "CTF{{...}}"
flag: "{flag}"
hints:
  - text: "Look at bytes 3-4 (\\x03\\x04) and file strings. It is a ZIP file with the first two bytes changed from 'PK' to 'XX'."
    penalty: 15
files:
  - mystery.bin
learning_objective: "Learn how file magic bytes work, and how to identify and repair corrupted archive headers."
published: true
"""
    (c_dir / "challenge.yaml").write_text(yaml_content, encoding="utf-8")
    (c_dir / "README.md").write_text("# Strange File\n\nRepair the magic bytes of `mystery.bin` and extract the contents.", encoding="utf-8")

    sol = f"""# Solution: Strange File

## Objective
Repair the corrupted ZIP magic bytes from `XX\\x03\\x04` back to `PK\\x03\\x04`.

## Steps
1. Inspect `mystery.bin` in a hex editor:
   First 4 bytes are `58 58 03 04`.
2. Notice the presence of file names like `secret_recovery.txt` in the archive directory.
3. Repair the first two bytes to `50 4B` (`PK`).
   Python one-liner:
   ```python
   data = bytearray(open("mystery.bin", "rb").read())
   data[0], data[1] = 0x50, 0x4B
   open("repaired.zip", "wb").write(data)
   ```
4. Extract `repaired.zip` and read `secret_recovery.txt`:
   `Recovered Flag: {flag}`
5. Submit `{flag}`.
"""
    (SOLUTIONS_DIR / "strange-file.md").write_text(sol, encoding="utf-8")
    return {"slug": "strange-file", "flag": flag, "file": files_dir / "mystery.bin"}


# -------------------------------------------------------------
# 3 REAL LOCAL WEB LABS
# -------------------------------------------------------------
def build_web_labs():
    # LAB 1: SQL Injection
    lab1_dir = ensure_dir(WEB_LABS_DIR / "sql-injection")
    lab1_app = ensure_dir(lab1_dir / "app")
    flag1 = "CTF{sqli_un10n_inj3ct10n_pwnd_817}"

    lab1_code = '''from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import sqlite3

app = FastAPI(title="CyberForge Lab 1 — SQL Injection")

# In-memory database initialization
conn = sqlite3.connect(":memory:", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT)")
cur.execute("CREATE TABLE admin_secrets (id INTEGER PRIMARY KEY, secret_name TEXT, flag TEXT)")
cur.execute("INSERT INTO users VALUES (1, 'alice', 'alice_pass_123', 'student')")
cur.execute("INSERT INTO users VALUES (2, 'bob', 'bob_pass_456', 'student')")
cur.execute("INSERT INTO admin_secrets VALUES (1, 'production_vault_flag', '__FLAG1__')")
conn.commit()

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>CyberForge Lab // Student Portal</title>
      <style>
        body { font-family: Inter, sans-serif; background: #070B14; color: #F8FAFC; padding: 2rem; }
        .card { max-width: 600px; margin: 0 auto; background: #111B2E; border: 1px solid #1E293B; border-radius: 8px; padding: 2rem; }
        input { width: 100%; padding: 0.75rem; background: #0D1422; border: 1px solid #1E293B; color: #fff; margin-bottom: 1rem; border-radius: 4px; box-sizing: border-box; }
        button { background: #00D9FF; color: #070B14; font-weight: bold; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; cursor: pointer; }
        .result { margin-top: 1rem; padding: 1rem; background: #0D1422; border: 1px solid #1E293B; border-radius: 4px; }
      </style>
    </head>
    <body>
      <div class="card">
        <h2>CyberForge Student Directory Search</h2>
        <p style="color: #94A3B8;">Search for student records or test your database query interface.</p>
        <form action="/search" method="get">
          <input type="text" name="q" placeholder="Enter student username (e.g. alice)" required />
          <button type="submit">Search Database</button>
        </form>
      </div>
    </body>
    </html>
    """

@app.get("/search", response_class=HTMLResponse)
def search(q: str):
    query = "SELECT id, username, role FROM users WHERE username = '" + q + "'"
    try:
        cur.execute(query)
        rows = cur.fetchall()
        html_rows = "".join([f"<li>ID: {r[0]} | User: {r[1]} | Role: {r[2]}</li>" for r in rows])
        results = f"<ul>{html_rows}</ul>" if rows else "<p>No matching records found.</p>"
    except Exception as e:
        results = f"<p style='color: #EF4444;'>SQL Error: {e}</p>"

    return f"""
    <!doctype html>
    <html lang="en">
    <head><meta charset="utf-8"><title>Search Results</title>
    <style>body {{ font-family: Inter, sans-serif; background: #070B14; color: #F8FAFC; padding: 2rem; }} .card {{ max-width: 600px; margin: 0 auto; background: #111B2E; border: 1px solid #1E293B; padding: 2rem; border-radius: 8px; }} a {{ color: #00D9FF; }}</style>
    </head>
    <body>
      <div class="card">
        <h2>Query Results</h2>
        <p>Executed: <code>{query}</code></p>
        <div style="background: #0D1422; padding: 1rem; border-radius: 4px; margin: 1rem 0;">{results}</div>
        <a href="/">Back to search</a>
      </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
'''.replace("__FLAG1__", flag1)

    (lab1_app / "main.py").write_text(lab1_code, encoding="utf-8")
    (lab1_dir / "Dockerfile").write_text("FROM python:3.12-slim\nWORKDIR /app\nRUN pip install fastapi uvicorn\nCOPY app/ /app/\nCMD [\"python\", \"main.py\"]\n", encoding="utf-8")
    (lab1_dir / "docker-compose.yml").write_text("version: '3.8'\nservices:\n  sqli-lab:\n    build: .\n    ports:\n      - '8011:8011'\n", encoding="utf-8")
    (lab1_dir / "README.md").write_text(f"# Web Lab 1: SQL Injection\n\nInject SQL into `/search?q=` to union-select the secret flag from `admin_secrets`.\nFlag: `{flag1}`\n", encoding="utf-8")

    # LAB 2: IDOR / Access Control
    lab2_dir = ensure_dir(WEB_LABS_DIR / "idor")
    lab2_app = ensure_dir(lab2_dir / "app")
    flag2 = "CTF{1d0r_br0k3n_0bj3ct_auth_449}"

    lab2_code = '''from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="CyberForge Lab 2 — IDOR")

PROFILES = {
    1001: {"name": "Sarah Connor", "role": "Junior Analyst", "email": "sarah@nexus.corp", "notes": "Onboarding completed."},
    1002: {"name": "James Cole", "role": "Security Intern", "email": "james@nexus.corp", "notes": "Assigned to incident review."},
    1337: {"name": "Dr. CyberForge Admin", "role": "Chief Security Architect", "email": "admin@nexus.corp", "notes": "RESTRICTED EXECUTIVE COMPLIANCE RECORD. Vault Flag: __FLAG2__"}
}

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!doctype html>
    <html lang="en">
    <head><meta charset="utf-8"><title>Personnel Directory</title>
    <style>body { font-family: Inter, sans-serif; background: #070B14; color: #F8FAFC; padding: 2rem; } .card { max-width: 600px; margin: 0 auto; background: #111B2E; border: 1px solid #1E293B; border-radius: 8px; padding: 2rem; } a { color: #00D9FF; }</style>
    </head>
    <body>
      <div class="card">
        <h2>Nexus Personnel Directory</h2>
        <p style="color: #94A3B8;">Welcome, Junior Analyst. Select your profile to view personnel records:</p>
        <ul>
          <li><a href="/profile?id=1001">My Profile (ID: 1001)</a></li>
          <li><a href="/profile?id=1002">Teammate Profile (ID: 1002)</a></li>
        </ul>
      </div>
    </body>
    </html>
    """

@app.get("/profile", response_class=HTMLResponse)
def profile(id: int = 1001):
    user = PROFILES.get(id)
    if not user:
        return HTMLResponse("<h3>Profile Not Found</h3><a href='/'>Back</a>", status_code=404)
    name = user['name']
    role = user['role']
    email = user['email']
    notes = user['notes']
    return f"""
    <!doctype html>
    <html lang="en">
    <head><meta charset="utf-8"><title>Personnel Profile</title>
    <style>body {{ font-family: Inter, sans-serif; background: #070B14; color: #F8FAFC; padding: 2rem; }} .card {{ max-width: 600px; margin: 0 auto; background: #111B2E; border: 1px solid #1E293B; border-radius: 8px; padding: 2rem; }} a {{ color: #00D9FF; }}</style>
    </head>
    <body>
      <div class="card">
        <h2>Personnel Record #{id}</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Role:</strong> {role}</p>
        <p><strong>Email:</strong> {email}</p>
        <div style="background: #0D1422; border-left: 4px solid #00D9FF; padding: 1rem; margin-top: 1rem;">
          <strong>Confidential Personnel Notes:</strong><br/>
          {notes}
        </div>
        <p style="margin-top: 1.5rem;"><a href="/">Back to Directory</a></p>
      </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)
'''.replace("__FLAG2__", flag2)

    (lab2_app / "main.py").write_text(lab2_code, encoding="utf-8")
    (lab2_dir / "Dockerfile").write_text("FROM python:3.12-slim\nWORKDIR /app\nRUN pip install fastapi uvicorn\nCOPY app/ /app/\nCMD [\"python\", \"main.py\"]\n", encoding="utf-8")
    (lab2_dir / "docker-compose.yml").write_text("version: '3.8'\nservices:\n  idor-lab:\n    build: .\n    ports:\n      - '8012:8012'\n", encoding="utf-8")
    (lab2_dir / "README.md").write_text(f"# Web Lab 2: IDOR\n\nInspect `/profile?id=` and increment/fuzz ID to find privileged user `1337`.\nFlag: `{flag2}`\n", encoding="utf-8")

    # LAB 3: File Upload
    lab3_dir = ensure_dir(WEB_LABS_DIR / "file-upload")
    lab3_app = ensure_dir(lab3_dir / "app")
    flag3 = "CTF{f1l3_upl0ad_byp4ss_succ3ss_321}"

    lab3_code = '''from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI(title="CyberForge Lab 3 — File Upload")
UPLOAD_DIR = Path("/tmp/cyberforge_lab_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <!doctype html>
    <html lang="en">
    <head><meta charset="utf-8"><title>Secure Report Upload Portal</title>
    <style>body { font-family: Inter, sans-serif; background: #070B14; color: #F8FAFC; padding: 2rem; } .card { max-width: 600px; margin: 0 auto; background: #111B2E; border: 1px solid #1E293B; border-radius: 8px; padding: 2rem; } input { margin: 1rem 0; } button { background: #00D9FF; color: #070B14; font-weight: bold; border: none; padding: 0.75rem 1.5rem; border-radius: 4px; cursor: pointer; } a { color: #00D9FF; }</style>
    </head>
    <body>
      <div class="card">
        <h2>Document Verification & Upload Portal</h2>
        <p style="color: #94A3B8;">Submit an audit report file (.txt, .log) for automated processing.</p>
        <form action="/upload" method="post" enctype="multipart/form-data">
          <input type="file" name="file" required /><br/>
          <button type="submit">Upload Document</button>
        </form>
      </div>
    </body>
    </html>
    """

@app.post("/upload", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    filename = file.filename or "unknown"
    contents = await file.read()
    dest = UPLOAD_DIR / filename
    dest.write_bytes(contents)

    msg = f"File '{filename}' uploaded successfully. Parser status: Processed {len(contents)} bytes."
    flag_box = ""
    if "override" in filename.lower() or "flag" in filename.lower() or b"override" in contents.lower():
        flag_box = "<div style='background: #0D1422; border-left: 4px solid #22C55E; padding: 1rem; margin: 1rem 0;'><strong>Security Diagnostic Override Triggered:</strong><br/>Flag: __FLAG3__</div>"

    return f"""
    <!doctype html>
    <html lang="en">
    <head><meta charset="utf-8"><title>Upload Status</title>
    <style>body {{ font-family: Inter, sans-serif; background: #070B14; color: #F8FAFC; padding: 2rem; }} .card {{ max-width: 600px; margin: 0 auto; background: #111B2E; border: 1px solid #1E293B; border-radius: 8px; padding: 2rem; }} a {{ color: #00D9FF; }}</style>
    </head>
    <body>
      <div class="card">
        <h2>Upload Processed</h2>
        <p>{msg}</p>
        {flag_box}
        <a href="/">Back to upload</a>
      </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8013)
'''.replace("__FLAG3__", flag3)

    (lab3_app / "main.py").write_text(lab3_code, encoding="utf-8")
    (lab3_dir / "Dockerfile").write_text("FROM python:3.12-slim\nWORKDIR /app\nRUN pip install fastapi uvicorn python-multipart\nCOPY app/ /app/\nCMD [\"python\", \"main.py\"]\n", encoding="utf-8")
    (lab3_dir / "docker-compose.yml").write_text("version: '3.8'\nservices:\n  upload-lab:\n    build: .\n    ports:\n      - '8013:8013'\n", encoding="utf-8")
    (lab3_dir / "README.md").write_text(f"# Web Lab 3: File Upload\n\nUpload a file with keyword `override` or `flag` to trigger the backend diagnostic parser.\nFlag: `{flag3}`\n", encoding="utf-8")

    return [
        {"id": "sqli", "name": "Web Lab 1: SQL Injection", "port": 8011, "flag": flag1},
        {"id": "idor", "name": "Web Lab 2: IDOR / Access Control", "port": 8012, "flag": flag2},
        {"id": "upload", "name": "Web Lab 3: File Upload", "port": 8013, "flag": flag3},
    ]


def main():
    ensure_dir(CHALLENGES_DIR)
    ensure_dir(SOLUTIONS_DIR)
    ensure_dir(WEB_LABS_DIR)
    print("=== Generating 15 Static/File Challenges ===")
    challenges = [
        build_hidden_header(),
        build_parameter_hunt(),
        build_broken_access(),
        build_suspicious_traffic(),
        build_memory_clue(),
        build_incident_logs(),
        build_classic_cipher(),
        build_weak_key(),
        build_encoding_chain(),
        build_digital_footprints(),
        build_forgotten_document(),
        build_crack_me(),
        build_hidden_logic(),
        build_image_secret(),
        build_strange_file(),
    ]
    print(f"Generated {len(challenges)} static/file challenges.")

    print("\n=== Generating 3 Real Web Labs ===")
    labs = build_web_labs()
    print(f"Generated {len(labs)} web labs.")

    manifest = {"challenges": challenges, "labs": labs}
    (CHALLENGES_DIR / "manifest.json").write_text(
        json.dumps(
            [
                {"slug": c["slug"], "flag": c["flag"], "file": str(c["file"].name)}
                for c in challenges
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    print("\n=== Generator Complete! Manifest saved to challenges/manifest.json ===")


if __name__ == "__main__":
    main()
