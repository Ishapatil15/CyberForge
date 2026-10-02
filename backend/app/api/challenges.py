from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, get_optional_user, require_roles
from app.limiter import limiter
from app.models import (
    Attachment,
    Challenge,
    ChallengeTag,
    Competition,
    CompetitionChallenge,
    Hint,
    HintReveal,
    ScoreEvent,
    ScoreEventType,
    Solve,
    Submission,
    Tag,
    User,
    UserRole,
)
from app.schemas import FlagSubmit
from app.security import flags_match, hash_flag
from app.services.audit import write_audit
from app.services.challenges import challenge_visible, serialize_challenge
from app.services.competitions import assert_can_submit_competition
from app.services.files import attachment_path
from app.services.scoring import recompute_user_points

router = APIRouter(prefix="/api/challenges", tags=["challenges"])


def _load_challenge(db: Session, challenge_id: int) -> Challenge:
    challenge = (
        db.query(Challenge)
        .options(
            joinedload(Challenge.tags).joinedload(ChallengeTag.tag),
            joinedload(Challenge.hints),
            joinedload(Challenge.attachments),
            joinedload(Challenge.author),
            joinedload(Challenge.competition_links).joinedload(CompetitionChallenge.competition),
        )
        .filter(Challenge.id == challenge_id)
        .first()
    )
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    return challenge


def _solve_count(db: Session, challenge_id: int) -> int:
    return db.query(func.count(Solve.id)).filter(Solve.challenge_id == challenge_id).scalar() or 0


def _primary_competition(challenge: Challenge) -> Competition | None:
    if challenge.competition_links:
        return challenge.competition_links[0].competition
    return None


@router.get("")
def list_challenges(
    q: str | None = None,
    category: str | None = None,
    difficulty: str | None = None,
    solved: bool | None = None,
    sort: str = "newest",
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    query = (
        db.query(Challenge)
        .options(
            joinedload(Challenge.tags).joinedload(ChallengeTag.tag),
            joinedload(Challenge.author),
            joinedload(Challenge.competition_links),
            joinedload(Challenge.attachments),
            joinedload(Challenge.hints),
        )
        .filter(Challenge.is_archived.is_(False))
    )
    if not user or user.role == UserRole.USER:
        query = query.filter(Challenge.is_published.is_(True))
    elif user.role == UserRole.CHALLENGE_AUTHOR:
        query = query.filter(or_(Challenge.is_published.is_(True), Challenge.author_id == user.id))
    if q:
        like = f"%{q.lower()}%"
        query = (
            query.outerjoin(ChallengeTag)
            .outerjoin(Tag)
            .filter(
                or_(
                    func.lower(Challenge.title).like(like),
                    func.lower(Challenge.slug).like(like),
                    func.lower(Challenge.description).like(like),
                    func.lower(Tag.name).like(like),
                )
            )
            .distinct()
        )
    if category:
        query = query.filter(Challenge.category == category)
    if difficulty:
        query = query.filter(Challenge.difficulty == difficulty)

    challenges = query.all()
    solved_ids: set[int] = set()
    if user:
        solved_ids = {
            s.challenge_id for s in db.query(Solve).filter(Solve.user_id == user.id).all()
        }
    if solved is True:
        challenges = [c for c in challenges if c.id in solved_ids]
    elif solved is False:
        challenges = [c for c in challenges if c.id not in solved_ids]

    counts = dict(
        db.query(Solve.challenge_id, func.count(Solve.id)).group_by(Solve.challenge_id).all()
    )
    if sort == "points":
        challenges.sort(key=lambda c: (-c.points, c.id))
    elif sort == "difficulty":
        order = {"EASY": 1, "MEDIUM": 2, "HARD": 3, "EXPERT": 4}
        challenges.sort(key=lambda c: (order.get(c.difficulty.value, 0), -c.points))
    elif sort == "most_solved":
        challenges.sort(key=lambda c: (-counts.get(c.id, 0), -c.points))
    else:
        challenges.sort(key=lambda c: (c.created_at or 0), reverse=True)

    total = len(challenges)
    page = max(page, 1)
    page_size = min(max(page_size, 1), 50)
    start = (page - 1) * page_size
    items = challenges[start : start + page_size]
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            serialize_challenge(c, solved=c.id in solved_ids, solve_count=counts.get(c.id, 0))
            for c in items
        ],
    }


@router.get("/{challenge_id}")
def get_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    challenge = _load_challenge(db, challenge_id)
    if not challenge_visible(challenge, user):
        raise HTTPException(status_code=404, detail="Challenge not found")
    solved = False
    attempts = []
    revealed = set()
    if user:
        solved = db.query(Solve).filter(Solve.user_id == user.id, Solve.challenge_id == challenge.id).first() is not None
        attempts = (
            db.query(Submission)
            .filter(Submission.user_id == user.id, Submission.challenge_id == challenge.id)
            .order_by(Submission.created_at.desc())
            .limit(25)
            .all()
        )
        revealed = {
            r.hint_id
            for r in db.query(HintReveal)
            .join(Hint)
            .filter(HintReveal.user_id == user.id, Hint.challenge_id == challenge.id)
            .all()
        }
    data = serialize_challenge(challenge, solved=solved, solve_count=_solve_count(db, challenge.id))
    data["hints"] = [
        {
            "id": h.id,
            "order_index": h.order_index,
            "cost": h.cost,
            "revealed": h.id in revealed,
            "content": h.content if h.id in revealed else None,
        }
        for h in sorted(challenge.hints, key=lambda x: x.order_index)
    ]
    data["attempts"] = [
        {"id": a.id, "is_correct": a.is_correct, "created_at": a.created_at} for a in attempts
    ]
    return data


@router.post("/{challenge_id}/hints/{hint_id}/reveal")
def reveal_hint(
    challenge_id: int,
    hint_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    challenge = _load_challenge(db, challenge_id)
    if not challenge_visible(challenge, user):
        raise HTTPException(status_code=404, detail="Challenge not found")
    hint = db.get(Hint, hint_id)
    if not hint or hint.challenge_id != challenge.id:
        raise HTTPException(status_code=404, detail="Hint not found")
    existing = db.query(HintReveal).filter(HintReveal.hint_id == hint.id, HintReveal.user_id == user.id).first()
    if existing:
        return {"id": hint.id, "content": hint.content, "cost": hint.cost, "already_revealed": True}
    db.add(HintReveal(hint_id=hint.id, user_id=user.id))
    if hint.cost:
        db.add(
            ScoreEvent(
                user_id=user.id,
                challenge_id=challenge.id,
                event_type=ScoreEventType.HINT_PENALTY,
                reference_id=hint.id,
                delta=-hint.cost,
            )
        )
        db.flush()
        recompute_user_points(db, user)
    write_audit(db, "hint_reveal", "hint", actor_id=user.id, resource_id=str(hint.id), request=request)
    db.commit()
    return {"id": hint.id, "content": hint.content, "cost": hint.cost, "already_revealed": False}


@router.post("/{challenge_id}/submit")
@limiter.limit("20/minute")
def submit_flag(
    challenge_id: int,
    payload: FlagSubmit,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    challenge = _load_challenge(db, challenge_id)
    if not challenge_visible(challenge, user):
        raise HTTPException(status_code=404, detail="Challenge not found")

    competition = None
    if payload.competition_id:
        competition = db.get(Competition, payload.competition_id)
        if not competition:
            raise HTTPException(status_code=404, detail="Competition not found")
        linked = any(link.competition_id == competition.id for link in challenge.competition_links)
        if not linked:
            raise HTTPException(status_code=400, detail="Challenge is not part of this competition")
        assert_can_submit_competition(db, competition, user)

    recent_wrong = (
        db.query(func.count(Submission.id))
        .filter(
            Submission.user_id == user.id,
            Submission.challenge_id == challenge.id,
            Submission.is_correct.is_(False),
        )
        .scalar()
        or 0
    )
    if recent_wrong >= 40:
        raise HTTPException(status_code=429, detail="Too many incorrect attempts for this challenge")

    correct = flags_match(payload.flag, challenge.flag_hash)
    submission = Submission(
        user_id=user.id,
        challenge_id=challenge.id,
        competition_id=competition.id if competition else None,
        is_correct=correct,
        submitted_flag_hash=hash_flag(payload.flag),
    )
    db.add(submission)

    already = db.query(Solve).filter(Solve.user_id == user.id, Solve.challenge_id == challenge.id).first()
    awarded = 0
    if correct and not already:
        solve = Solve(
            user_id=user.id,
            challenge_id=challenge.id,
            competition_id=competition.id if competition else None,
            points_awarded=challenge.points,
        )
        db.add(solve)
        db.add(
            ScoreEvent(
                user_id=user.id,
                challenge_id=challenge.id,
                competition_id=competition.id if competition else None,
                event_type=ScoreEventType.SOLVE,
                reference_id=challenge.id,
                delta=challenge.points,
            )
        )
        awarded = challenge.points
        db.flush()
        recompute_user_points(db, user)

    write_audit(
        db,
        "flag_submit",
        "challenge",
        actor_id=user.id,
        resource_id=str(challenge.id),
        request=request,
        metadata={"correct": correct, "duplicate": bool(already and correct)},
    )
    db.commit()
    return {
        "correct": correct,
        "already_solved": bool(already),
        "points_awarded": awarded if correct and not already else 0,
        "total_points": user.total_points,
        "message": "Correct flag" if correct else "Incorrect flag",
    }


@router.get("/{challenge_id}/attachments/{attachment_id}")
def download_attachment(
    challenge_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    challenge = _load_challenge(db, challenge_id)
    if not challenge_visible(challenge, user):
        raise HTTPException(status_code=404, detail="Challenge not found")
    attachment = db.get(Attachment, attachment_id)
    if not attachment or attachment.challenge_id != challenge.id:
        raise HTTPException(status_code=404, detail="Attachment not found")
    path = attachment_path(attachment.stored_name)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing")
    return FileResponse(path, filename=attachment.original_name, media_type=attachment.content_type)
