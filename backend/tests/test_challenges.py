from app.models import UserRole
from tests.conftest import create_challenge, create_user


def test_unpublished_hidden_from_users(client, db_session):
    author = create_user(db_session, "author", role=UserRole.CHALLENGE_AUTHOR)
    create_challenge(db_session, author, published=False, slug="hidden")
    create_user(db_session, "player")
    client.post("/api/auth/login", json={"username": "player", "password": "Password!23"})
    listing = client.get("/api/challenges")
    assert listing.status_code == 200
    assert listing.json()["total"] == 0


def test_correct_flag_awards_points_once(client, db_session):
    author = create_user(db_session, "author", role=UserRole.CHALLENGE_AUTHOR)
    challenge = create_challenge(db_session, author, flag="CTF{ok}", points=250)
    create_user(db_session, "player")
    client.post("/api/auth/login", json={"username": "player", "password": "Password!23"})
    first = client.post(f"/api/challenges/{challenge.id}/submit", json={"flag": "CTF{ok}"})
    assert first.status_code == 200
    assert first.json()["correct"] is True
    assert first.json()["points_awarded"] == 250
    second = client.post(f"/api/challenges/{challenge.id}/submit", json={"flag": "CTF{ok}"})
    assert second.json()["correct"] is True
    assert second.json()["already_solved"] is True
    assert second.json()["points_awarded"] == 0
    me = client.get("/api/auth/me")
    assert me.json()["total_points"] == 250


def test_incorrect_flag(client, db_session):
    author = create_user(db_session, "author", role=UserRole.CHALLENGE_AUTHOR)
    challenge = create_challenge(db_session, author)
    create_user(db_session, "player")
    client.post("/api/auth/login", json={"username": "player", "password": "Password!23"})
    res = client.post(f"/api/challenges/{challenge.id}/submit", json={"flag": "CTF{nope}"})
    assert res.status_code == 200
    assert res.json()["correct"] is False
    detail = client.get(f"/api/challenges/{challenge.id}")
    assert "CTF{secret}" not in detail.text
    assert "flag_hash" not in detail.text


def test_public_api_does_not_leak_flag(client, db_session):
    author = create_user(db_session, "author", role=UserRole.CHALLENGE_AUTHOR)
    challenge = create_challenge(db_session, author, flag="CTF{must_not_leak}")
    res = client.get(f"/api/challenges/{challenge.id}")
    assert res.status_code == 200
    assert "must_not_leak" not in res.text


def test_hint_reveal_applies_penalty(client, db_session):
    from app.models import Hint
    author = create_user(db_session, "hintauthor", role=UserRole.CHALLENGE_AUTHOR)
    challenge = create_challenge(db_session, author, flag="CTF{hinted}", points=200, slug="hinted-chal")
    hint = Hint(challenge_id=challenge.id, content="Secret hint content", cost=30, order_index=1)
    db_session.add(hint)
    db_session.commit()

    player = create_user(db_session, "hintplayer")
    client.post("/api/auth/login", json={"username": "hintplayer", "password": "Password!23"})

    # Solve challenge first -> 200 pts
    sol_res = client.post(f"/api/challenges/{challenge.id}/submit", json={"flag": "CTF{hinted}"})
    assert sol_res.status_code == 200
    assert sol_res.json()["total_points"] == 200

    # Reveal hint with 30 pt cost
    rev_res = client.post(f"/api/challenges/{challenge.id}/hints/{hint.id}/reveal")
    assert rev_res.status_code == 200
    assert rev_res.json()["content"] == "Secret hint content"
    assert rev_res.json()["cost"] == 30

    me = client.get("/api/auth/me")
    assert me.json()["total_points"] == 170

    # Re-revealing doesn't penalize again
    rev_res2 = client.post(f"/api/challenges/{challenge.id}/hints/{hint.id}/reveal")
    assert rev_res2.json()["already_revealed"] is True
    assert client.get("/api/auth/me").json()["total_points"] == 170


def test_admin_get_and_edit_challenge(client, db_session):
    from app.models import Hint
    admin = create_user(db_session, "adm_tester", role=UserRole.ADMIN)
    challenge = create_challenge(db_session, admin, slug="admin-chal", points=100)
    hint = Hint(challenge_id=challenge.id, content="Unrevealed hint", cost=15, order_index=1)
    db_session.add(hint)
    db_session.commit()

    client.post("/api/auth/login", json={"username": "adm_tester", "password": "Password!23"})
    res = client.get(f"/api/admin/challenges/{challenge.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == challenge.title
    assert len(data["hints"]) == 1
    assert data["hints"][0]["content"] == "Unrevealed hint"

    # Edit challenge
    patch_res = client.patch(
        f"/api/admin/challenges/{challenge.id}",
        json={"points": 150, "description": "Updated description"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["points"] == 150


def test_bearer_token_auth(client, db_session):
    from app.security import create_access_token
    user = create_user(db_session, "token_user")
    token = create_access_token(str(user.id))
    # Request with Bearer header (no cookie)
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["username"] == "token_user"
