import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.limiter import limiter
from app.main import app

limiter.enabled = False
from app.models import (
    Category,
    Challenge,
    Competition,
    CompetitionChallenge,
    CompetitionMode,
    CompetitionVisibility,
    Difficulty,
    User,
    UserRole,
)
from app.security import hash_flag, hash_password, utcnow
from datetime import timedelta


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_user(db, username, password="Password!23", role=UserRole.USER, email=None):
    user = User(
        username=username,
        email=email or f"{username}@local.ctf",
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_challenge(db, author, title="Web Lab", slug="web-lab", flag="CTF{secret}", published=True, points=100):
    challenge = Challenge(
        title=title,
        slug=slug,
        description="Practice challenge",
        category=Category.WEB,
        difficulty=Difficulty.EASY,
        points=points,
        flag_format="CTF{...}",
        flag_hash=hash_flag(flag),
        author_id=author.id,
        is_published=published,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)
    return challenge


def auth_client(client, username, password="Password!23"):
    res = client.post("/api/auth/login", json={"username": username, "password": password})
    assert res.status_code == 200
    return client
