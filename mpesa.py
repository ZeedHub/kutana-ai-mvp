import base64
from datetime import datetime

import httpx

from ..config import settings


async def _token(client: httpx.AsyncClient) -> str:
    r = await client.get(
        f"{settings.mpesa_base_url}/oauth/v1/generate",
        params={"grant_type": "client_credentials"},
        auth=(settings.mpesa_consumer_key, settings.mpesa_consumer_secret),
    )
    r.raise_for_status()
    return r.json()["access_token"]


async def stk_push(phone: str, amount: int, reference: str) -> dict:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{settings.mpesa_shortcode}{settings.mpesa_passkey}{ts}".encode()).decode()
    payload = {
        "BusinessShortCode": settings.mpesa_shortcode,
        "Password": password,
        "Timestamp": ts,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": settings.mpesa_shortcode,
        "PhoneNumber": phone,
        "CallBackURL": f"{settings.public_base_url}/api/payments/mpesa/callback/{settings.mpesa_callback_secret}",
        "AccountReference": reference[:12],
        "TransactionDesc": "Kutana Black",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        token = await _token(client)
        r = await client.post(
            f"{settings.mpesa_base_url}/mpesa/stkpush/v1/processrequest",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )
        r.raise_for_status()
        return r.json()
