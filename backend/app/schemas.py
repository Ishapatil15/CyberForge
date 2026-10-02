from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import Category, CompetitionMode, CompetitionVisibility, Difficulty, UserRole
from app.security import USERNAME_RE


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def username_ok(cls, v: str) -> str:
        if not USERNAME_RE.match(v):
            raise ValueError("Username must be 3-32 characters: letters, numbers, underscore")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole
    avatar_url: str | None
    bio: str | None
    total_points: int
    is_active: bool
    is_suspended: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpdate(BaseModel):
    bio: str | None = Field(default=None, max_length=280)
    avatar_url: str | None = Field(default=None, max_length=512)


class ChallengeListQuery(BaseModel):
    q: str | None = None
    category: Category | None = None
    difficulty: Difficulty | None = None
    solved: bool | None = None
    sort: str = "newest"
    page: int = 1
    page_size: int = 20


class HintCreate(BaseModel):
    content: str
    cost: int = Field(ge=0, le=10000)
    order_index: int = 1


class ChallengeCreate(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    slug: str = Field(min_length=3, max_length=180)
    description: str
    category: Category
    difficulty: Difficulty
    points: int = Field(ge=1, le=10000)
    tags: list[str] = []
    flag: str = Field(min_length=4, max_length=256)
    flag_format: str = "CF{...}"
    hints: list[HintCreate] = []
    competition_id: int | None = None
    is_published: bool = False


class ChallengeUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: Category | None = None
    difficulty: Difficulty | None = None
    points: int | None = Field(default=None, ge=1, le=10000)
    tags: list[str] | None = None
    flag: str | None = None
    flag_format: str | None = None
    hints: list[HintCreate] | None = None
    competition_id: int | None = None
    is_published: bool | None = None
    is_archived: bool | None = None


class FlagSubmit(BaseModel):
    flag: str = Field(min_length=1, max_length=256)
    competition_id: int | None = None


class TeamCreate(BaseModel):
    name: str = Field(min_length=3, max_length=64)
    description: str | None = None


class TeamInvite(BaseModel):
    username: str


class CompetitionCreate(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    slug: str = Field(min_length=3, max_length=140)
    description: str
    rules: str = ""
    mode: CompetitionMode = CompetitionMode.INDIVIDUAL
    visibility: CompetitionVisibility = CompetitionVisibility.PUBLIC
    registration_required: bool = True
    start_at: datetime
    end_at: datetime
    registration_start_at: datetime
    registration_end_at: datetime
    challenge_ids: list[int] = []


class CompetitionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    rules: str | None = None
    visibility: CompetitionVisibility | None = None
    registration_required: bool | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    registration_start_at: datetime | None = None
    registration_end_at: datetime | None = None
    challenge_ids: list[int] | None = None


class RoleUpdate(BaseModel):
    role: UserRole


class SuspendUpdate(BaseModel):
    is_suspended: bool
