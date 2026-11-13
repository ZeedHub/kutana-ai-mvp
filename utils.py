import re
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

NAIROBI = ZoneInfo("Africa/Nairobi")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def age_from(dob: date) -> int:
    t = date.today()
    return t.year - dob.year - ((t.month, t.day) < (dob.month, dob.day))


def nairobi_day_start_utc() -> datetime:
    now = datetime.now(NAIROBI)
    return now.replace(hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)


def normalize_phone(raw: str) -> str:
    """Return Kenyan MSISDN as 2547XXXXXXXX / 2541XXXXXXXX or raise ValueError."""
    p = re.sub(r"[\s\-()]", "", raw)
    if p.startswith("+"):
        p = p[1:]
    if p.startswith("0"):
        p = "254" + p[1:]
    if not re.fullmatch(r"254[17]\d{8}", p):
        raise ValueError("Invalid Kenyan phone number")
    return p
