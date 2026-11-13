from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ProfileVector, Swipe, User
from ..traits import CATEGORIES, WEIGHTS


def category_scores(a: list[float], b: list[float]) -> dict[str, int]:
    out: dict[str, float] = {}
    for name, (lo, hi) in CATEGORIES.items():
        diffs = [abs(x - y) for x, y in zip(a[lo:hi], b[lo:hi])]
        out[name] = 100 - sum(diffs) / len(diffs)
    out["overall"] = sum(out[k] * WEIGHTS[k] for k in CATEGORIES)
    return {k: round(v) for k, v in out.items()}


async def candidates(db: AsyncSession, me: User, my_vec, limit: int = 60):
    """pgvector pre-filter (nearest by L2), then caller re-ranks with category scores."""
    already = select(Swipe.target_id).where(Swipe.swiper_id == me.id)
    dist = ProfileVector.embedding.l2_distance(my_vec)
    q = (
        select(User, ProfileVector.embedding)
        .join(ProfileVector, ProfileVector.user_id == User.id)
        .where(User.id != me.id, User.is_active.is_(True), User.id.not_in(already))
        .order_by(dist)
        .limit(limit)
    )
    if me.interested_in != "everyone":
        q = q.where(User.gender == me.interested_in)
    q = q.where(User.interested_in.in_([me.gender, "everyone"]))
    return (await db.execute(q)).all()
