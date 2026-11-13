import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..deps import get_current_user, is_premium, require_premium
from ..models import Match, ProfileVector, Swipe, User
from ..schemas import MatchCard, MatchesOut, Metrics, SwipeIn, SwipeOut
from ..services.matching import candidates, category_scores
from ..utils import age_from, nairobi_day_start_utc

router = APIRouter(prefix="/matches", tags=["matches"])


async def _swipes_remaining(db: AsyncSession, user: User, premium: bool) -> int | None:
    if premium:
        return None
    used = await db.scalar(
        select(func.count()).select_from(Swipe)
        .where(Swipe.swiper_id == user.id, Swipe.created_at >= nairobi_day_start_utc())
    )
    return max(0, settings.free_daily_swipes - (used or 0))


def _card(u: User, s: dict, show_metrics: bool) -> MatchCard:
    return MatchCard(
        id=str(u.id), name=u.name, age=age_from(u.dob), profession=u.profession, image=u.photo_url,
        overall_score=s["overall"], is_verified=u.is_verified,
        metrics=Metrics(financial=s["financial"], nightlife=s["nightlife"], goals=s["goals"]) if show_metrics else None,
    )


@router.get("", response_model=MatchesOut)
async def leaderboard(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    my_vec = await db.scalar(select(ProfileVector.embedding).where(ProfileVector.user_id == user.id))
    if my_vec is None:
        raise HTTPException(409, "profiling_incomplete")
    premium = await is_premium(db, user.id)
    mine = [float(x) for x in my_vec]
    scored = []
    for cand, emb in await candidates(db, user, my_vec):
        scored.append((category_scores(mine, [float(x) for x in emb]), cand))
    scored.sort(key=lambda t: t[0]["overall"], reverse=True)

    cards: list[MatchCard] = []
    for rank, (s, cand) in enumerate(scored):
        if premium:
            cards.append(_card(cand, s, show_metrics=True))
        elif rank < settings.free_visible_matches:
            cards.append(_card(cand, s, show_metrics=False))   # free: overall score only
        else:
            # Locked: never leak identity, photo, id or scores
            cards.append(MatchCard(id=f"locked-{rank}", locked=True))
    return MatchesOut(premium=premium, swipes_remaining=await _swipes_remaining(db, user, premium), matches=cards)


@router.post("/{target_id}/swipe", response_model=SwipeOut)
async def swipe(target_id: uuid.UUID, body: SwipeIn, user: User = Depends(get_current_user),
                db: AsyncSession = Depends(get_db)):
    if target_id == user.id:
        raise HTTPException(400, "Cannot swipe on yourself")
    target = await db.get(User, target_id)
    if not target or not target.is_active:
        raise HTTPException(404, "User not found")
    premium = await is_premium(db, user.id)
    remaining = await _swipes_remaining(db, user, premium)
    if remaining is not None and remaining <= 0:
        raise HTTPException(429, "Daily swipe limit reached. Upgrade to Kutana Black for unlimited.")
    if await db.scalar(select(Swipe.id).where(Swipe.swiper_id == user.id, Swipe.target_id == target_id)):
        raise HTTPException(409, "Already swiped")

    db.add(Swipe(swiper_id=user.id, target_id=target_id, action=body.action))
    matched = False
    if body.action == "like":
        reciprocal = await db.scalar(select(Swipe.id).where(
            Swipe.swiper_id == target_id, Swipe.target_id == user.id, Swipe.action == "like"))
        if reciprocal:
            a, b = sorted([user.id, target_id], key=str)
            exists = await db.scalar(select(Match.id).where(Match.user_a_id == a, Match.user_b_id == b))
            if not exists:
                db.add(Match(user_a_id=a, user_b_id=b))
            matched = True
    await db.commit()
    return SwipeOut(matched=matched, swipes_remaining=None if remaining is None else remaining - 1)


@router.get("/mutual", response_model=list[MatchCard])
async def mutual(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Match).where((Match.user_a_id == user.id) | (Match.user_b_id == user.id))
                             .order_by(Match.created_at.desc()))).scalars().all()
    out = []
    for m in rows:
        other = await db.get(User, m.user_b_id if m.user_a_id == user.id else m.user_a_id)
        if other and other.is_active:
            out.append(MatchCard(id=str(other.id), name=other.name, age=age_from(other.dob),
                                 profession=other.profession, image=other.photo_url, is_verified=other.is_verified))
    return out


@router.get("/likes-me", response_model=list[MatchCard])
async def likes_me(user: User = Depends(require_premium), db: AsyncSession = Depends(get_db)):
    """Premium: see who liked you before you swipe."""
    mine = select(Swipe.target_id).where(Swipe.swiper_id == user.id)
    users = (await db.execute(
        select(User).join(Swipe, and_(Swipe.swiper_id == User.id, Swipe.target_id == user.id, Swipe.action == "like"))
        .where(User.is_active.is_(True), User.id.not_in(mine))
    )).scalars().all()
    return [MatchCard(id=str(u.id), name=u.name, age=age_from(u.dob), profession=u.profession,
                      image=u.photo_url, is_verified=u.is_verified) for u in users]
