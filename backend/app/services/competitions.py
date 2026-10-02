from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import (
    Competition,
    CompetitionMode,
    CompetitionParticipant,
    TeamMember,
    User,
)


def competition_status(comp: Competition, now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    start = comp.start_at if comp.start_at.tzinfo else comp.start_at.replace(tzinfo=timezone.utc)
    end = comp.end_at if comp.end_at.tzinfo else comp.end_at.replace(tzinfo=timezone.utc)
    reg_start = (
        comp.registration_start_at
        if comp.registration_start_at.tzinfo
        else comp.registration_start_at.replace(tzinfo=timezone.utc)
    )
    reg_end = (
        comp.registration_end_at
        if comp.registration_end_at.tzinfo
        else comp.registration_end_at.replace(tzinfo=timezone.utc)
    )
    if now < start:
        if reg_start <= now <= reg_end:
            return "REGISTRATION_OPEN"
        return "UPCOMING"
    if now > end:
        return "COMPLETED"
    return "ACTIVE"


def is_registered(db: Session, competition: Competition, user: User) -> bool:
    if competition.mode == CompetitionMode.INDIVIDUAL:
        return (
            db.query(CompetitionParticipant)
            .filter(
                CompetitionParticipant.competition_id == competition.id,
                CompetitionParticipant.user_id == user.id,
            )
            .first()
            is not None
        )
    membership = db.query(TeamMember).filter(TeamMember.user_id == user.id).first()
    if not membership:
        return False
    return (
        db.query(CompetitionParticipant)
        .filter(
            CompetitionParticipant.competition_id == competition.id,
            CompetitionParticipant.team_id == membership.team_id,
        )
        .first()
        is not None
    )


def assert_can_submit_competition(db: Session, competition: Competition | None, user: User) -> None:
    if competition is None:
        return
    now = datetime.now(timezone.utc)
    status_name = competition_status(competition, now)
    if status_name != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Competition is not currently active",
        )
    if competition.registration_required and not is_registered(db, competition, user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must be registered for this competition",
        )
