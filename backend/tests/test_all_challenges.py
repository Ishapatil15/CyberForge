import json
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Challenge, User, UserRole
from app.security import hash_password
from app.seed import seed


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    seed()
    with TestClient(app) as c:
        yield c


def _get_auth_headers(client: TestClient, username: str = "player_test", password: str = "TestPass!23"):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            user = User(
                username=username,
                email=f"{username}@test.ctf",
                password_hash=hash_password(password),
                role=UserRole.USER,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        user_id = user.id
    finally:
        db.close()

    from app.security import create_access_token
    token = create_access_token(str(user_id))
    return {"Authorization": f"Bearer {token}"}


def test_challenges_and_attachments_exist(client: TestClient):
    res = client.get("/api/challenges?page_size=50")
    assert res.status_code == 200
    items = res.json()["items"]
    # We should have at least 18 challenges (15 file + 3 labs)
    assert len(items) >= 18

    # Verify every challenge has points > 0 and valid category
    for c in items:
        assert c["points"] > 0
        assert c["category"] in [
            "WEB", "CRYPTOGRAPHY", "FORENSICS", "REVERSE_ENGINEERING",
            "OSINT", "STEGANOGRAPHY", "MISCELLANEOUS"
        ]


def test_solve_all_15_challenges_and_prevent_duplicate_score(client: TestClient):
    import uuid
    headers = _get_auth_headers(client, f"solver_{uuid.uuid4().hex[:8]}", "SolverPass!23")

    manifest_path = Path(__file__).resolve().parent.parent.parent / "challenges" / "manifest.json"
    assert manifest_path.exists(), "Manifest file must exist"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    total_expected_points = 0

    for item in manifest:
        slug = item["slug"]
        flag = item["flag"]

        # 1. Fetch challenge list to find ID
        res = client.get(f"/api/challenges?q={slug}", headers=headers)
        assert res.status_code == 200
        matches = [c for c in res.json()["items"] if c["slug"] == slug]
        assert len(matches) > 0, f"Challenge {slug} not found in listing"
        chal_id = matches[0]["id"]
        points = matches[0]["points"]

        # 2. Get challenge detail
        res = client.get(f"/api/challenges/{chal_id}", headers=headers)
        assert res.status_code == 200
        detail = res.json()
        assert detail["solved"] is False

        # 3. Check attachment download if present
        if detail["attachments"]:
            att_id = detail["attachments"][0]["id"]
            dl = client.get(f"/api/challenges/{chal_id}/attachments/{att_id}", headers=headers)
            assert dl.status_code == 200, f"Failed to download attachment for {slug}"
            assert len(dl.content) > 0

        # 4. Submit incorrect flag first
        bad_sub = client.post(f"/api/challenges/{chal_id}/submit", json={"flag": "CTF{wrong_flag}"}, headers=headers)
        assert bad_sub.status_code == 200
        assert bad_sub.json()["correct"] is False
        assert bad_sub.json()["points_awarded"] == 0

        # 5. Submit valid flag
        sub = client.post(f"/api/challenges/{chal_id}/submit", json={"flag": flag}, headers=headers)
        assert sub.status_code == 200
        sub_data = sub.json()
        assert sub_data["correct"] is True, f"Flag {flag} rejected for {slug}"
        assert sub_data["already_solved"] is False
        assert sub_data["points_awarded"] == points
        total_expected_points += points

        # 6. Submit duplicate flag
        dup = client.post(f"/api/challenges/{chal_id}/submit", json={"flag": flag}, headers=headers)
        assert dup.status_code == 200
        dup_data = dup.json()
        assert dup_data["correct"] is True
        assert dup_data["already_solved"] is True
        assert dup_data["points_awarded"] == 0


def test_web_labs_api(client: TestClient):
    headers = _get_auth_headers(client, "lab_tester_user", "LabPass!23")

    # 1. List labs
    res = client.get("/api/labs", headers=headers)
    assert res.status_code == 200
    labs = res.json()["items"]
    assert len(labs) == 3
    assert {l["id"] for l in labs} == {"sql-injection", "idor", "file-upload"}

    # 2. Check individual lab status
    res = client.get("/api/labs/sql-injection/status", headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == "sql-injection"

    # 3. Start lab
    start_res = client.post("/api/labs/sql-injection/start", headers=headers)
    assert start_res.status_code == 200
    assert start_res.json()["ok"] is True
    assert start_res.json()["status"] == "RUNNING"
    assert "8011" in start_res.json()["target_url"]

    # 4. Stop lab
    stop_res = client.post("/api/labs/sql-injection/stop", headers=headers)
    assert stop_res.status_code == 200
    assert stop_res.json()["ok"] is True
    assert stop_res.json()["status"] == "STOPPED"
