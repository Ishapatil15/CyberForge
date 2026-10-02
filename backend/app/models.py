from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    USER = "USER"
    CHALLENGE_AUTHOR = "CHALLENGE_AUTHOR"
    ADMIN = "ADMIN"


class Difficulty(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"
    EXPERT = "EXPERT"


class Category(str, enum.Enum):
    WEB = "WEB"
    CRYPTOGRAPHY = "CRYPTOGRAPHY"
    FORENSICS = "FORENSICS"
    REVERSE_ENGINEERING = "REVERSE_ENGINEERING"
    OSINT = "OSINT"
    STEGANOGRAPHY = "STEGANOGRAPHY"
    BINARY_EXPLOITATION = "BINARY_EXPLOITATION"
    NETWORKING = "NETWORKING"
    MOBILE = "MOBILE"
    MISCELLANEOUS = "MISCELLANEOUS"


class CompetitionMode(str, enum.Enum):
    INDIVIDUAL = "INDIVIDUAL"
    TEAM = "TEAM"


class CompetitionVisibility(str, enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


class ScoreEventType(str, enum.Enum):
    SOLVE = "SOLVE"
    HINT_PENALTY = "HINT_PENALTY"


class InvitationStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    DECLINED = "DECLINED"
    REVOKED = "REVOKED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(280), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_suspended: Mapped[bool] = mapped_column(Boolean, default=False)
    total_points: Mapped[int] = mapped_column(Integer, default=0, index=True)
    last_score_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    team_memberships: Mapped[list[TeamMember]] = relationship(back_populates="user")
    submissions: Mapped[list[Submission]] = relationship(back_populates="user")


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    captain_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    captain: Mapped[User] = relationship(foreign_keys=[captain_id])
    members: Mapped[list[TeamMember]] = relationship(back_populates="team", cascade="all, delete-orphan")
    invitations: Mapped[list[TeamInvitation]] = relationship(back_populates="team", cascade="all, delete-orphan")


class TeamMember(Base):
    __tablename__ = "team_members"
    __table_args__ = (UniqueConstraint("team_id", "user_id", name="uq_team_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    team: Mapped[Team] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="team_memberships")


class TeamInvitation(Base):
    __tablename__ = "team_invitations"
    __table_args__ = (UniqueConstraint("team_id", "invitee_id", name="uq_team_invitee"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), index=True)
    inviter_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    invitee_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    status: Mapped[InvitationStatus] = mapped_column(Enum(InvitationStatus), default=InvitationStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    team: Mapped[Team] = relationship(back_populates="invitations")
    invitee: Mapped[User] = relationship(foreign_keys=[invitee_id])
    inviter: Mapped[User] = relationship(foreign_keys=[inviter_id])


class Competition(Base):
    __tablename__ = "competitions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    rules: Mapped[str] = mapped_column(Text, default="")
    mode: Mapped[CompetitionMode] = mapped_column(Enum(CompetitionMode), default=CompetitionMode.INDIVIDUAL)
    visibility: Mapped[CompetitionVisibility] = mapped_column(
        Enum(CompetitionVisibility), default=CompetitionVisibility.PUBLIC
    )
    registration_required: Mapped[bool] = mapped_column(Boolean, default=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    registration_start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    registration_end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    challenges: Mapped[list[CompetitionChallenge]] = relationship(
        back_populates="competition", cascade="all, delete-orphan"
    )
    participants: Mapped[list[CompetitionParticipant]] = relationship(
        back_populates="competition", cascade="all, delete-orphan"
    )


class CompetitionChallenge(Base):
    __tablename__ = "competition_challenges"
    __table_args__ = (UniqueConstraint("competition_id", "challenge_id", name="uq_comp_challenge"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id", ondelete="CASCADE"), index=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id", ondelete="CASCADE"), index=True)

    competition: Mapped[Competition] = relationship(back_populates="challenges")
    challenge: Mapped[Challenge] = relationship(back_populates="competition_links")


class CompetitionParticipant(Base):
    __tablename__ = "competition_participants"
    __table_args__ = (
        UniqueConstraint("competition_id", "user_id", name="uq_comp_user"),
        UniqueConstraint("competition_id", "team_id", name="uq_comp_team"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    competition: Mapped[Competition] = relationship(back_populates="participants")
    user: Mapped[User | None] = relationship()
    team: Mapped[Team | None] = relationship()


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    slug: Mapped[str] = mapped_column(String(180), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text)
    category: Mapped[Category] = mapped_column(Enum(Category), index=True)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), index=True)
    points: Mapped[int] = mapped_column(Integer)
    flag_format: Mapped[str] = mapped_column(String(80), default="CTF{...}")
    flag_hash: Mapped[str] = mapped_column(String(128))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"))
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    author: Mapped[User] = relationship()
    tags: Mapped[list[ChallengeTag]] = relationship(back_populates="challenge", cascade="all, delete-orphan")
    hints: Mapped[list[Hint]] = relationship(back_populates="challenge", cascade="all, delete-orphan")
    attachments: Mapped[list[Attachment]] = relationship(back_populates="challenge", cascade="all, delete-orphan")
    competition_links: Mapped[list[CompetitionChallenge]] = relationship(back_populates="challenge")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True, index=True)


class ChallengeTag(Base):
    __tablename__ = "challenge_tags"
    __table_args__ = (UniqueConstraint("challenge_id", "tag_id", name="uq_challenge_tag"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id", ondelete="CASCADE"), index=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id", ondelete="CASCADE"), index=True)

    challenge: Mapped[Challenge] = relationship(back_populates="tags")
    tag: Mapped[Tag] = relationship()


class Hint(Base):
    __tablename__ = "hints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id", ondelete="CASCADE"), index=True)
    order_index: Mapped[int] = mapped_column(Integer, default=1)
    content: Mapped[str] = mapped_column(Text)
    cost: Mapped[int] = mapped_column(Integer, default=0)

    challenge: Mapped[Challenge] = relationship(back_populates="hints")
    reveals: Mapped[list[HintReveal]] = relationship(back_populates="hint", cascade="all, delete-orphan")


class HintReveal(Base):
    __tablename__ = "hint_reveals"
    __table_args__ = (UniqueConstraint("hint_id", "user_id", name="uq_hint_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hint_id: Mapped[int] = mapped_column(ForeignKey("hints.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    revealed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    hint: Mapped[Hint] = relationship(back_populates="reveals")


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id", ondelete="CASCADE"), index=True)
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(255), unique=True)
    content_type: Mapped[str] = mapped_column(String(120))
    size_bytes: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    challenge: Mapped[Challenge] = relationship(back_populates="attachments")


class Submission(Base):
    __tablename__ = "submissions"
    __table_args__ = (
        Index("ix_submissions_user_challenge", "user_id", "challenge_id"),
        Index("ix_submissions_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id", ondelete="CASCADE"), index=True)
    competition_id: Mapped[int | None] = mapped_column(
        ForeignKey("competitions.id", ondelete="SET NULL"), nullable=True, index=True
    )
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    submitted_flag_hash: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates="submissions")
    challenge: Mapped[Challenge] = relationship()
    competition: Mapped[Competition | None] = relationship()


class Solve(Base):
    __tablename__ = "solves"
    __table_args__ = (UniqueConstraint("user_id", "challenge_id", name="uq_user_challenge_solve"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("challenges.id", ondelete="CASCADE"), index=True)
    competition_id: Mapped[int | None] = mapped_column(
        ForeignKey("competitions.id", ondelete="SET NULL"), nullable=True
    )
    points_awarded: Mapped[int] = mapped_column(Integer)
    solved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship()
    challenge: Mapped[Challenge] = relationship()


class ScoreEvent(Base):
    __tablename__ = "score_events"
    __table_args__ = (
        UniqueConstraint("user_id", "event_type", "reference_id", name="uq_score_event"),
        Index("ix_score_events_user", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    challenge_id: Mapped[int | None] = mapped_column(ForeignKey("challenges.id", ondelete="SET NULL"), nullable=True)
    competition_id: Mapped[int | None] = mapped_column(ForeignKey("competitions.id", ondelete="SET NULL"), nullable=True)
    event_type: Mapped[ScoreEventType] = mapped_column(Enum(ScoreEventType))
    reference_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    delta: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_created", "created_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    resource_type: Mapped[str] = mapped_column(String(40))
    resource_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    actor: Mapped[User | None] = relationship()
