from datetime import timedelta
from pathlib import Path
import shutil
import uuid
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import (
    Attachment,
    Category,
    Challenge,
    ChallengeTag,
    Competition,
    CompetitionChallenge,
    CompetitionMode,
    CompetitionParticipant,
    CompetitionVisibility,
    Difficulty,
    Hint,
    Tag,
    Team,
    TeamMember,
    User,
    UserRole,
)
from app.security import hash_flag, hash_password, utcnow
from app.services.challenges import slugify

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CHALLENGES_DIR = ROOT_DIR / "challenges"


def get_or_create_tag(db: Session, name: str) -> Tag:
    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        tag = Tag(name=name)
        db.add(tag)
        db.flush()
    return tag


def ensure_user(db: Session, username: str, email: str, password: str, role: UserRole) -> User:
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.flush()
    return user


def attach_file(db: Session, challenge: Challenge, src_path: Path, content_type: str = "application/octet-stream") -> Attachment:
    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = src_path.suffix.lower()
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    dest_path = upload_dir / stored_name
    shutil.copyfile(src_path, dest_path)

    existing = db.query(Attachment).filter(
        Attachment.challenge_id == challenge.id,
        Attachment.original_name == src_path.name,
    ).first()
    if existing:
        return existing

    attachment = Attachment(
        challenge_id=challenge.id,
        original_name=src_path.name,
        stored_name=stored_name,
        content_type=content_type,
        size_bytes=src_path.stat().st_size,
    )
    db.add(attachment)
    db.flush()
    return attachment


def ensure_challenge(
    db: Session,
    author: User,
    title: str,
    slug: str,
    description: str,
    category: Category,
    difficulty: Difficulty,
    points: int,
    flag: str,
    tags: list[str],
    hints: list[tuple[str, int]],
    file_info: tuple[Path, str] | None = None,
    published: bool = True,
) -> Challenge:
    challenge = db.query(Challenge).filter(Challenge.slug == slug).first()
    if not challenge:
        challenge = Challenge(
            title=title,
            slug=slug,
            description=description,
            category=category,
            difficulty=difficulty,
            points=points,
            flag_format="CTF{...}",
            flag_hash=hash_flag(flag),
            author_id=author.id,
            is_published=published,
        )
        db.add(challenge)
        db.flush()

        for name in tags:
            challenge.tags.append(ChallengeTag(tag=get_or_create_tag(db, name)))
        for i, (content, cost) in enumerate(hints, start=1):
            challenge.hints.append(Hint(content=content, cost=cost, order_index=i))
    else:
        # Keep flag and details updated
        challenge.flag_hash = hash_flag(flag)
        challenge.points = points
        challenge.is_published = published
        challenge.description = description
        db.flush()

    if file_info and file_info[0].exists():
        attach_file(db, challenge, file_info[0], file_info[1])

    return challenge


def seed(db: Session | None = None) -> None:
    close = False
    if db is None:
        db = SessionLocal()
        close = True
    try:
        settings = get_settings()
        admin = ensure_user(db, settings.admin_username, settings.admin_email, settings.admin_password, UserRole.ADMIN)
        author = ensure_user(db, "author", "author@local.ctf", "AuthorPass!23", UserRole.CHALLENGE_AUTHOR)
        isha = ensure_user(db, "isha", "isha@local.ctf", "PlayerPass!23", UserRole.USER)
        rahul = ensure_user(db, "rahul", "rahul@local.ctf", "PlayerPass!23", UserRole.USER)
        ananya = ensure_user(db, "ananya", "ananya@local.ctf", "PlayerPass!23", UserRole.USER)
        akash = ensure_user(db, "akash", "akash@local.ctf", "PlayerPass!23", UserRole.USER)

        challenges = []

        # 1. Hidden Header
        c1 = ensure_challenge(
            db, author,
            title="Hidden Header",
            slug="hidden-header",
            description="A network administrator intercepted a response from an internal staging gateway. Inspect the captured HTTP response artifact to discover the diagnostic authentication token.",
            category=Category.WEB,
            difficulty=Difficulty.EASY,
            points=100,
            flag="CTF{h3ad3r_1nspect10n_mast3r}",
            tags=["web", "http-headers", "curl"],
            hints=[("Inspect all custom HTTP headers beginning with X-.", 10)],
            file_info=(CHALLENGES_DIR / "web" / "hidden-header" / "files" / "response.txt", "text/plain"),
        )
        challenges.append(c1)

        # 2. Parameter Hunt
        c2 = ensure_challenge(
            db, author,
            title="Parameter Hunt",
            slug="parameter-hunt",
            description="A client-side service worker leaked an API endpoint schema. Investigate the route definitions to discover an undocumented diagnostic parameter.",
            category=Category.WEB,
            difficulty=Difficulty.EASY,
            points=150,
            flag="CTF{und0cum3nted_param_leak_892}",
            tags=["web", "api", "parameter-discovery"],
            hints=[("Search the schema for routes with debug or override parameters.", 15)],
            file_info=(CHALLENGES_DIR / "web" / "parameter-hunt" / "files" / "api_routes.json", "application/json"),
        )
        challenges.append(c2)

        # 3. Broken Access
        c3 = ensure_challenge(
            db, author,
            title="Broken Access",
            slug="broken-access",
            description="A security analyst captured transaction logs showing a user requesting documents outside their assigned tenancy. Analyze the API trace to identify the unauthorized object reference and extract the leaked administrative key.",
            category=Category.WEB,
            difficulty=Difficulty.MEDIUM,
            points=200,
            flag="CTF{b0la_auth_m1sconf1g_7714}",
            tags=["web", "bola", "idor", "api-security"],
            hints=[("Look for invoice IDs that do not belong to Tenant Alpha and inspect the returned JSON response.", 20)],
            file_info=(CHALLENGES_DIR / "web" / "broken-access" / "files" / "audit_traffic.json", "application/json"),
        )
        challenges.append(c3)

        # 4. Suspicious Traffic
        c4 = ensure_challenge(
            db, author,
            title="Suspicious Traffic",
            slug="suspicious-traffic",
            description="A network intrusion detection system alerted on beaconing behavior from a workstation. Examine the supplied packet capture in Wireshark and extract the exfiltrated flag.",
            category=Category.FORENSICS,
            difficulty=Difficulty.EASY,
            points=100,
            flag="CTF{pcap_fl0w_analyz3d_4421}",
            tags=["forensics", "wireshark", "pcap", "network-analysis"],
            hints=[("Filter by http in Wireshark or follow the TCP stream on port 80.", 10)],
            file_info=(CHALLENGES_DIR / "forensics" / "suspicious-traffic" / "files" / "suspicious_traffic.pcap", "application/vnd.tcpdump.pcap"),
        )
        challenges.append(c4)

        # 5. Memory Clue
        c5 = ensure_challenge(
            db, author,
            title="Memory Clue",
            slug="memory-clue",
            description="Investigators dumped the memory space of a suspicious background process. Extract the secret vault authentication token preserved in the process environment segment.",
            category=Category.FORENSICS,
            difficulty=Difficulty.MEDIUM,
            points=200,
            flag="CTF{m3m0ry_str1ngs_unv31l_993}",
            tags=["forensics", "memory-forensics", "strings"],
            hints=[("Run strings on the memory dump and search for CYBERFORGE or VAULT.", 20)],
            file_info=(CHALLENGES_DIR / "forensics" / "memory-clue" / "files" / "memory_minidump.raw", "application/octet-stream"),
        )
        challenges.append(c5)

        # 6. Incident Logs
        c6 = ensure_challenge(
            db, author,
            title="Incident Logs",
            slug="incident-logs",
            description="An unknown actor successfully logged into an internal host and executed a staging command. Correlate auth.log, server.log, and application.log to identify the intrusion and decode the payload.",
            category=Category.FORENSICS,
            difficulty=Difficulty.EASY,
            points=150,
            flag="CTF{l0g_c0rr3lat10n_d3t3ct3d_512}",
            tags=["forensics", "log-analysis", "incident-response"],
            hints=[("Find the attacker IP from the accepted SSH login in auth.log, then check application.log for the payload.", 15)],
            file_info=(CHALLENGES_DIR / "forensics" / "incident-logs" / "files" / "incident_logs.zip", "application/zip"),
        )
        challenges.append(c6)

        # 7. Classic Cipher
        c7 = ensure_challenge(
            db, author,
            title="Classic Cipher",
            slug="classic-cipher",
            description="An operational memo was encrypted using a polyalphabetic Vigenère cipher with the keyword FORGE. Decrypt the ciphertext to uncover the clearance key.",
            category=Category.CRYPTOGRAPHY,
            difficulty=Difficulty.EASY,
            points=100,
            flag="CTF{v1g3n3r3_c1ph3r_unl0ck3d_881}",
            tags=["crypto", "vigenere", "classic-cipher"],
            hints=[("Use CyberChef or Python to decrypt the Vigenère cipher using key 'FORGE'.", 10)],
            file_info=(CHALLENGES_DIR / "crypto" / "classic-cipher" / "files" / "ciphertext.txt", "text/plain"),
        )
        challenges.append(c7)

        # 8. Weak Key
        c8 = ensure_challenge(
            db, author,
            title="Weak Key",
            slug="weak-key",
            description="A custom RSA key generator produced primes that are dangerously close to each other. Use Fermat's factorization method to factorize modulus n and decrypt the flag ciphertext.",
            category=Category.CRYPTOGRAPHY,
            difficulty=Difficulty.MEDIUM,
            points=200,
            flag="CTF{sm4ll_pr1m3s_br3ak_rsa_339}",
            tags=["crypto", "rsa", "fermat-factorization"],
            hints=[("Because p and q are close, calculate a = isqrt(n); test if a^2 - n is a square.", 20)],
            file_info=(CHALLENGES_DIR / "crypto" / "weak-key" / "files" / "challenge_info.txt", "text/plain"),
        )
        challenges.append(c8)

        # 9. Encoding Chain
        c9 = ensure_challenge(
            db, author,
            title="Encoding Chain",
            slug="encoding-chain",
            description="An attacker obfuscated their payload by chaining multiple encoding layers. Unwrap the encoding transformations in sequence to discover the plaintext flag.",
            category=Category.CRYPTOGRAPHY,
            difficulty=Difficulty.EASY,
            points=120,
            flag="CTF{mult1_lay3r_d3c0d1ng_pr0}",
            tags=["crypto", "encoding", "base64", "rot13"],
            hints=[("Reversal sequence: URL Decode -> Hex to ASCII -> Base64 Decode -> ROT13.", 10)],
            file_info=(CHALLENGES_DIR / "crypto" / "encoding-chain" / "files" / "payload.txt", "text/plain"),
        )
        challenges.append(c9)

        # 10. Digital Footprints
        c10 = ensure_challenge(
            db, author,
            title="Digital Footprints",
            slug="digital-footprints",
            description="Fictional aerospace research organization NexusForge left digital traces across public archives. Correlate the website comment, social feed, and project metadata in nexusforge_osint.zip to locate the verification token.",
            category=Category.OSINT,
            difficulty=Difficulty.EASY,
            points=100,
            flag="CTF{f00tpr1nt_c0rr3lat10n_succ3ss_104}",
            tags=["osint", "correlation", "metadata"],
            hints=[("Find the username in website.html, then check metadata.txt for the verification token.", 10)],
            file_info=(CHALLENGES_DIR / "osint" / "digital-footprints" / "files" / "nexusforge_osint.zip", "application/zip"),
        )
        challenges.append(c10)

        # 11. The Forgotten Document
        c11 = ensure_challenge(
            db, author,
            title="The Forgotten Document",
            slug="the-forgotten-document",
            description="Corporate audit logs contain records of a retired backup host. Correlate the decommission memo, internal DNS zone file, and hardware server inventory in audit_records.zip to recover the escrow key.",
            category=Category.OSINT,
            difficulty=Difficulty.MEDIUM,
            points=180,
            flag="CTF{d0cum3nt_arch1v3_unh1dd3n_782}",
            tags=["osint", "asset-tracking", "correlation"],
            hints=[("Lookup legacy-backup.internal in dns_zone.txt to find the asset tag, then locate it in server_inventory.csv.", 15)],
            file_info=(CHALLENGES_DIR / "osint" / "the-forgotten-document" / "files" / "audit_records.zip", "application/zip"),
        )
        challenges.append(c11)

        # 12. Crack Me
        c12 = ensure_challenge(
            db, author,
            title="Crack Me",
            slug="crack-me",
            description="A secure access terminal checks user input against an obfuscated validation sequence. Analyze the logic in crackme.zip to recover the correct passkey and reveal the flag.",
            category=Category.REVERSE_ENGINEERING,
            difficulty=Difficulty.EASY,
            points=150,
            flag="CTF{str1ngs_and_x0r_r3v3rs1ng_619}",
            tags=["reverse-engineering", "static-analysis", "python-reversing"],
            hints=[("Inspect SECRET_XOR in crackme.py or XOR each byte with 0x5A to recover the required key 'CyberForgeKey42'.", 15)],
            file_info=(CHALLENGES_DIR / "reverse" / "crack-me" / "files" / "crackme.zip", "application/zip"),
        )
        challenges.append(c12)

        # 13. Hidden Logic
        c13 = ensure_challenge(
            db, author,
            title="Hidden Logic",
            slug="hidden-logic",
            description="A hardware validation routine enforces licensing keys using a custom arithmetic state transformation. Reverse engineer validator.py in hidden_logic.zip to calculate the valid serial and trigger flag output.",
            category=Category.REVERSE_ENGINEERING,
            difficulty=Difficulty.MEDIUM,
            points=220,
            flag="CTF{v4l1dat10n_l0g1c_d3c0d3d_941}",
            tags=["reverse-engineering", "algorithm-reversal", "math"],
            hints=[("Invert the formula: ord(ch) = (TARGET_ARRAY[i] - i * 3) ^ 0x37.", 20)],
            file_info=(CHALLENGES_DIR / "reverse" / "hidden-logic" / "files" / "hidden_logic.zip", "application/zip"),
        )
        challenges.append(c13)

        # 14. Image Secret
        c14 = ensure_challenge(
            db, author,
            title="Image Secret",
            slug="image-secret",
            description="A digital reconnaissance image contains intelligence concealed within its metadata chunk and trailing file stream. Analyze cyber_artifact.png to extract the hidden flag.",
            category=Category.STEGANOGRAPHY,
            difficulty=Difficulty.EASY,
            points=100,
            flag="CTF{st3g0_png_chUnk_unc0v3r3d_215}",
            tags=["steganography", "metadata", "png-chunks"],
            hints=[("Use strings or exiftool on cyber_artifact.png to inspect embedded text chunks.", 10)],
            file_info=(CHALLENGES_DIR / "misc" / "image-secret" / "files" / "cyber_artifact.png", "image/png"),
        )
        challenges.append(c14)

        # 15. Strange File
        c15 = ensure_challenge(
            db, author,
            title="Strange File",
            slug="strange-file",
            description="Forensics responders recovered a file mystery.bin with a corrupted header. Analyze the file format structure in a hex editor, repair the magic bytes, and extract the recovery document.",
            category=Category.MISCELLANEOUS,
            difficulty=Difficulty.MEDIUM,
            points=180,
            flag="CTF{p0lygl0t_m4g1c_byt3s_f1x3d_608}",
            tags=["misc", "file-signatures", "magic-bytes"],
            hints=[("Look at bytes 3-4 (\\x03\\x04) and file strings. It is a ZIP file with the first two bytes changed from 'PK' to 'XX'.", 15)],
            file_info=(CHALLENGES_DIR / "misc" / "strange-file" / "files" / "mystery.bin", "application/octet-stream"),
        )
        challenges.append(c15)

        # 16. Web Lab 1: SQL Injection
        c16 = ensure_challenge(
            db, author,
            title="Web Lab: SQL Injection",
            slug="lab-sql-injection",
            description="Launch the local SQL Injection Web Lab to access a student query portal. Craft a SQL injection payload into the search query to union-select the secret flag from admin_secrets.",
            category=Category.WEB,
            difficulty=Difficulty.EASY,
            points=150,
            flag="CTF{sqli_un10n_inj3ct10n_pwnd_817}",
            tags=["web", "sqli", "interactive-lab"],
            hints=[("Enter: ' UNION SELECT 1, flag, 'admin' FROM admin_secrets -- in the search bar.", 15)],
        )
        challenges.append(c16)

        # 17. Web Lab 2: IDOR
        c17 = ensure_challenge(
            db, author,
            title="Web Lab: IDOR / Access Control",
            slug="lab-idor",
            description="Launch the local IDOR Web Lab to inspect personnel records. Fuzz the profile ID parameter to locate the unlisted administrative officer and read their compliance notes.",
            category=Category.WEB,
            difficulty=Difficulty.MEDIUM,
            points=200,
            flag="CTF{1d0r_br0k3n_0bj3ct_auth_449}",
            tags=["web", "idor", "access-control", "interactive-lab"],
            hints=[("Try querying /profile?id=1337.", 20)],
        )
        challenges.append(c17)

        # 18. Web Lab 3: File Upload
        c18 = ensure_challenge(
            db, author,
            title="Web Lab: File Upload",
            slug="lab-file-upload",
            description="Launch the local File Upload Web Lab. Upload an audit document containing override flags to trigger the internal parser diagnostic routine.",
            category=Category.WEB,
            difficulty=Difficulty.MEDIUM,
            points=200,
            flag="CTF{f1l3_upl0ad_byp4ss_succ3ss_321}",
            tags=["web", "file-upload", "parser-bypass", "interactive-lab"],
            hints=[("Upload a file with 'override' or 'flag' in the filename or file content.", 20)],
        )
        challenges.append(c18)

        # Competition setup
        now = utcnow()
        comp = db.query(Competition).filter(Competition.slug == "cyber-warfare-2026").first()
        if not comp:
            comp = Competition(
                name="Cyber Warfare 2026",
                slug="cyber-warfare-2026",
                description="CyberForge invitational arena featuring 15 real challenges across Web, Crypto, Forensics, OSINT, Reversing, and 3 Interactive Web Labs.",
                rules="No attacking the platform infrastructure. No sharing flags. Play fairly. Times are enforced server-side in UTC.",
                mode=CompetitionMode.INDIVIDUAL,
                visibility=CompetitionVisibility.PUBLIC,
                registration_required=True,
                start_at=now - timedelta(hours=2),
                end_at=now + timedelta(days=7),
                registration_start_at=now - timedelta(days=3),
                registration_end_at=now + timedelta(days=6),
            )
            db.add(comp)
            db.flush()
            db.add(CompetitionParticipant(competition_id=comp.id, user_id=isha.id))
            db.add(CompetitionParticipant(competition_id=comp.id, user_id=rahul.id))

        # Link all challenges to competition
        existing_links = {
            link.challenge_id for link in db.query(CompetitionChallenge).filter(CompetitionChallenge.competition_id == comp.id).all()
        }
        for chal in challenges:
            if chal.id not in existing_links:
                db.add(CompetitionChallenge(competition_id=comp.id, challenge_id=chal.id))

        # Team setup
        if not db.query(Team).filter(Team.slug == "cyber-wolves").first():
            team = Team(
                name="Cyber Wolves",
                slug="cyber-wolves",
                description="Student practice team for CyberForge.",
                captain_id=isha.id,
            )
            db.add(team)
            db.flush()
            db.add(TeamMember(team_id=team.id, user_id=isha.id))
            db.add(TeamMember(team_id=team.id, user_id=rahul.id))
            db.add(TeamMember(team_id=team.id, user_id=ananya.id))

        db.commit()
        print(f"Successfully seeded {len(challenges)} authentic challenges, attachments, hints, and competition links.")
    finally:
        if close:
            db.close()


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    seed()
