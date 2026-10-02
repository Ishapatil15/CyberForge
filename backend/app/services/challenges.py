from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models import (
    Challenge,
    ChallengeTag,
    Competition,
    CompetitionChallenge,
    Hint,
    Tag,
    User,
    UserRole,
)
from app.schemas import ChallengeCreate, ChallengeUpdate, HintCreate
from app.security import hash_flag


def slugify(value: str) -> str:
    return value.strip().lower().replace(" ", "-")


def user_team(db: Session, user: User):
    from app.models import TeamMember

    return db.query(TeamMember).filter(TeamMember.user_id == user.id).first()


def set_tags(db: Session, challenge: Challenge, names: list[str]) -> None:
    challenge.tags.clear()
    db.flush()
    for raw in names:
        name = raw.strip().lower()
        if not name:
            continue
        tag = db.query(Tag).filter(Tag.name == name).first()
        if not tag:
            tag = Tag(name=name)
            db.add(tag)
            db.flush()
        challenge.tags.append(ChallengeTag(tag=tag))


def replace_hints(db: Session, challenge: Challenge, hints: list[HintCreate]) -> None:
    challenge.hints.clear()
    db.flush()
    for item in hints:
        challenge.hints.append(Hint(content=item.content, cost=item.cost, order_index=item.order_index))


def link_competition(db: Session, challenge: Challenge, competition_id: int | None) -> None:
    db.query(CompetitionChallenge).filter(CompetitionChallenge.challenge_id == challenge.id).delete()
    if competition_id:
        competition = db.get(Competition, competition_id)
        if not competition:
            raise ValueError("Competition not found")
        db.add(CompetitionChallenge(competition_id=competition_id, challenge_id=challenge.id))


def create_challenge(db: Session, author: User, payload: ChallengeCreate) -> Challenge:
    challenge = Challenge(
        title=payload.title,
        slug=slugify(payload.slug),
        description=payload.description,
        category=payload.category,
        difficulty=payload.difficulty,
        points=payload.points,
        flag_format=payload.flag_format,
        flag_hash=hash_flag(payload.flag),
        author_id=author.id,
        is_published=payload.is_published,
    )
    db.add(challenge)
    db.flush()
    set_tags(db, challenge, payload.tags)
    replace_hints(db, challenge, payload.hints)
    if payload.competition_id:
        link_competition(db, challenge, payload.competition_id)
    return challenge


def update_challenge(db: Session, challenge: Challenge, payload: ChallengeUpdate) -> Challenge:
    data = payload.model_dump(exclude_unset=True)
    if "flag" in data and data["flag"]:
        challenge.flag_hash = hash_flag(data.pop("flag"))
    elif "flag" in data:
        data.pop("flag")
    tags = data.pop("tags", None)
    hints = data.pop("hints", None)
    competition_id = data.pop("competition_id", None) if "competition_id" in data else ...
    for key, value in data.items():
        setattr(challenge, key, value)
    if tags is not None:
        set_tags(db, challenge, tags)
    if hints is not None:
        replace_hints(db, challenge, hints)
    if competition_id is not ...:
        link_competition(db, challenge, competition_id)
    return challenge


def can_manage_challenge(user: User, challenge: Challenge) -> bool:
    if user.role == UserRole.ADMIN:
        return True
    return user.role == UserRole.CHALLENGE_AUTHOR and challenge.author_id == user.id


def challenge_visible(challenge: Challenge, user: User | None) -> bool:
    if user and user.role in {UserRole.ADMIN, UserRole.CHALLENGE_AUTHOR}:
        if user.role == UserRole.ADMIN or challenge.author_id == user.id:
            return not challenge.is_archived or user.role == UserRole.ADMIN
    return challenge.is_published and not challenge.is_archived


def serialize_challenge(challenge: Challenge, solved: bool = False, solve_count: int = 0, include_admin: bool = False) -> dict:
    tags = [ct.tag.name for ct in challenge.tags]
    comps = [link.competition_id for link in challenge.competition_links]
    data = {
        "id": challenge.id,
        "title": challenge.title,
        "slug": challenge.slug,
        "description": challenge.description,
        "category": challenge.category.value,
        "difficulty": challenge.difficulty.value,
        "points": challenge.points,
        "tags": tags,
        "author": challenge.author.username if challenge.author else None,
        "flag_format": challenge.flag_format,
        "solve_count": solve_count,
        "solved": solved,
        "is_published": challenge.is_published,
        "created_at": challenge.created_at,
        "updated_at": challenge.updated_at,
        "competition_ids": comps,
        "attachments": [
            {"id": a.id, "original_name": a.original_name, "size_bytes": a.size_bytes}
            for a in challenge.attachments
        ],
        "hint_count": len(challenge.hints),
    }
    if include_admin:
        data["hints"] = [
            {"id": h.id, "content": h.content, "cost": h.cost, "order_index": h.order_index}
            for h in sorted(challenge.hints, key=lambda x: x.order_index)
        ]
        data["is_archived"] = challenge.is_archived
    return data
