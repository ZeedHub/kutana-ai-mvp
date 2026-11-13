import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..database import get_db
from ..deps import get_current_user
from ..models import ProfileVector, ProfilerMessage, ProfilerSession, User
from ..schemas import ChatMsg, ProfilerReply, ProfilerSend, ProfilerState
from ..security import decrypt, encrypt
from ..services import llm
from ..utils import utcnow

log = logging.getLogger(__name__)
router = APIRouter(prefix="/profiler", tags=["profiler"])
MAX = settings.max_profiler_messages

GREETING = ("Hey there. I am the Kutana Profiler. I use our chats to build your private compatibility matrix. "
            f"To keep it focused, we only have {MAX} messages. Ready?")


async def _history(db: AsyncSession, session_id) -> list[dict]:
    rows = (await db.execute(
        select(ProfilerMessage).where(ProfilerMessage.session_id == session_id).order_by(ProfilerMessage.id)
    )).scalars().all()
    return [{"role": r.role, "text": decrypt(r.ciphertext)} for r in rows]


async def _new_session(db: AsyncSession, user: User) -> ProfilerSession:
    s = ProfilerSession(user_id=user.id)
    db.add(s)
    await db.flush()
    db.add(ProfilerMessage(session_id=s.id, role="ai", ciphertext=encrypt(GREETING)))
    await db.commit()
    return s


async def _state(db: AsyncSession, user: User, s: ProfilerSession | None) -> ProfilerState:
    if s is None:
        return ProfilerState(status="complete", messages=[], used=MAX, max=MAX)
    hist = await _history(db, s.id)
    return ProfilerState(status="active", messages=[ChatMsg(**m) for m in hist], used=s.user_message_count, max=MAX)


async def _finalize(db: AsyncSession, user: User, s: ProfilerSession) -> None:
    """Score transcript -> store vector -> hard-delete the chat (ODPC: vectorize then delete)."""
    hist = await _history(db, s.id)
    try:
        vec = await llm.extract_vector(hist)
    except Exception:
        log.exception("scoring failed")
        raise HTTPException(502, "Scoring failed. Call POST /profiler/finalize to retry.")
    stmt = pg_insert(ProfileVector).values(user_id=user.id, embedding=vec)
    stmt = stmt.on_conflict_do_update(index_elements=["user_id"], set_={"embedding": vec, "updated_at": utcnow()})
    await db.execute(stmt)
    await db.execute(delete(ProfilerSession).where(ProfilerSession.id == s.id))  # messages cascade
    await db.commit()


async def _get_session(db: AsyncSession, user: User, lock: bool = False) -> ProfilerSession | None:
    q = select(ProfilerSession).where(ProfilerSession.user_id == user.id)
    if lock:
        q = q.with_for_update()
    return (await db.execute(q)).scalar_one_or_none()


def _require_consent(user: User):
    if not (user.consent_ai_profiling_at and user.consent_sensitive_data_at):
        raise HTTPException(403, "AI profiling consent required")


@router.post("/session", response_model=ProfilerState)
async def start_or_resume(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    _require_consent(user)
    s = await _get_session(db, user)
    if s is None:
        has_vec = await db.scalar(select(ProfileVector.user_id).where(ProfileVector.user_id == user.id))
        if has_vec:
            return await _state(db, user, None)
        s = await _new_session(db, user)
    return await _state(db, user, s)


@router.post("/restart", response_model=ProfilerState)
async def restart(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """'Retake AI Profiling'. Old vector is kept until the new run completes."""
    _require_consent(user)
    await db.execute(delete(ProfilerSession).where(ProfilerSession.user_id == user.id))
    s = await _new_session(db, user)
    return await _state(db, user, s)


@router.post("/message", response_model=ProfilerReply)
async def send_message(body: ProfilerSend, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    s = await _get_session(db, user, lock=True)
    if s is None:
        raise HTTPException(404, "No active session. Call POST /profiler/session")
    if s.user_message_count >= MAX:
        raise HTTPException(409, "Message limit reached")

    hist = await _history(db, s.id)
    hist.append({"role": "user", "text": body.text.strip()})
    db.add(ProfilerMessage(session_id=s.id, role="user", ciphertext=encrypt(body.text.strip())))
    s.user_message_count += 1
    await db.flush()

    if s.user_message_count >= MAX:
        await db.commit()  # persist the last answer so finalize can be retried on failure
        await _finalize(db, user, s)
        return ProfilerReply(reply="Thanks, that's everything I need. Analysing your profile now.",
                             used=MAX, max=MAX, complete=True)

    try:
        reply = await llm.next_question(hist, MAX - s.user_message_count)
    except Exception:
        log.exception("chat LLM failed")
        raise HTTPException(502, "AI is unavailable, please retry")  # uncommitted -> user msg rolled back
    db.add(ProfilerMessage(session_id=s.id, role="ai", ciphertext=encrypt(reply)))
    await db.commit()
    return ProfilerReply(reply=reply, used=s.user_message_count, max=MAX, complete=False)


@router.post("/finalize", response_model=ProfilerReply)
async def retry_finalize(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    s = await _get_session(db, user, lock=True)
    if s is None or s.user_message_count < MAX:
        raise HTTPException(409, "Nothing to finalize")
    await _finalize(db, user, s)
    return ProfilerReply(reply="Profile built.", used=MAX, max=MAX, complete=True)
