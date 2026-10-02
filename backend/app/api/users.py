from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user
from app.models import Challenge, CompetitionParticipant, InvitationStatus, Solve, Submission, TeamInvitation, TeamMember, User
from app.services.scoring import global_rank

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me/profile")
def my_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    solved = db.query(func.count(Solve.id)).filter(Solve.user_id == user.id).scalar() or 0
    attempted = (
        db.query(func.count(func.distinct(Submission.challenge_id)))
        .filter(Submission.user_id == user.id)
        .scalar()
        or 0
    )
    membership = (
        db.query(TeamMember)
        .options(joinedload(TeamMember.team))
        .filter(TeamMember.user_id == user.id)
        .first()
    )
    competitions = (
        db.query(CompetitionParticipant)
        .options(joinedload(CompetitionParticipant.competition))
        .filter(CompetitionParticipant.user_id == user.id)
        .all()
    )
    if membership:
        team_comps = (
            db.query(CompetitionParticipant)
            .options(joinedload(CompetitionParticipant.competition))
            .filter(CompetitionParticipant.team_id == membership.team_id)
            .all()
        )
        competitions = competitions + team_comps
    invites = (
        db.query(TeamInvitation)
        .options(joinedload(TeamInvitation.team))
        .filter(TeamInvitation.invitee_id == user.id, TeamInvitation.status == InvitationStatus.PENDING)
        .all()
    )
    category_rows = (
        db.query(Challenge.category, func.count(Solve.id))
        .join(Solve, Solve.challenge_id == Challenge.id)
        .filter(Solve.user_id == user.id)
        .group_by(Challenge.category)
        .all()
    )
    recent = (
        db.query(Submission)
        .options(joinedload(Submission.challenge))
        .filter(Submission.user_id == user.id)
        .order_by(Submission.created_at.desc())
        .limit(8)
        .all()
    )
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "total_points": user.total_points,
            "created_at": user.created_at,
        },
        "rank": global_rank(db, user),
        "solved": solved,
        "attempted": attempted,
        "team": {"id": membership.team.id, "name": membership.team.name} if membership else None,
        "competitions": [
            {"id": p.competition.id, "name": p.competition.name} for p in competitions if p.competition
        ],
        "invitations": [
            {"id": i.id, "team_id": i.team_id, "team_name": i.team.name} for i in invites
        ],
        "progress_by_category": [{"category": c.value, "solved": n} for c, n in category_rows],
        "recent_submissions": [
            {
                "id": s.id,
                "challenge_id": s.challenge_id,
                "challenge_title": s.challenge.title if s.challenge else None,
                "is_correct": s.is_correct,
                "created_at": s.created_at,
            }
            for s in recent
        ],
    }


@router.get("/me/submissions")
def my_submissions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    submissions = (
        db.query(Submission)
        .options(joinedload(Submission.challenge))
        .filter(Submission.user_id == user.id)
        .order_by(Submission.created_at.asc())
        .all()
    )
    grouped: dict[int, dict] = {}
    for s in submissions:
        row = grouped.setdefault(
            s.challenge_id,
            {
                "challenge_id": s.challenge_id,
                "challenge": s.challenge.title if s.challenge else None,
                "category": s.challenge.category.value if s.challenge else None,
                "attempts": 0,
                "status": "Incorrect",
                "first_attempt": s.created_at,
                "solved_at": None,
            },
        )
        row["attempts"] += 1
        if s.is_correct and row["solved_at"] is None:
            row["status"] = "Correct"
            row["solved_at"] = s.created_at
    return {"items": list(grouped.values())}


@router.get("/me/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    profile = my_profile(db, user)
    from app.api.competitions import serialize_competition
    from app.models import Competition
    from app.services.competitions import competition_status
    from app.services.challenges import serialize_challenge

    comps = db.query(Competition).all()
    active = [c for c in comps if competition_status(c) in {"ACTIVE", "REGISTRATION_OPEN"}]
    recent_challenges = (
        db.query(Challenge)
        .filter(Challenge.is_published.is_(True), Challenge.is_archived.is_(False))
        .order_by(Challenge.created_at.desc())
        .limit(6)
        .all()
    )
    solved_ids = {s.challenge_id for s in db.query(Solve).filter(Solve.user_id == user.id).all()}
    recommended = (
        db.query(Challenge)
        .filter(
            Challenge.is_published.is_(True),
            Challenge.is_archived.is_(False),
            ~Challenge.id.in_(solved_ids or {0}),
        )
        .order_by(Challenge.points.asc())
        .limit(6)
        .all()
    )
    return {
        **profile,
        "active_competitions": [serialize_competition(db, c, user) for c in active],
        "recent_challenges": [serialize_challenge(c, solved=c.id in solved_ids) for c in recent_challenges],
        "recommended_challenges": [serialize_challenge(c, solved=False) for c in recommended],
    }


@router.get("/{user_id}/public")
def public_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user or user.is_suspended:
        raise HTTPException(status_code=404, detail="User not found")
    solved = db.query(func.count(Solve.id)).filter(Solve.user_id == user.id).scalar() or 0
    return {
        "id": user.id,
        "username": user.username,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "total_points": user.total_points,
        "rank": global_rank(db, user),
        "solved": solved,
        "role": user.role.value,
    }
