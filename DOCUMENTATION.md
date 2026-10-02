# CyberForge CTF Platform — Comprehensive Technical Documentation

## Executive Overview
**CyberForge** is an enterprise-grade, student-focused Capture The Flag (CTF) cybersecurity platform. Designed with a modern, high-contrast, cybersecurity aesthetic, it features real server-side HMAC flag verification, 15 complete static/file challenges across 6 core disciplines, 3 live interactive web labs, team competition scoring, and an administrative command center.

---

## 1. System Access & Authentication Credentials

The platform is pre-seeded with distinct user roles. Plaintext flags and administration capabilities are strictly isolated on the backend.

### Standard Seed Accounts

| Role | Username | Password | Email | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `ChangeMeAdmin!23` | `admin@local.ctf` | Full platform control: challenge creator, hint/flag manager, file uploader, user/team moderating, lab lifecycle controller. |
| **Challenge Author** | `author` | `AuthorPass!23` | `author@local.ctf` | Create, draft, and edit challenges and hint contents without full user administrative rights. |
| **Student Operator** | `isha` | `PlayerPass!23` | `isha@local.ctf` | Player account enrolled in active competition *"Cyber Warfare 2026"* and Captain of team *"Cyber Wolves"*. |
| **Student Operator** | `rahul` | `PlayerPass!23` | `rahul@local.ctf` | Player account enrolled in competition & member of team *"Cyber Wolves"*. |
| **Student Operator** | `ananya` | `PlayerPass!23` | `ananya@local.ctf` | Player account & member of team *"Cyber Wolves"*. |
| **Student Operator** | `akash` | `PlayerPass!23` | `akash@local.ctf` | Independent student operator account for practice solving. |

> [!NOTE]
> Self-registration is enabled for all new players via the `/register` portal. Registered users receive the standard `USER` role. User promotion to `ADMIN` or `CHALLENGE_AUTHOR` can only be performed by an existing administrator via the Admin Panel (`/admin/users`).

---

## 2. Architecture & Tech Stack

```
┌────────────────────────────────────────────────────────┐
│            CyberForge Frontend (React + Vite)          │
│       Tailwind CSS, Inter Typography, Lucide Icons     │
└───────────────────────────┬────────────────────────────┘
                            │ REST API (JSON / Multipart)
                            │ Session Cookies & Bearer JWT
┌───────────────────────────▼────────────────────────────┐
│            FastAPI Backend Application                 │
│      SlowAPI Rate Limiter, Argon2, HMAC Pepper         │
└─────────────┬────────────────────────────┬─────────────┘
              │ SQLAlchemy 2.0 ORM         │ Process Lifecycle
┌─────────────▼──────────────┐ ┌───────────▼─────────────┐
│    Database Storage        │ │  Interactive Web Labs   │
│  SQLite (ctf.db) / Postgres│ │ (Ports 8011, 8012, 8013)│
└────────────────────────────┘ └─────────────────────────┘
```

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, React Router v6.
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2.
- **Database**: SQLite default for zero-friction local execution (`ctf.db`) and PostgreSQL for Docker production.
- **Security Engine**: Constant-time HMAC-SHA256 comparison for flags, Argon2 for password hashing, and SlowAPI rate limiting (`8/min` on login, `20/min` on submissions).

---

## 3. Challenge Library: 15 File/Static Challenges

All challenges feature authentic downloadable artifacts generated in `challenges/` with writeups in `solutions/`:

### Web / HTTP (File Artifacts)
1. **Hidden Header** (Easy, 100 PTS)
   - **Slug**: `hidden-header`
   - **Artifact**: `challenges/web/hidden-header/files/response.txt`
   - **Objective**: Inspect raw HTTP response headers for internal diagnostic data.
   - **Solution**: Open `response.txt` or execute `grep -i "X-CyberForge" response.txt` to find `X-CyberForge-Diagnostic-Token`.
   - **Flag**: `CTF{h3ad3r_1nspect10n_mast3r}`
   - **Hints**: Inspect all headers starting with `X-` (Penalty: 10 PTS).

2. **Parameter Hunt** (Easy, 150 PTS)
   - **Slug**: `parameter-hunt`
   - **Artifact**: `challenges/web/parameter-hunt/files/api_routes.json`
   - **Objective**: Audit OpenAPI/Swagger specification dumps for undocumented parameters.
   - **Solution**: Search for `developer_override` under `/api/v2/system/debug` in `api_routes.json`.
   - **Flag**: `CTF{und0cum3nted_param_leak_892}`
   - **Hints**: Search for routes with debug or override parameters (Penalty: 15 PTS).

3. **Broken Access** (Medium, 200 PTS)
   - **Slug**: `broken-access`
   - **Artifact**: `challenges/web/broken-access/files/audit_traffic.json`
   - **Objective**: Identify Broken Object-Level Authorization (BOLA/IDOR) in transaction logs.
   - **Solution**: Inspect request `tx_103` where `tenant_a` accesses invoice `9999` returning `admin_escrow_key`.
   - **Flag**: `CTF{b0la_auth_m1sconf1g_7714}`
   - **Hints**: Check invoice IDs that do not belong to Tenant Alpha (Penalty: 20 PTS).

### Digital Forensics
4. **Suspicious Traffic** (Easy, 100 PTS)
   - **Slug**: `suspicious-traffic`
   - **Artifact**: `challenges/forensics/suspicious-traffic/files/suspicious_traffic.pcap`
   - **Objective**: Filter packet streams in Wireshark and extract exfiltrated HTTP data.
   - **Solution**: Open capture in Wireshark, filter by `http`, and inspect the HTTP POST request to `c2-collector.darkcyber.net`.
   - **Flag**: `CTF{pcap_fl0w_analyz3d_4421}`
   - **Hints**: Follow the TCP stream on port 80 or filter by http (Penalty: 10 PTS).

5. **Memory Clue** (Medium, 200 PTS)
   - **Slug**: `memory-clue`
   - **Artifact**: `challenges/forensics/memory-clue/files/memory_minidump.raw`
   - **Objective**: Extract process environment variables from memory segments.
   - **Solution**: Execute `strings memory_minidump.raw | grep "CYBERFORGE_VAULT_TOKEN"`.
   - **Flag**: `CTF{m3m0ry_str1ngs_unv31l_993}`
   - **Hints**: Run strings and search for CYBERFORGE or VAULT (Penalty: 20 PTS).

6. **Incident Logs** (Easy, 150 PTS)
   - **Slug**: `incident-logs`
   - **Artifact**: `challenges/forensics/incident-logs/files/incident_logs.zip`
   - **Objective**: Correlate authentication, web, and application logs to reconstruct an attack.
   - **Solution**: Identify attacker IP `203.0.113.88` logging in via SSH, locate executed script in `application.log`, and base64-decode the payload.
   - **Flag**: `CTF{l0g_c0rr3lat10n_d3t3ct3d_512}`
   - **Hints**: Find the accepted SSH login IP in auth.log, then check application.log (Penalty: 15 PTS).

### Cryptography
7. **Classic Cipher** (Easy, 100 PTS)
   - **Slug**: `classic-cipher`
   - **Artifact**: `challenges/crypto/classic-cipher/files/ciphertext.txt`
   - **Objective**: Decrypt polyalphabetic Vigenère ciphertext with a known key.
   - **Solution**: Decrypt the ciphertext in CyberChef or Python using Vigenère with key `FORGE`.
   - **Flag**: `CTF{v1g3n3r3_c1ph3r_unl0ck3d_881}`
   - **Hints**: Decrypt with Vigenère cipher using key 'FORGE' (Penalty: 10 PTS).

8. **Weak Key** (Medium, 200 PTS)
   - **Slug**: `weak-key`
   - **Artifact**: `challenges/crypto/weak-key/files/challenge_info.txt`
   - **Objective**: Break RSA encryption generated with small prime difference using Fermat's factorization.
   - **Solution**: Calculate $a = \lceil \sqrt{n} \rceil$, find $b = \sqrt{a^2 - n}$, compute $p = a - b, q = a + b$, and compute private exponent $d = e^{-1} \pmod{\phi(n)}$.
   - **Flag**: `CTF{sm4ll_pr1m3s_br3ak_rsa_339}`
   - **Hints**: Fermat's method: check if $a^2 - n$ is a square starting from $a = \text{isqrt}(n)$ (Penalty: 20 PTS).

9. **Encoding Chain** (Easy, 120 PTS)
   - **Slug**: `encoding-chain`
   - **Artifact**: `challenges/crypto/encoding-chain/files/payload.txt`
   - **Objective**: Reverse a multi-stage encoding pipeline.
   - **Solution**: URL Decode $\rightarrow$ Hex to ASCII $\rightarrow$ Base64 Decode $\rightarrow$ ROT13.
   - **Flag**: `CTF{mult1_lay3r_d3c0d1ng_pr0}`
   - **Hints**: URL Decode -> Hex -> Base64 -> ROT13 (Penalty: 10 PTS).

### Open Source Intelligence (OSINT)
10. **Digital Footprints** (Easy, 100 PTS)
    - **Slug**: `digital-footprints`
    - **Artifact**: `challenges/osint/digital-footprints/files/nexusforge_osint.zip`
    - **Objective**: Correlate HTML comments, archived social posts, and document metadata.
    - **Solution**: Discover user `j_reynolds_99` in `website.html` comments and read `Verification-Token` in `metadata.txt`.
    - **Flag**: `CTF{f00tpr1nt_c0rr3lat10n_succ3ss_104}`
    - **Hints**: Check website.html comments, then inspect metadata.txt (Penalty: 10 PTS).

11. **The Forgotten Document** (Medium, 180 PTS)
    - **Slug**: `the-forgotten-document`
    - **Artifact**: `challenges/osint/the-forgotten-document/files/audit_records.zip`
    - **Objective**: Cross-reference decommission memos, DNS CNAME zone dumps, and asset inventories.
    - **Solution**: Memo directs to `legacy-backup.internal` $\rightarrow$ DNS points to `asset-9941` $\rightarrow$ CSV escrow notes leak flag.
    - **Flag**: `CTF{d0cum3nt_arch1v3_unh1dd3n_782}`
    - **Hints**: Lookup legacy-backup.internal in dns_zone.txt, then find asset tag in server_inventory.csv (Penalty: 15 PTS).

### Reverse Engineering
12. **Crack Me** (Easy, 150 PTS)
    - **Slug**: `crack-me`
    - **Artifact**: `challenges/reverse/crack-me/files/crackme.zip`
    - **Objective**: Reverse an XOR validation routine to find the required access key.
    - **Solution**: XOR `SECRET_XOR` bytes with `0x5A` to uncover passkey `CyberForgeKey42`. Run `python crackme.py CyberForgeKey42`.
    - **Flag**: `CTF{str1ngs_and_x0r_r3v3rs1ng_619}`
    - **Hints**: Deobfuscate SECRET_XOR with 0x5A to recover 'CyberForgeKey42' (Penalty: 15 PTS).

13. **Hidden Logic** (Medium, 220 PTS)
    - **Slug**: `hidden-logic`
    - **Artifact**: `challenges/reverse/hidden-logic/files/hidden_logic.zip`
    - **Objective**: Invert an arithmetic state transformation formula: `target[i] = (ord(c) ^ 0x37) + i * 3`.
    - **Solution**: Invert formula: `char = (target[i] - i * 3) ^ 0x37` to deduce serial `CF-9418`. Run `python validator.py CF-9418`.
    - **Flag**: `CTF{v4l1dat10n_l0g1c_d3c0d3d_941}`
    - **Hints**: Invert formula: `(target[i] - i * 3) ^ 0x37` (Penalty: 20 PTS).

### Steganography & Miscellaneous
14. **Image Secret** (Easy, 100 PTS)
    - **Slug**: `image-secret`
    - **Artifact**: `challenges/misc/image-secret/files/cyber_artifact.png`
    - **Objective**: Inspect PNG chunks and trailing stream appended beyond the `IEND` marker.
    - **Solution**: Execute `strings cyber_artifact.png | grep "CTF{"` or view with `exiftool`.
    - **Flag**: `CTF{st3g0_png_chUnk_unc0v3r3d_215}`
    - **Hints**: Use strings or exiftool on cyber_artifact.png (Penalty: 10 PTS).

15. **Strange File** (Medium, 180 PTS)
    - **Slug**: `strange-file`
    - **Artifact**: `challenges/misc/strange-file/files/mystery.bin`
    - **Objective**: Repair corrupted file magic bytes (`XX\x03\x04` $\rightarrow$ `PK\x03\x04`) and extract nested files.
    - **Solution**: Change first two bytes from `XX` (`0x58 0x58`) to `PK` (`0x50 0x4B`), unzip the archive, and read `secret_recovery.txt`.
    - **Flag**: `CTF{p0lygl0t_m4g1c_byt3s_f1x3d_608}`
    - **Hints**: Fix the first two bytes to 'PK' and unzip (Penalty: 15 PTS).

---

## 4. Interactive Local Web Labs

CyberForge includes 3 live, isolated vulnerable web applications that can be launched directly from the challenge interface or managed by administrators:

### Lab 1: SQL Injection (Port 8011)
- **Directory**: `web-labs/sql-injection/`
- **Challenge Slug**: `lab-sql-injection` (150 PTS)
- **Vulnerability**: Unsanitized raw query in `/search?q=`.
- **Exploitation**:
  ```sql
  ' UNION SELECT 1, flag, 'admin' FROM admin_secrets --
  ```
- **Flag**: `CTF{sqli_un10n_inj3ct10n_pwnd_817}`

### Lab 2: IDOR / Access Control (Port 8012)
- **Directory**: `web-labs/idor/`
- **Challenge Slug**: `lab-idor` (200 PTS)
- **Vulnerability**: Missing authorization checks on `/profile?id=`.
- **Exploitation**: Fuzz query parameters to access privileged account ID `1337`:
  ```
  http://localhost:8012/profile?id=1337
  ```
- **Flag**: `CTF{1d0r_br0k3n_0bj3ct_auth_449}`

### Lab 3: File Upload Bypass (Port 8013)
- **Directory**: `web-labs/file-upload/`
- **Challenge Slug**: `lab-file-upload` (200 PTS)
- **Vulnerability**: Weak blacklist and diagnostic parser keyword override.
- **Exploitation**: Upload any `.txt` or `.log` file containing the word `override` or named `override.txt`.
- **Flag**: `CTF{f1l3_upl0ad_byp4ss_succ3ss_321}`

### Managing Web Labs
- **In-Browser UI**: Open any web lab challenge page (e.g. `/challenges/16`) and click **"Launch Web Lab"**. The target URL `http://localhost:<port>` appears with restart and stop buttons.
- **Admin Control Center**: Navigate to `/admin/labs` to monitor active ports, view uptime, and manage all 3 instances concurrently.
- **Docker Compose**:
  ```bash
  cd "d:\CTF Platform\web-labs"
  docker compose up -d
  ```

---

## 5. Development & Testing Commands

### Start Backend Server
```powershell
cd "d:\CTF Platform\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Start Frontend Server
```powershell
cd "d:\CTF Platform\frontend"
npm run dev -- --host
```

### Run Test Suites
```powershell
# Backend (Pytest):
cd "d:\CTF Platform\backend"
pytest -v

# Frontend (Vitest & Build):
cd "d:\CTF Platform\frontend"
npm run test -- --run
npm run build
```
