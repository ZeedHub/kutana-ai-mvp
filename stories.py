import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..deps import get_current_user, require_admin
from ..models import Story, StoryVote, User
from ..schemas import StoryCreate, StoryOut

router = APIRouter(prefix="/stories", tags=["stories"])


async def _votes(db: AsyncSession, story_id) -> int:
    return await db.scalar(select(func.count()).select_from(StoryVote).where(StoryVote.story_id == story_id)) or 0


@router.get("", response_model=list[StoryOut])
async def list_stories(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    votes = func.count(StoryVote.user_id)
    rows = (await db.execute(
        select(Story, votes.label("votes"))
        .outerjoin(StoryVote, StoryVote.story_id == Story.id)
        .where(Story.is_approved.is_(True))
        .group_by(Story.id)
        .order_by(votes.desc(), Story.created_at.desc())
    )).all()
    mine = set((await db.execute(select(StoryVote.story_id).where(StoryVote.user_id == user.id))).scalars().all())
    top = rows[0][1] if rows else 0
    return [StoryOut(id=str(s.id), couple=s.couple, location=s.location, image=s.image_url, votes=v,
                     is_top=(v == top and v > 0), has_voted=s.id in mine) for s, v in rows]


@router.post("/{story_id}/vote")
async def vote(story_id: uuid.UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    story = await db.get(Story, story_id)
    if not story or not story.is_approved:
        raise HTTPException(404, "Story not found")
    db.add(StoryVote(user_id=user.id, story_id=story_id))
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, "You already voted for this story")
    return {"votes": await _votes(db, story_id), "has_voted": True}


@router.delete("/{story_id}/vote")
async def unvote(story_id: uuid.UUID, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    v = await db.get(StoryVote, (user.id, story_id))
    if v:
        await db.delete(v)
        await db.commit()
    return {"votes": await _votes(db, story_id), "has_voted": False}


@router.post("", status_code=201)
async def submit_story(body: StoryCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    s = Story(created_by=user.id, couple=body.couple, location=body.location, image_url=body.image_url)
    db.add(s)
    await db.commit()
    return {"id": str(s.id), "status": "pending_approval"}


@router.patch("/{story_id}/approve")
async def approve(story_id: uuid.UUID, _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    s = await db.get(Story, story_id)
    if not s:
        raise HTTPException(404, "Story not found")
    s.is_approved = True
    await db.commit()
    return {"id": str(s.id), "is_approved": True}
