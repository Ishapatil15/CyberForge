from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import require_roles
from app.models import (
    Attachment,
    AuditLog,
    Challenge,
    ChallengeTag,
    Competition,
    CompetitionChallenge,
    Solve,
    Submission,
    Team,
    TeamMember,
    User,
    UserRole,
)
from app.schemas import ChallengeCreate, ChallengeUpdate, CompetitionCreate, CompetitionUpdate, RoleUpdate, SuspendUpdate
from app.security import hash_flag
from app.services.audit import write_audit
from app.services.challenges import can_manage_challenge, create_challenge, serialize_challenge, update_challenge
from app.services.files import save_upload, validate_upload
from app.services.challenges import slugify

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _admin_or_author(user: User = Depends(require_roles(UserRole.ADMIN, UserRole.CHALLENGE_AUTHOR))) -> User:
    return user


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN))):
    from app.services.competitions import competition_status

    comps = db.query(Competition).all()
    return {
        "total_users": db.query(func.count(User.id)).scalar() or 0,
        "active_users": db.query(func.count(User.id)).filter(User.is_active.is_(True), User.is_suspended.is_(False)).scalar()
        or 0,
        "total_challenges": db.query(func.count(Challenge.id)).filter(Challenge.is_archived.is_(False)).scalar() or 0,
        "published_challenges": db.query(func.count(Challenge.id)).filter(Challenge.is_published.is_(True)).scalar() or 0,
        "total_competitions": len(comps),
        "active_competitions": sum(1 for c in comps if competition_status(c) == "ACTIVE"),
        "total_submissions": db.query(func.count(Submission.id)).scalar() or 0,
        "total_solves": db.query(func.count(Solve.id)).scalar() or 0,
        "total_teams": db.query(func.count(Team.id)).scalar() or 0,
    }


@router.get("/users")
def list_users(
    q: str | None = None,
    page: int = 1,
    page_size: int = 30,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN)),
):
    query = db.query(User)
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(or_(func.lower(User.username).like(like), func.lower(User.email).like(like)))
    total = query.count()
    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    items = query.order_by(User.id.asc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "items": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "role": u.role.value,
                "total_points": u.total_points,
                "is_suspended": u.is_suspended,
                "created_at": u.created_at,
            }
            for u in items
        ],
    }


@router.patch("/users/{user_id}/role")
def change_role(
    user_id: int,
    payload: RoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles(UserRole.ADMIN)),
):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == admin.id and payload.role != UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="Cannot demote yourself")
    target.role = payload.role
    write_audit(
        db,
        "user_role_change",
        "user",
        actor_id=admin.id,
        resource_id=str(target.id),
        request=request,
        metadata={"role": payload.role.value},
    )
    db.commit()
    return {"ok": True, "role": target.role.value}


@router.patch("/users/{user_id}/suspend")
def suspend_user(
    user_id: int,
    payload: SuspendUpdate,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles(UserRole.ADMIN)),
):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot suspend yourself")
    target.is_suspended = payload.is_suspended
    write_audit(
        db,
        "user_suspend" if payload.is_suspended else "user_unsuspend",
        "user",
        actor_id=admin.id,
        resource_id=str(target.id),
        request=request,
    )
    db.commit()
    return {"ok": True}


@router.get("/challenges")
def admin_challenges(
    db: Session = Depends(get_db),
    user: User = Depends(_admin_or_author),
):
    query = (
        db.query(Challenge)
        .options(
            joinedload(Challenge.tags).joinedload(ChallengeTag.tag),
            joinedload(Challenge.author),
            joinedload(Challenge.hints),
            joinedload(Challenge.attachments),
            joinedload(Challenge.competition_links),
        )
    )
    if user.role != UserRole.ADMIN:
        query = query.filter(Challenge.is_archived.is_(False), Challenge.author_id == user.id)
    items = query.order_by(Challenge.created_at.desc()).all()
    return {"items": [serialize_challenge(c, include_admin=True) for c in items]}


@router.post("/challenges")
def create(
    payload: ChallengeCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(_admin_or_author),
):
    if db.query(Challenge).filter(Challenge.slug == slugify(payload.slug)).first():
        raise HTTPException(status_code=400, detail="Slug already exists")
    challenge = create_challenge(db, user, payload)
    write_audit(db, "challenge_create", "challenge", actor_id=user.id, resource_id=str(challenge.id), request=request)
    db.commit()
    db.refresh(challenge)
    return serialize_challenge(
        db.query(Challenge)
        .options(
            joinedload(Challenge.tags).joinedload(ChallengeTag.tag),
            joinedload(Challenge.author),
            joinedload(Challenge.hints),
            joinedload(Challenge.attachments),
            joinedload(Challenge.competition_links),
        )
        .filter(Challenge.id == challenge.id)
        .first(),
        include_admin=True,
    )


@router.get("/challenges/{challenge_id}")
def get_admin_challenge(
    challenge_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(_admin_or_author),
):
    challenge = (
        db.query(Challenge)
        .options(
            joinedload(Challenge.tags).joinedload(ChallengeTag.tag),
            joinedload(Challenge.hints),
            joinedload(Challenge.attachments),
            joinedload(Challenge.author),
            joinedload(Challenge.competition_links),
        )
        .filter(Challenge.id == challenge_id)
        .first()
    )
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if not can_manage_challenge(user, challenge):
        raise HTTPException(status_code=403, detail="Not authorized")
    return serialize_challenge(challenge, include_admin=True)


@router.patch("/challenges/{challenge_id}")
def patch_challenge(
    challenge_id: int,
    payload: ChallengeUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(_admin_or_author),
):
    challenge = (
        db.query(Challenge)
        .options(
            joinedload(Challenge.tags).joinedload(ChallengeTag.tag),
            joinedload(Challenge.hints),
            joinedload(Challenge.attachments),
            joinedload(Challenge.author),
            joinedload(Challenge.competition_links),
        )
        .filter(Challenge.id == challenge_id)
        .first()
    )
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if not can_manage_challenge(user, challenge):
        raise HTTPException(status_code=403, detail="Not authorized")
    try:
        update_challenge(db, challenge, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    write_audit(db, "challenge_update", "challenge", actor_id=user.id, resource_id=str(challenge.id), request=request)
    db.commit()
    db.refresh(challenge)
    return serialize_challenge(challenge, include_admin=True)


@router.delete("/challenges/{challenge_id}")
def archive_challenge(
    challenge_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(_admin_or_author),
):
    challenge = db.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if not can_manage_challenge(user, challenge):
        raise HTTPException(status_code=403, detail="Not authorized")
    challenge.is_archived = True
    challenge.is_published = False
    write_audit(db, "challenge_archive", "challenge", actor_id=user.id, resource_id=str(challenge.id), request=request)
    db.commit()
    return {"ok": True}


@router.post("/challenges/{challenge_id}/attachments")
def upload_attachment(
    challenge_id: int,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(_admin_or_author),
):
    challenge = db.get(Challenge, challenge_id)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    if not can_manage_challenge(user, challenge):
        raise HTTPException(status_code=403, detail="Not authorized")
    stored, content_type = validate_upload(file)
    size = save_upload(file, stored)
    attachment = Attachment(
        challenge_id=challenge.id,
        original_name=file.filename or stored,
        stored_name=stored,
        content_type=content_type,
        size_bytes=size,
    )
    db.add(attachment)
    write_audit(db, "attachment_upload", "challenge", actor_id=user.id, resource_id=str(challenge.id), request=request)
    db.commit()
    db.refresh(attachment)
    return {"id": attachment.id, "original_name": attachment.original_name, "size_bytes": attachment.size_bytes}


@router.get("/submissions")
def admin_submissions(
    q: str | None = None,
    page: int = 1,
    page_size: int = 40,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN)),
):
    query = db.query(Submission).options(
        joinedload(Submission.user), joinedload(Submission.challenge), joinedload(Submission.competition)
    )
    if q:
        like = f"%{q.lower()}%"
        query = query.join(User, Submission.user_id == User.id).filter(func.lower(User.username).like(like))
    total = query.count()
    page = max(page, 1)
    items = (
        query.order_by(Submission.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "items": [
            {
                "id": s.id,
                "username": s.user.username if s.user else None,
                "challenge": s.challenge.title if s.challenge else None,
                "competition": s.competition.name if s.competition else None,
                "is_correct": s.is_correct,
                "created_at": s.created_at,
            }
            for s in items
        ],
    }


@router.get("/activity")
def activity(
    page: int = 1,
    page_size: int = 40,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN)),
):
    query = db.query(AuditLog).options(joinedload(AuditLog.actor))
    total = query.count()
    items = (
        query.order_by(AuditLog.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "items": [
            {
                "id": a.id,
                "actor": a.actor.username if a.actor else None,
                "action": a.action,
                "resource_type": a.resource_type,
                "resource_id": a.resource_id,
                "ip_address": a.ip_address,
                "created_at": a.created_at,
            }
            for a in items
        ],
    }


@router.get("/teams")
def admin_teams(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN))):
    from app.api.teams import serialize_team

    teams = db.query(Team).options(joinedload(Team.captain), joinedload(Team.members)).all()
    return {"items": [serialize_team(db, t, include_invites=True) for t in teams]}


@router.post("/competitions")
def create_competition(
    payload: CompetitionCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN)),
):
    if db.query(Competition).filter(Competition.slug == slugify(payload.slug)).first():
        raise HTTPException(status_code=400, detail="Slug already exists")
    if payload.end_at <= payload.start_at:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    comp = Competition(
        name=payload.name,
        slug=slugify(payload.slug),
        description=payload.description,
        rules=payload.rules,
        mode=payload.mode,
        visibility=payload.visibility,
        registration_required=payload.registration_required,
        start_at=payload.start_at,
        end_at=payload.end_at,
        registration_start_at=payload.registration_start_at,
        registration_end_at=payload.registration_end_at,
    )
    db.add(comp)
    db.flush()
    for cid in payload.challenge_ids:
        if not db.get(Challenge, cid):
            raise HTTPException(status_code=400, detail=f"Challenge {cid} not found")
        db.add(CompetitionChallenge(competition_id=comp.id, challenge_id=cid))
    write_audit(db, "competition_create", "competition", actor_id=user.id, resource_id=str(comp.id), request=request)
    db.commit()
    db.refresh(comp)
    return {"id": comp.id, "slug": comp.slug, "name": comp.name}


@router.patch("/competitions/{competition_id}")
def update_competition(
    competition_id: int,
    payload: CompetitionUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN)),
):
    comp = db.get(Competition, competition_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Competition not found")
    data = payload.model_dump(exclude_unset=True)
    ids = data.pop("challenge_ids", None)
    for key, value in data.items():
        setattr(comp, key, value)
    if ids is not None:
        db.query(CompetitionChallenge).filter(CompetitionChallenge.competition_id == comp.id).delete()
        for cid in ids:
            db.add(CompetitionChallenge(competition_id=comp.id, challenge_id=cid))
    write_audit(db, "competition_update", "competition", actor_id=user.id, resource_id=str(comp.id), request=request)
    db.commit()
    return {"ok": True}


@router.get("/competitions")
def admin_competitions(db: Session = Depends(get_db), user: User = Depends(require_roles(UserRole.ADMIN))):
    from app.api.competitions import serialize_competition

    comps = db.query(Competition).options(joinedload(Competition.challenges)).all()
    return {"items": [serialize_competition(db, c, user) for c in comps]}
