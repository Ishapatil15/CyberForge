from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("/global")
def global_leaderboard(db: Session = Depends(get_db), page: int = 1, page_size: int = 50):
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
    total = len(users)
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    start = (page - 1) * page_size
    slice_ = users[start : start + page_size]
    items = []
    for i, user in enumerate(slice_, start=start + 1):
        items.append(
            {
                "rank": i,
                "user_id": user.id,
                "username": user.username,
                "points": user.total_points,
                "solves": len(user.submissions) if False else None,
                "last_score_at": user.last_score_at,
            }
        )
    from sqlalchemy import func
    from app.models import Solve, Submission

    solve_counts = dict(db.query(Solve.user_id, func.count(Solve.id)).group_by(Solve.user_id).all())
    attempt_counts = dict(db.query(Submission.user_id, func.count(Submission.id)).group_by(Submission.user_id).all())
    for item in items:
        uid = item["user_id"]
        solves = solve_counts.get(uid, 0)
        attempts = attempt_counts.get(uid, 0)
        acc = f"{round((solves / attempts) * 100)}%" if attempts > 0 else "100%"
        item["solves"] = solves
        item["attempts"] = attempts
        item["accuracy"] = acc
    return {"total": total, "page": page, "page_size": page_size, "items": items}
