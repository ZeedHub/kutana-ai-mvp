import logging
from datetime import timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import PLANS, settings
from ..database import get_db
from ..deps import get_current_user
from ..models import Payment, Subscription, User
from ..schemas import PaymentStatus, StkIn, StkOut
from ..services import mpesa
from ..utils import utcnow

log = logging.getLogger(__name__)
router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/mpesa/stk", response_model=StkOut)
async def start_stk(body: StkIn, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    plan = PLANS[body.plan]
    try:
        res = await mpesa.stk_push(body.phone, plan["amount_kes"], f"KUT{str(user.id)[:6]}")
    except httpx.HTTPError:
        log.exception("Daraja STK push failed")
        raise HTTPException(502, "M-Pesa is unavailable, please try again")
    if str(res.get("ResponseCode")) != "0":
        raise HTTPException(400, res.get("ResponseDescription", "STK push rejected"))
    db.add(Payment(user_id=user.id, plan=body.plan, amount_kes=plan["amount_kes"], phone=body.phone,
                   checkout_request_id=res["CheckoutRequestID"], merchant_request_id=res.get("MerchantRequestID")))
    await db.commit()
    return StkOut(checkout_request_id=res["CheckoutRequestID"], message="Check your phone and enter your M-Pesa PIN")


@router.get("/status/{checkout_request_id}", response_model=PaymentStatus)
async def payment_status(checkout_request_id: str, user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    p = await db.scalar(select(Payment).where(Payment.checkout_request_id == checkout_request_id,
                                               Payment.user_id == user.id))
    if not p:
        raise HTTPException(404, "Payment not found")
    return PaymentStatus(status=p.status, result_desc=p.result_desc)


@router.post("/mpesa/callback/{secret}", include_in_schema=False)
async def mpesa_callback(secret: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Daraja calls this. Secret path token stands in for a signature (Daraja doesn't sign callbacks)."""
    ok = {"ResultCode": 0, "ResultDesc": "Accepted"}
    if secret != settings.mpesa_callback_secret:
        raise HTTPException(404)
    try:
        cb = (await request.json())["Body"]["stkCallback"]
        p = await db.scalar(select(Payment).where(Payment.checkout_request_id == cb["CheckoutRequestID"]).with_for_update())
    except Exception:
        log.exception("bad callback payload")
        return ok
    if not p or p.status != "pending":
        return ok  # unknown or already processed (idempotent)

    p.result_desc = str(cb.get("ResultDesc"))[:255]
    if cb.get("ResultCode") == 0:
        items = {i["Name"]: i.get("Value") for i in cb.get("CallbackMetadata", {}).get("Item", [])}
        if int(float(items.get("Amount", 0))) < p.amount_kes:
            p.status, p.result_desc = "failed", "Amount mismatch"
        elif p.user_id:
            p.status, p.mpesa_receipt = "success", str(items.get("MpesaReceiptNumber"))
            sub = await db.get(Subscription, p.user_id)
            base = sub.expires_at if sub and sub.expires_at > utcnow() else utcnow()
            expires = base + timedelta(days=PLANS[p.plan]["days"])
            if sub:
                sub.expires_at = expires
            else:
                db.add(Subscription(user_id=p.user_id, tier="black", expires_at=expires))
    else:
        p.status = "failed"
    await db.commit()
    return ok
