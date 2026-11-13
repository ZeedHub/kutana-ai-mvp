from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from .utils import age_from, normalize_phone


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=80)
    dob: date
    gender: Literal["male", "female", "other"]
    interested_in: Literal["male", "female", "everyone"] = "everyone"
    city: str = "Nairobi"
    consent_ai_profiling: bool
    consent_sensitive_data: bool

    @model_validator(mode="after")
    def check(self):
        if age_from(self.dob) < 18:
            raise ValueError("You must be 18 or older")
        if not (self.consent_ai_profiling and self.consent_sensitive_data):
            raise ValueError("Explicit consent is required (Data Protection Act, 2019)")
        return self


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SubscriptionOut(BaseModel):
    tier: Literal["free", "black"]
    expires_at: datetime | None = None


class ProfileOut(BaseModel):
    id: str
    name: str
    age: int
    city: str
    country: str
    profession: str | None
    photo_url: str | None
    is_verified: bool
    privacy_status: Literal["Compliant", "Consent required"]
    subscription: SubscriptionOut
    profiling_complete: bool


class ProfileUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    city: str | None = Field(default=None, max_length=80)
    profession: str | None = Field(default=None, max_length=120)
    photo_url: str | None = Field(default=None, max_length=500)
    interested_in: Literal["male", "female", "everyone"] | None = None


# ---- profiler
class ChatMsg(BaseModel):
    role: Literal["ai", "user"]
    text: str


class ProfilerState(BaseModel):
    status: Literal["active", "complete"]
    messages: list[ChatMsg]
    used: int
    max: int


class ProfilerSend(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


class ProfilerReply(BaseModel):
    reply: str
    used: int
    max: int
    complete: bool


# ---- matches
class Metrics(BaseModel):
    financial: int
    nightlife: int
    goals: int


class MatchCard(BaseModel):
    id: str
    name: str | None = None
    age: int | None = None
    profession: str | None = None
    image: str | None = None
    overall_score: int | None = None
    metrics: Metrics | None = None
    is_verified: bool = False
    locked: bool = False


class MatchesOut(BaseModel):
    premium: bool
    swipes_remaining: int | None
    matches: list[MatchCard]


class SwipeIn(BaseModel):
    action: Literal["like", "pass"]


class SwipeOut(BaseModel):
    matched: bool
    swipes_remaining: int | None


# ---- stories
class StoryOut(BaseModel):
    id: str
    couple: str
    location: str
    image: str
    votes: int
    is_top: bool
    has_voted: bool


class StoryCreate(BaseModel):
    couple: str = Field(min_length=1, max_length=120)
    location: str = Field(min_length=1, max_length=160)
    image_url: str = Field(max_length=500)


# ---- payments
class StkIn(BaseModel):
    phone: str
    plan: Literal["black_monthly"] = "black_monthly"

    @field_validator("phone")
    @classmethod
    def _phone(cls, v):
        return normalize_phone(v)


class StkOut(BaseModel):
    checkout_request_id: str
    message: str


class PaymentStatus(BaseModel):
    status: Literal["pending", "success", "failed"]
    result_desc: str | None = None
