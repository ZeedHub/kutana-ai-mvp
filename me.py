from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..deps import get_current_user, get_subscription
from ..models import Match, Payment, ProfileVector, ProfilerSession, Story, StoryVote, Swipe, User
from ..schemas import ProfileOut, ProfileUpdate, SubscriptionOut
from ..utils import age_from

router = APIRouter(prefix="/me", tags=["me"])


async def _profile(db: AsyncSession, u: User) -> ProfileOut:
    sub = await get_subscription(db, u.id)
    has_vec = await db.scalar(select(ProfileVector.user_id).where(ProfileVector.user_id == u.id))
    consented = bool(u.consent_ai_profiling_at and u.consent_sensitive_data_at)
    return ProfileOut(
        id=str(u.id), name=u.name, age=age_from(u.dob), city=u.city, country=u.country,
        profession=u.profession, photo_url=u.photo_url, is_verified=u.is_verified,
        privacy_status="Compliant" if consented else "Consent required",
        subscription=SubscriptionOut(tier="black" if sub else "free", expires_at=sub.expires_at if sub else None),
        profiling_complete=bool(has_vec),
    )


@router.get("", response_model=ProfileOut)
async def get_me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await _profile(db, user)


@router.patch("", response_model=ProfileOut)
async def update_me(body: ProfileUpdate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    for k, v in body.model_dump(exclude_unset=True).items():
        if v is not None:
            setattr(user, k, v)
    await db.commit()
    return await _profile(db, user)


@router.delete("/profiling", status_code=204)
async def delete_profiling(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Withdraw AI-profiling data (vector + any in-flight chat)."""
    await db.execute(delete(ProfilerSession).where(ProfilerSession.user_id == user.id))
    await db.execute(delete(ProfileVector).where(ProfileVector.user_id == user.id))
    await db.commit()


@router.get("/export")
async def export_data(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Data portability (DPA 2019 s.38)."""
    swipes = (await db.execute(select(Swipe).where(Swipe.swiper_id == user.id))).scalars().all()
    matches = (await db.execute(select(Match).where((Match.user_a_id == user.id) | (Match.user_b_id == user.id)))).scalars().all()
    votes = (await db.execute(select(StoryVote).where(StoryVote.user_id == user.id))).scalars().all()
    pays = (await db.execute(select(Payment).where(Payment.user_id == user.id))).scalars().all()
    vec = await db.scalar(select(ProfileVector.embedding).where(ProfileVector.user_id == user.id))
    return {
        "account": {"id": str(user.id), "email": user.email, "name": user.name, "dob": str(user.dob),
                    "gender": user.gender, "interested_in": user.interested_in, "city": user.city,
                    "profession": user.profession, "created_at": user.created_at,
                    "consent_ai_profiling_at": user.consent_ai_profiling_at,
                    "consent_sensitive_data_at": user.consent_sensitive_data_at},
        "compatibility_vector": None if vec is None else [float(x) for x in vec],
        "swipes": [{"target": str(s.target_id), "action": s.action, "at": s.created_at} for s in swipes],
        "matches": [{"a": str(m.user_a_id), "b": str(m.user_b_id), "at": m.created_at} for m in matches],
        "story_votes": [str(v.story_id) for v in votes],
        "payments": [{"plan": p.plan, "amount_kes": p.amount_kes, "status": p.status,
                      "receipt": p.mpesa_receipt, "at": p.created_at} for p in pays],
    }


@router.delete("", status_code=204)
async def delete_account(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Right to erasure. FK cascades remove all personal rows; payments are anonymised (user_id -> NULL)."""
    await db.execute(delete(User).where(User.id == user.id))
    await db.commit()
