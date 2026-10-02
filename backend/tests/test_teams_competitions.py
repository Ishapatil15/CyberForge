from datetime import timedelta

from app.models import (
    Competition,
    CompetitionChallenge,
    CompetitionMode,
    CompetitionParticipant,
    CompetitionVisibility,
    UserRole,
)
from app.security import utcnow
from tests.conftest import create_challenge, create_user


def test_team_create_invite_and_unauthorized_remove(client, db_session):
    create_user(db_session, "captain")
    create_user(db_session, "member")
    create_user(db_session, "intruder")
    client.post("/api/auth/login", json={"username": "captain", "password": "Password!23"})
    team = client.post("/api/teams", json={"name": "Cyber Wolves", "description": "Practice"})
    assert team.status_code == 200
    team_id = team.json()["id"]
    invite = client.post(f"/api/teams/{team_id}/invite", json={"username": "member"})
    assert invite.status_code == 200
    client.post("/api/auth/logout")
    client.post("/api/auth/login", json={"username": "member", "password": "Password!23"})
    invites = client.get("/api/users/me/profile").json()["invitations"]
    assert len(invites) == 1
    assert client.post(f"/api/teams/invitations/{invites[0]['id']}/accept").status_code == 200
    client.post("/api/auth/logout")
    client.post("/api/auth/login", json={"username": "intruder", "password": "Password!23"})
    member_id = next(u["id"] for u in client.get(f"/api/teams/{team_id}").json()["members"] if u["username"] == "member")
    denied = client.post(f"/api/teams/{team_id}/members/{member_id}/remove")
    assert denied.status_code == 403


def test_competition_window_enforced(client, db_session):
    admin = create_user(db_session, "admin", role=UserRole.ADMIN)
    challenge = create_challenge(db_session, admin, slug="comp-web")
    now = utcnow()
    upcoming = Competition(
        name="Future Cup",
        slug="future-cup",
        description="Later",
        rules="Be nice",
        mode=CompetitionMode.INDIVIDUAL,
        visibility=CompetitionVisibility.PUBLIC,
        registration_required=True,
        start_at=now + timedelta(days=2),
        end_at=now + timedelta(days=3),
        registration_start_at=now - timedelta(days=1),
        registration_end_at=now + timedelta(days=1),
    )
    db_session.add(upcoming)
    db_session.flush()
    db_session.add(CompetitionChallenge(competition_id=upcoming.id, challenge_id=challenge.id))
    player = create_user(db_session, "player")
    db_session.add(CompetitionParticipant(competition_id=upcoming.id, user_id=player.id))
    db_session.commit()
    client.post("/api/auth/login", json={"username": "player", "password": "Password!23"})
    res = client.post(
        f"/api/challenges/{challenge.id}/submit",
        json={"flag": "CTF{secret}", "competition_id": upcoming.id},
    )
    assert res.status_code == 403


def test_active_competition_allows_submit(client, db_session):
    admin = create_user(db_session, "admin", role=UserRole.ADMIN)
    challenge = create_challenge(db_session, admin, slug="live-web", flag="CTF{live}")
    now = utcnow()
    live = Competition(
        name="Live Cup",
        slug="live-cup",
        description="Now",
        rules="Be nice",
        mode=CompetitionMode.INDIVIDUAL,
        visibility=CompetitionVisibility.PUBLIC,
        registration_required=True,
        start_at=now - timedelta(hours=1),
        end_at=now + timedelta(days=1),
        registration_start_at=now - timedelta(days=1),
        registration_end_at=now + timedelta(days=1),
    )
    db_session.add(live)
    db_session.flush()
    db_session.add(CompetitionChallenge(competition_id=live.id, challenge_id=challenge.id))
    player = create_user(db_session, "player")
    db_session.add(CompetitionParticipant(competition_id=live.id, user_id=player.id))
    db_session.commit()
    client.post("/api/auth/login", json={"username": "player", "password": "Password!23"})
    res = client.post(
        f"/api/challenges/{challenge.id}/submit",
        json={"flag": "CTF{live}", "competition_id": live.id},
    )
    assert res.status_code == 200
    assert res.json()["correct"] is True


def test_leaderboard_tie_break(client, db_session):
    author = create_user(db_session, "author", role=UserRole.CHALLENGE_AUTHOR)
    c1 = create_challenge(db_session, author, slug="a", flag="CTF{a}", points=100)
    create_user(db_session, "alpha")
    create_user(db_session, "beta")
    client.post("/api/auth/login", json={"username": "alpha", "password": "Password!23"})
    client.post(f"/api/challenges/{c1.id}/submit", json={"flag": "CTF{a}"})
    client.post("/api/auth/logout")
    client.post("/api/auth/login", json={"username": "beta", "password": "Password!23"})
    client.post(f"/api/challenges/{c1.id}/submit", json={"flag": "CTF{a}"})
    board = client.get("/api/leaderboard/global").json()["items"]
    assert board[0]["username"] == "alpha"
    assert board[1]["username"] == "beta"
