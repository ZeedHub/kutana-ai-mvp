import uuid
from datetime import date, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (Boolean, Date, DateTime, ForeignKey, Index, Integer, String,
                        Text, UniqueConstraint, func)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base
from .traits import DIM


def _pk():
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def _fk(target: str, ondelete: str = "CASCADE", nullable: bool = False, **kw):
    return mapped_column(UUID(as_uuid=True), ForeignKey(target, ondelete=ondelete), nullable=nullable, **kw)


def _now():
    return mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = _pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(80))
    dob: Mapped[date] = mapped_column(Date)
    gender: Mapped[str] = mapped_column(String(10))
    interested_in: Mapped[str] = mapped_column(String(10), default="everyone")
    city: Mapped[str] = mapped_column(String(80), default="Nairobi")
    country: Mapped[str] = mapped_column(String(80), default="Kenya")
    profession: Mapped[str | None] = mapped_column(String(120), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)   # set by biometric/liveness flow
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    # Kenya DPA 2019: explicit, timestamped consent for sensitive data + AI profiling
    consent_ai_profiling_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consent_sensitive_data_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = _now()


class ProfileVector(Base):
    """Only the numeric trait vector is kept. Raw chat text is never persisted after scoring."""
    __tablename__ = "profile_vectors"
    user_id: Mapped[uuid.UUID] = _fk("users.id", primary_key=True)
    embedding = mapped_column(Vector(DIM))
    updated_at: Mapped[datetime] = _now()


class ProfilerSession(Base):
    __tablename__ = "profiler_sessions"
    id: Mapped[uuid.UUID] = _pk()
    user_id: Mapped[uuid.UUID] = _fk("users.id", unique=True)
    user_message_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = _now()


class ProfilerMessage(Base):
    __tablename__ = "profiler_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[uuid.UUID] = _fk("profiler_sessions.id", index=True)
    role: Mapped[str] = mapped_column(String(10))          # 'ai' | 'user'
    ciphertext: Mapped[str] = mapped_column(Text)          # Fernet-encrypted at rest
    created_at: Mapped[datetime] = _now()


class Swipe(Base):
    __tablename__ = "swipes"
    __table_args__ = (UniqueConstraint("swiper_id", "target_id"), Index("ix_swipe_day", "swiper_id", "created_at"))
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    swiper_id: Mapped[uuid.UUID] = _fk("users.id")
    target_id: Mapped[uuid.UUID] = _fk("users.id", index=True)
    action: Mapped[str] = mapped_column(String(10))        # 'like' | 'pass'
    created_at: Mapped[datetime] = _now()


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (UniqueConstraint("user_a_id", "user_b_id"),)
    id: Mapped[uuid.UUID] = _pk()
    user_a_id: Mapped[uuid.UUID] = _fk("users.id")
    user_b_id: Mapped[uuid.UUID] = _fk("users.id")
    created_at: Mapped[datetime] = _now()


class Subscription(Base):
    __tablename__ = "subscriptions"
    user_id: Mapped[uuid.UUID] = _fk("users.id", primary_key=True)
    tier: Mapped[str] = mapped_column(String(20), default="black")
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[uuid.UUID] = _pk()
    user_id: Mapped[uuid.UUID | None] = _fk("users.id", ondelete="SET NULL", nullable=True)  # keep for tax records
    plan: Mapped[str] = mapped_column(String(40))
    amount_kes: Mapped[int] = mapped_column(Integer)
    phone: Mapped[str] = mapped_column(String(15))
    checkout_request_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    merchant_request_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    status: Mapped[str] = mapped_column(String(12), default="pending")   # pending|success|failed
    mpesa_receipt: Mapped[str | None] = mapped_column(String(40), nullable=True)
    result_desc: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = _now()


class Story(Base):
    __tablename__ = "stories"
    id: Mapped[uuid.UUID] = _pk()
    created_by: Mapped[uuid.UUID | None] = _fk("users.id", ondelete="SET NULL", nullable=True)
    couple: Mapped[str] = mapped_column(String(120))
    location: Mapped[str] = mapped_column(String(160))
    image_url: Mapped[str] = mapped_column(String(500))
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = _now()


class StoryVote(Base):
    __tablename__ = "story_votes"
    user_id: Mapped[uuid.UUID] = _fk("users.id", primary_key=True)
    story_id: Mapped[uuid.UUID] = _fk("stories.id", primary_key=True)
    created_at: Mapped[datetime] = _now()
