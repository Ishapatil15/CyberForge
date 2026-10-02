from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, get_optional_user
from app.models import (
    Challenge,
    Competition,
    CompetitionChallenge,
    CompetitionMode,
    CompetitionParticipant,
    Solve,
    TeamMember,
    User,
)
from app.services.challenges import serialize_challenge
from app.services.competitions import competition_status, is_registered
from app.services.audit import write_audit

router = APIRouter(prefix="/api/competitions", tags=["competitions"])


def _aware(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def serialize_competition(db: Session, comp: Competition, user: User | None) -> dict:
    status_name = competition_status(comp)
    challenge_ids = [link.challenge_id for link in comp.challenges]
    participant_count = db.query(func.count(CompetitionParticipant.id)).filter(
        CompetitionParticipant.competition_id == comp.id
    ).scalar() or 0
    registered = is_registered(db, comp, user) if user else False
    my_score = None
    my_rank = None
    if user and registered:
        board = _leaderboard(db, comp)
        for row in board:
            if comp.mode == CompetitionMode.INDIVIDUAL and row.get("user_id") == user.id:
                my_score = row["points"]
                my_rank = row["rank"]
                break
            if comp.mode == CompetitionMode.TEAM:
                membership = db.query(TeamMember).filter(TeamMember.user_id == user.id).first()
                if membership and row.get("team_id") == membership.team_id:
                    my_score = row["points"]
                    my_rank = row["rank"]
                    break
    return {
        "id": comp.id,
        "name": comp.name,
        "slug": comp.slug,
        "description": comp.description,
        "rules": comp.rules,
        "mode": comp.mode.value,
        "visibility": comp.visibility.value,
        "registration_required": comp.registration_required,
        "start_at": comp.start_at,
        "end_at": comp.end_at,
        "registration_start_at": comp.registration_start_at,
        "registration_end_at": comp.registration_end_at,
        "status": status_name,
        "participant_count": participant_count,
        "challenge_count": len(challenge_ids),
        "registered": registered,
        "my_score": my_score,
        "my_rank": my_rank,
        "server_now": datetime.now(timezone.utc),
    }


def _leaderboard(db: Session, comp: Competition) -> list[dict]:
    if comp.mode == CompetitionMode.INDIVIDUAL:
        participants = (
            db.query(CompetitionParticipant)
            .options(joinedload(CompetitionParticipant.user))
            .filter(CompetitionParticipant.competition_id == comp.id, CompetitionParticipant.user_id.is_not(None))
            .all()
        )
        rows = []
        for p in participants:
            solves = (
                db.query(Solve)
                .filter(Solve.user_id == p.user_id, Solve.competition_id == comp.id)
                .all()
            )
            points = sum(s.points_awarded for s in solves)
            last = max((s.solved_at for s in solves), default=None)
            rows.append(
                {
                    "user_id": p.user_id,
                    "username": p.user.username if p.user else None,
                    "points": points,
                    "solves": len(solves),
                    "last_solve_at": last,
                }
            )
        rows.sort(key=lambda r: (-r["points"], r["last_solve_at"] is None, r["last_solve_at"] or datetime.max.replace(tzinfo=timezone.utc)))
        for i, row in enumerate(rows, start=1):
            row["rank"] = i
        return rows

    participants = (
        db.query(CompetitionParticipant)
        .options(joinedload(CompetitionParticipant.team))
        .filter(CompetitionParticipant.competition_id == comp.id, CompetitionParticipant.team_id.is_not(None))
        .all()
    )
    rows = []
    for p in participants:
        member_ids = [m.user_id for m in db.query(TeamMember).filter(TeamMember.team_id == p.team_id).all()]
        if not member_ids:
            rows.append({"team_id": p.team_id, "team_name": p.team.name if p.team else None, "points": 0, "solves": 0, "last_solve_at": None})
            continue
        solves = (
            db.query(Solve)
            .filter(Solve.user_id.in_(member_ids), Solve.competition_id == comp.id)
            .all()
        )
        unique = {}
        for s in solves:
            prev = unique.get(s.challenge_id)
            if not prev or s.solved_at < prev.solved_at:
                unique[s.challenge_id] = s
        points = sum(s.points_awarded for s in unique.values())
        last = max((s.solved_at for s in unique.values()), default=None)
        rows.append(
            {
                "team_id": p.team_id,
                "team_name": p.team.name if p.team else None,
                "points": points,
                "solves": len(unique),
                "last_solve_at": last,
            }
        )
    rows.sort(key=lambda r: (-r["points"], r["last_solve_at"] is None, r["last_solve_at"] or datetime.max.replace(tzinfo=timezone.utc)))
    for i, row in enumerate(rows, start=1):
        row["rank"] = i
    return rows


@router.get("")
def list_competitions(db: Session = Depends(get_db), user: User | None = Depends(get_optional_user)):
    comps = (
        db.query(Competition)
        .options(joinedload(Competition.challenges), joinedload(Competition.participants))
        .all()
    )
    return {"items": [serialize_competition(db, c, user) for c in comps]}


@router.get("/{competition_id}")
def get_competition(
    competition_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    comp = (
        db.query(Competition)
        .options(joinedload(Competition.challenges).joinedload(CompetitionChallenge.challenge))
        .filter(Competition.id == competition_id)
        .first()
    )
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
    data = serialize_competition(db, comp, user)
    status_name = data["status"]
    show_challenges = status_name in {"ACTIVE", "COMPLETED"} or (user and user.role.value == "ADMIN")
    solved_ids = set()
    if user:
        solved_ids = {s.challenge_id for s in db.query(Solve).filter(Solve.user_id == user.id).all()}
    if show_challenges:
        challenges = [link.challenge for link in comp.challenges if link.challenge and link.challenge.is_published]
        data["challenges"] = [
            serialize_challenge(c, solved=c.id in solved_ids)
            for c in challenges
        ]
    else:
        data["challenges"] = []
    return data


@router.post("/{competition_id}/register")
def register(
    competition_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    comp = db.get(Competition, competition_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
    now = datetime.now(timezone.utc)
    if not (_aware(comp.registration_start_at) <= now <= _aware(comp.registration_end_at)):
        raise HTTPException(status_code=403, detail="Registration is closed")
    if is_registered(db, comp, user):
        raise HTTPException(status_code=400, detail="Already registered")
    if comp.mode == CompetitionMode.INDIVIDUAL:
        db.add(CompetitionParticipant(competition_id=comp.id, user_id=user.id))
    else:
        membership = db.query(TeamMember).filter(TeamMember.user_id == user.id).first()
        if not membership:
            raise HTTPException(status_code=400, detail="Join a team before registering")
        team = membership.team
        if team.captain_id != user.id:
            raise HTTPException(status_code=403, detail="Only the team captain can register")
        db.add(CompetitionParticipant(competition_id=comp.id, team_id=team.id))
    write_audit(db, "competition_register", "competition", actor_id=user.id, resource_id=str(comp.id), request=request)
    db.commit()
    return {"ok": True}


@router.get("/{competition_id}/leaderboard")
def competition_leaderboard(competition_id: int, db: Session = Depends(get_db)):
    comp = db.get(Competition, competition_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
    return {"items": _leaderboard(db, comp)}
