import json

from fastapi import Request
from sqlalchemy.orm import Session

from app.models import AuditLog


def client_ip(request: Request | None) -> str | None:
    if request is None:
        return None
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def write_audit(
    db: Session,
    action: str,
    resource_type: str,
    actor_id: int | None = None,
    resource_id: str | None = None,
    request: Request | None = None,
    metadata: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=client_ip(request),
            metadata_json=json.dumps(metadata) if metadata else None,
        )
    )
