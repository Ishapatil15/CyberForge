from app.models import UserRole
from tests.conftest import create_user


def test_register_and_me(client):
    res = client.post(
        "/api/auth/register",
        json={"username": "nova", "email": "nova@local.ctf", "password": "Password!23"},
    )
    assert res.status_code == 200
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["username"] == "nova"
    assert me.json()["role"] == "USER"


def test_login_invalid(client, db_session):
    create_user(db_session, "isha")
    res = client.post("/api/auth/login", json={"username": "isha", "password": "wrongpass1"})
    assert res.status_code == 401


def test_logout(client):
    client.post(
        "/api/auth/register",
        json={"username": "logoutu", "email": "logoutu@local.ctf", "password": "Password!23"},
    )
    client.post("/api/auth/logout")
    assert client.get("/api/auth/me").status_code == 401


def test_cannot_patch_role_via_profile(client):
    client.post(
        "/api/auth/register",
        json={"username": "roletry", "email": "roletry@local.ctf", "password": "Password!23"},
    )
    res = client.patch("/api/auth/me", json={"bio": "hello", "role": "ADMIN"})
    assert res.status_code == 200
    assert res.json()["role"] == "USER"


def test_admin_required(client, db_session):
    create_user(db_session, "plain")
    client.post("/api/auth/login", json={"username": "plain", "password": "Password!23"})
    res = client.get("/api/admin/users")
    assert res.status_code == 403


def test_admin_can_list_users(client, db_session):
    create_user(db_session, "admin", role=UserRole.ADMIN)
    client.post("/api/auth/login", json={"username": "admin", "password": "Password!23"})
    res = client.get("/api/admin/users")
    assert res.status_code == 200
    assert res.json()["total"] >= 1
