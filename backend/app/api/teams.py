from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, get_optional_user
from app.models import (
    InvitationStatus,
    Solve,
    Team,
    TeamInvitation,
    TeamMember,
    User,
)
from app.schemas import TeamCreate, TeamInvite
from app.services.audit import write_audit
from app.services.challenges import slugify

router = APIRouter(prefix="/api/teams", tags=["teams"])


def _member_count(db: Session, team_id: int) -> int:
    return db.query(func.count(TeamMember.id)).filter(TeamMember.team_id == team_id).scalar() or 0


def _team_user_ids(db: Session, team_id: int) -> list[int]:
    return [m.user_id for m in db.query(TeamMember).filter(TeamMember.team_id == team_id).all()]


def _team_stats(db: Session, team: Team) -> dict:
    user_ids = _team_user_ids(db, team.id)
    if not user_ids:
        return {"points": 0, "solves": 0, "rank": None}
    solves = db.query(Solve).filter(Solve.user_id.in_(user_ids)).all()
    unique = {(s.challenge_id) for s in solves}
    points = db.query(func.coalesce(func.sum(User.total_points), 0)).filter(User.id.in_(user_ids)).scalar() or 0
    teams = db.query(Team).all()
    scored = []
    for t in teams:
        ids = _team_user_ids(db, t.id)
        if not ids:
            scored.append((t.id, 0, None))
            continue
        last = db.query(func.max(User.last_score_at)).filter(User.id.in_(ids)).scalar()
        pts = db.query(func.coalesce(func.sum(User.total_points), 0)).filter(User.id.in_(ids)).scalar() or 0
        scored.append((t.id, int(pts), last))
    scored.sort(key=lambda x: (-x[1], x[2] is None, x[2] or 0))
    rank = next((i + 1 for i, row in enumerate(scored) if row[0] == team.id), None)
    return {"points": int(points), "solves": len(unique), "rank": rank}


def serialize_team(db: Session, team: Team, include_invites: bool = False) -> dict:
    stats = _team_stats(db, team)
    members = (
        db.query(TeamMember)
        .options(joinedload(TeamMember.user))
        .filter(TeamMember.team_id == team.id)
        .all()
    )
    data = {
        "id": team.id,
        "name": team.name,
        "slug": team.slug,
        "description": team.description,
        "captain_id": team.captain_id,
        "captain": team.captain.username if team.captain else None,
        "members": [
            {"id": m.user.id, "username": m.user.username, "points": m.user.total_points} for m in members
        ],
        **stats,
        "created_at": team.created_at,
    }
    if include_invites:
        invites = (
            db.query(TeamInvitation)
            .options(joinedload(TeamInvitation.invitee))
            .filter(TeamInvitation.team_id == team.id, TeamInvitation.status == InvitationStatus.PENDING)
            .all()
        )
        data["invitations"] = [
            {"id": i.id, "username": i.invitee.username, "status": i.status.value} for i in invites
        ]
    return data


@router.get("")
def list_teams(db: Session = Depends(get_db)):
    teams = db.query(Team).options(joinedload(Team.captain), joinedload(Team.members)).all()
    items = [serialize_team(db, t) for t in teams]
    items.sort(key=lambda t: (-t["points"], t["rank"] or 9999))
    return {"items": items}


@router.post("")
def create_team(
    payload: TeamCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if db.query(TeamMember).filter(TeamMember.user_id == user.id).first():
        raise HTTPException(status_code=400, detail="You already belong to a team")
    slug = slugify(payload.name)
    if db.query(Team).filter((Team.name == payload.name) | (Team.slug == slug)).first():
        raise HTTPException(status_code=400, detail="Team name already taken")
    team = Team(name=payload.name, slug=slug, description=payload.description, captain_id=user.id)
    db.add(team)
    db.flush()
    db.add(TeamMember(team_id=team.id, user_id=user.id))
    write_audit(db, "team_create", "team", actor_id=user.id, resource_id=str(team.id), request=request)
    db.commit()
    db.refresh(team)
    return serialize_team(db, team, include_invites=True)


@router.get("/{team_id}")
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    include = False
    if user:
        include = team.captain_id == user.id or user.role.value == "ADMIN"
    return serialize_team(db, team, include_invites=include)


@router.post("/{team_id}/invite")
def invite(
    team_id: int,
    payload: TeamInvite,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    membership = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == user.id).first()
    if not membership or team.captain_id != user.id:
        raise HTTPException(status_code=403, detail="Only the captain can invite members")
    invitee = db.query(User).filter(User.username == payload.username).first()
    if not invitee:
        raise HTTPException(status_code=404, detail="User not found")
    if db.query(TeamMember).filter(TeamMember.user_id == invitee.id).first():
        raise HTTPException(status_code=400, detail="User already on a team")
    existing = (
        db.query(TeamInvitation)
        .filter(TeamInvitation.team_id == team.id, TeamInvitation.invitee_id == invitee.id)
        .first()
    )
    if existing and existing.status == InvitationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Invitation already pending")
    if existing:
        existing.status = InvitationStatus.PENDING
        existing.inviter_id = user.id
        invite_row = existing
    else:
        invite_row = TeamInvitation(
            team_id=team.id, inviter_id=user.id, invitee_id=invitee.id, status=InvitationStatus.PENDING
        )
        db.add(invite_row)
    write_audit(db, "team_invite", "team", actor_id=user.id, resource_id=str(team.id), request=request)
    db.commit()
    db.refresh(invite_row)
    return {"id": invite_row.id, "username": invitee.username, "status": invite_row.status.value}


@router.post("/invitations/{invitation_id}/accept")
def accept_invite(
    invitation_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    invite = db.get(TeamInvitation, invitation_id)
    if not invite or invite.invitee_id != user.id or invite.status != InvitationStatus.PENDING:
        raise HTTPException(status_code=404, detail="Invitation not found")
    if db.query(TeamMember).filter(TeamMember.user_id == user.id).first():
        raise HTTPException(status_code=400, detail="You already belong to a team")
    invite.status = InvitationStatus.ACCEPTED
    db.add(TeamMember(team_id=invite.team_id, user_id=user.id))
    write_audit(db, "team_join", "team", actor_id=user.id, resource_id=str(invite.team_id), request=request)
    db.commit()
    return {"ok": True}


@router.post("/invitations/{invitation_id}/decline")
def decline_invite(
    invitation_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    invite = db.get(TeamInvitation, invitation_id)
    if not invite or invite.invitee_id != user.id or invite.status != InvitationStatus.PENDING:
        raise HTTPException(status_code=404, detail="Invitation not found")
    invite.status = InvitationStatus.DECLINED
    db.commit()
    return {"ok": True}


@router.post("/{team_id}/leave")
def leave_team(
    team_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    membership = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == user.id).first()
    if not membership:
        raise HTTPException(status_code=400, detail="Not a member")
    if team.captain_id == user.id:
        other = (
            db.query(TeamMember)
            .filter(TeamMember.team_id == team.id, TeamMember.user_id != user.id)
            .first()
        )
        if other:
            team.captain_id = other.user_id
        else:
            db.delete(team)
            write_audit(db, "team_disband", "team", actor_id=user.id, resource_id=str(team_id), request=request)
            db.commit()
            return {"ok": True, "disbanded": True}
    db.delete(membership)
    write_audit(db, "team_leave", "team", actor_id=user.id, resource_id=str(team.id), request=request)
    db.commit()
    return {"ok": True}


@router.post("/{team_id}/members/{user_id}/remove")
def remove_member(
    team_id: int,
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    team = db.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    if team.captain_id != user.id and user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    if user_id == team.captain_id:
        raise HTTPException(status_code=400, detail="Cannot remove the captain")
    membership = db.query(TeamMember).filter(TeamMember.team_id == team.id, TeamMember.user_id == user_id).first()
    if not membership:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(membership)
    write_audit(db, "team_remove_member", "team", actor_id=user.id, resource_id=str(team.id), request=request)
    db.commit()
    return {"ok": True}
