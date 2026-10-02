from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models import User


def recompute_user_points(db: Session, user: User) -> None:
    from sqlalchemy import func
    from app.models import ScoreEvent, Solve

    total = db.query(func.coalesce(func.sum(ScoreEvent.delta), 0)).filter(ScoreEvent.user_id == user.id).scalar()
    last = db.query(func.max(Solve.solved_at)).filter(Solve.user_id == user.id).scalar()
    user.total_points = max(0, int(total or 0))
    user.last_score_at = last


def global_rank(db: Session, user: User) -> int:
    users = (
        db.query(User)
        .filter(User.is_active.is_(True), User.is_suspended.is_(False))
        .all()
    )
    users.sort(
        key=lambda u: (
            -u.total_points,
            u.last_score_at is None,
            u.last_score_at or datetime.max.replace(tzinfo=timezone.utc),
            u.username.lower(),
        )
    )
    for i, u in enumerate(users, start=1):
        if u.id == user.id:
            return i
    return len(users) + 1
