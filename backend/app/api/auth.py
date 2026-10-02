from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.deps import get_current_user
from app.limiter import limiter
from app.models import User, UserRole
from app.schemas import LoginRequest, ProfileUpdate, RegisterRequest, UserPublic
from app.security import create_access_token, hash_password, verify_password
from app.services.audit import write_audit

router = APIRouter(prefix="/api/auth", tags=["auth"])


def set_session(response: Response, user_id: int) -> None:
    settings = get_settings()
    token = create_access_token(str(user_id))
    response.set_cookie(
        key=settings.cookie_name,
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.access_token_expire_minutes * 60,
        path="/",
    )


@router.post("/register", response_model=UserPublic)
def register(payload: RegisterRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == payload.username) | (User.email == payload.email)).first():
        raise HTTPException(status_code=400, detail="Username or email already in use")
    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=UserRole.USER,
    )
    db.add(user)
    db.flush()
    write_audit(db, "register", "user", actor_id=user.id, resource_id=str(user.id), request=request)
    db.commit()
    db.refresh(user)
    set_session(response, user.id)
    return user


@router.post("/login", response_model=UserPublic)
@limiter.limit("8/minute")
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        write_audit(db, "login_failure", "user", resource_id=payload.username, request=request)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.is_suspended or not user.is_active:
        raise HTTPException(status_code=403, detail="Account suspended")
    write_audit(db, "login_success", "user", actor_id=user.id, resource_id=str(user.id), request=request)
    db.commit()
    set_session(response, user.id)
    return user


@router.post("/logout")
def logout(response: Response):
    settings = get_settings()
    response.delete_cookie(settings.cookie_name, path="/")
    return {"ok": True}


@router.get("/me", response_model=UserPublic)
def me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserPublic)
def update_me(payload: ProfileUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if payload.bio is not None:
        user.bio = payload.bio
    if payload.avatar_url is not None:
        user.avatar_url = payload.avatar_url
    db.commit()
    db.refresh(user)
    return user
