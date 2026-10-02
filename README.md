# CyberForge CTF Platform — Cybersecurity Competition Platform

A modern, high-performance, and secure Capture The Flag (CTF) platform built for students, university teams, and cybersecurity competitions. CyberForge provides server-side flag validation, dynamic competition windows, team collaboration, live leaderboards with deterministic tie-breaking, an administrative control center, 15 complete reproducible file/static challenges, and 3 live interactive web labs.

---

## 1. Brand Identity & Visual Design

* **Brand**: CyberForge
* **Logo**: Custom isometric cube brand emblem with forge flame motif.
* **Typography**: Crisp, humanist **Inter** typography for interface readability, with JetBrains Mono reserved strictly for flags, hashes, code, and terminal logs.
* **Palette**:
  * Primary background: `#070B14` (Deep navy / near-black)
  * Secondary surface: `#0D1422`
  * Card background: `#111B2E` (hover: `#162238`)
  * Primary accent: `#00D9FF` (Electric cyan)
  * Secondary accent: `#7C3AED` (Forge purple)
  * Main text: `#F8FAFC`, Secondary text: `#94A3B8`, Borders: `#1E293B`

---

## 2. Architecture & Technology Stack

```
┌───────────────────────────────────────────┐
│          CyberForge Web Portal            │
│    (React 18, Vite, Tailwind, Inter)      │
└─────────────────────┬─────────────────────┘
                      │ HTTP (REST + Cookies / Bearer)
┌─────────────────────▼─────────────────────┐
│             FastAPI Backend               │
│  (SlowAPI Rate Limiter, Argon2, Jose JWT) │
└──────────┬──────────────────────┬─────────┘
           │ SQLAlchemy 2.0 ORM   │ Process & Container Runner
┌──────────▼──────────────┐ ┌─────▼─────────────────────────┐
│  SQLite / PostgreSQL    │ │    Interactive Web Labs       │
│ (Alembic Schema Engine) │ │ (SQLi: 8011, IDOR: 8012, ...) │
└─────────────────────────┘ └───────────────────────────────┘
```

### Technology Highlights

* **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React icons, React Router v6.
* **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0 (declarative mapped columns), Pydantic v2 & Pydantic Settings.
* **Database**: SQLite (Zero-configuration local development) & PostgreSQL (Production / Docker Compose).
* **Authentication**: HTTP-only secure cookie sessions with fallback support for `Authorization: Bearer <token>` headers; password hashing via **Argon2** (`argon2-cffi`).
* **Flag Validation Engine**: HMAC-SHA256 with server-side pepper and constant-time digest comparison (`hmac.compare_digest`). Plaintext flags are never saved or exposed to the client.
* **Interactive Web Labs**: Built-in process lifecycle manager (`GET /api/labs`, `POST /api/labs/{id}/start`, `stop`, `status`) and containerized deployments via Docker Compose.

---

## 3. Challenge Library (15 Authentic Challenges + 3 Web Labs)

Every challenge contains real artifacts, structured metadata in `challenges/`, and reproducible solutions in `solutions/`:

### Web / HTTP (File Artifacts)
1. **Hidden Header** (Easy, 100 pts) — Inspect raw HTTP response headers (`response.txt`) for diagnostic authorization tokens.
   * Flag: `CTF{h3ad3r_1nspect10n_mast3r}`
2. **Parameter Hunt** (Easy, 150 pts) — Analyze an OpenAPI/Swagger routes dump (`api_routes.json`) to find an undocumented debug override parameter.
   * Flag: `CTF{und0cum3nted_param_leak_892}`
3. **Broken Access** (Medium, 200 pts) — Audit API transaction traces (`audit_traffic.json`) to spot BOLA/IDOR violations leaking executive escrow keys.
   * Flag: `CTF{b0la_auth_m1sconf1g_7714}`

### Digital Forensics
4. **Suspicious Traffic** (Easy, 100 pts) — Examine synthetic PCAP capture (`suspicious_traffic.pcap`) in Wireshark and extract exfiltrated HTTP beaconing data.
   * Flag: `CTF{pcap_fl0w_analyz3d_4421}`
5. **Memory Clue** (Medium, 200 pts) — Extract environment variables and tokens from a raw process memory minidump (`memory_minidump.raw`).
   * Flag: `CTF{m3m0ry_str1ngs_unv31l_993}`
6. **Incident Logs** (Easy, 150 pts) — Correlate `auth.log`, `server.log`, and `application.log` inside `incident_logs.zip` to trace an intruder and decode their payload.
   * Flag: `CTF{l0g_c0rr3lat10n_d3t3ct3d_512}`

### Cryptography
7. **Classic Cipher** (Easy, 100 pts) — Decrypt a polyalphabetic Vigenère ciphertext (`ciphertext.txt`) encrypted with keyword `FORGE`.
   * Flag: `CTF{v1g3n3r3_c1ph3r_unl0ck3d_881}`
8. **Weak Key** (Medium, 200 pts) — Factorize an RSA modulus $n$ generated with dangerously close primes using Fermat's factorization (`challenge_info.txt`).
   * Flag: `CTF{sm4ll_pr1m3s_br3ak_rsa_339}`
9. **Encoding Chain** (Easy, 120 pts) — Reverse a four-layer stacked encoding pipeline: URL Decode $\rightarrow$ Hex $\rightarrow$ Base64 $\rightarrow$ ROT13 (`payload.txt`).
   * Flag: `CTF{mult1_lay3r_d3c0d1ng_pr0}`

### Open Source Intelligence (OSINT)
10. **Digital Footprints** (Easy, 100 pts) — Correlate HTML comments, social posts, and project metadata in `nexusforge_osint.zip` to recover an engineer's verification token.
    * Flag: `CTF{f00tpr1nt_c0rr3lat10n_succ3ss_104}`
11. **The Forgotten Document** (Medium, 180 pts) — Cross-reference a decommission memo, internal DNS zone file, and hardware server inventory in `audit_records.zip`.
    * Flag: `CTF{d0cum3nt_arch1v3_unh1dd3n_782}`

### Reverse Engineering
12. **Crack Me** (Easy, 150 pts) — Perform static analysis and XOR deobfuscation on `crackme.py` in `crackme.zip` to determine the required passkey (`CyberForgeKey42`).
    * Flag: `CTF{str1ngs_and_x0r_r3v3rs1ng_619}`
13. **Hidden Logic** (Medium, 220 pts) — Invert a proprietary state-machine validation algorithm in `validator.py` (`hidden_logic.zip`) to calculate the valid serial (`CF-9418`).
    * Flag: `CTF{v4l1dat10n_l0g1c_d3c0d3d_941}`

### Steganography & Miscellaneous
14. **Image Secret** (Easy, 100 pts) — Extract intelligence hidden within custom PNG `tEXt` chunks and trailing bytes appended after `IEND` (`cyber_artifact.png`).
    * Flag: `CTF{st3g0_png_chUnk_unc0v3r3d_215}`
15. **Strange File** (Medium, 180 pts) — Identify altered ZIP magic bytes (`XX\x03\x04` $\rightarrow$ `PK\x03\x04`), repair `mystery.bin`, and extract the recovery flag.
    * Flag: `CTF{p0lygl0t_m4g1c_byt3s_f1x3d_608}`

### Interactive Web Labs
16. **Web Lab 1: SQL Injection** (Easy, 150 pts, Port 8011) — Interactive student grades portal with vulnerable search parameters.
    * Flag: `CTF{sqli_un10n_inj3ct10n_pwnd_817}`
17. **Web Lab 2: IDOR / Access Control** (Medium, 200 pts, Port 8012) — Personnel records viewer with unauthenticated resource ID enumeration.
    * Flag: `CTF{1d0r_br0k3n_0bj3ct_auth_449}`
18. **Web Lab 3: File Upload Bypass** (Medium, 200 pts, Port 8013) — Document uploader with filter override trigger.
    * Flag: `CTF{f1l3_upl0ad_byp4ss_succ3ss_321}`

---

## 4. Quick Start & Execution

### Prerequisites
* Python 3.11+
* Node.js 18+

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
python -m app.seed
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev -- --host
```

Open `http://localhost:5173` in your browser.

---

## 5. Seed Accounts & Credentials

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `ChangeMeAdmin!23` | Control center, challenge editor, file upload, lab manager |
| **Challenge Author** | `author` | `AuthorPass!23` | Challenge draft review & authoring |
| **Student Operator** | `isha` | `PlayerPass!23` | Player account in active competition & team "Cyber Wolves" |
| **Student Operator** | `rahul` | `PlayerPass!23` | Player account in team "Cyber Wolves" |

---

## 6. Running Automated Tests

Run all 20 backend test suites (including automated challenge solvers and web lab lifecycles):
```bash
cd backend
pytest -v
```

Run frontend unit tests and typecheck:
```bash
cd frontend
npm run test -- --run
npm run build
```
