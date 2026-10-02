from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.api import admin, auth, challenges, competitions, labs, leaderboard, teams, users
from app.config import get_settings
from app.limiter import limiter

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(status_code=429, content={"detail": "Too many requests"})


app.include_router(auth.router)
app.include_router(challenges.router)
app.include_router(labs.router)
app.include_router(teams.router)
app.include_router(competitions.router)
app.include_router(leaderboard.router)
app.include_router(users.router)
app.include_router(admin.router)


@app.get("/api/health")
def health():
    return {"ok": True, "name": settings.app_name}


@app.get("/api/stats")
def public_stats(db=Depends(challenges.get_db)):
    from sqlalchemy import func
    from app.models import Challenge, Competition, Solve, User

    return {
        "active_challenges": db.query(func.count(Challenge.id)).filter(Challenge.is_published.is_(True), Challenge.is_archived.is_(False)).scalar() or 0,
        "registered_players": db.query(func.count(User.id)).filter(User.is_active.is_(True), User.is_suspended.is_(False)).scalar() or 0,
        "competitions": db.query(func.count(Competition.id)).scalar() or 0,
        "challenges_solved": db.query(func.count(Solve.id)).scalar() or 0,
    }
