# Kutana AI – Backend (FastAPI + PostgreSQL/pgvector)

## Run
```bash
cp .env.example .env            # fill JWT_SECRET, FERNET_KEY, ANTHROPIC_API_KEY (+ M-Pesa keys)
docker compose up -d db
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload   # docs at http://localhost:8000/docs
```
Or `docker compose up --build` for everything. M-Pesa callbacks need a public HTTPS URL (e.g. ngrok) in `PUBLIC_BASE_URL`.

## Front-end tab -> endpoints (all under `/api`, Bearer JWT except auth)
| UI | Endpoint |
|---|---|
| Sign up / in | `POST /auth/register`, `POST /auth/login` |
| **AI tab** (10-message chat) | `POST /profiler/session` (start/resume), `POST /profiler/message {text}`, `POST /profiler/finalize` (retry), `POST /profiler/restart` |
| **Matches tab** | `GET /matches`, `POST /matches/{id}/swipe {action}`, `GET /matches/mutual`, `GET /matches/likes-me` (premium) |
| **Stories tab** | `GET /stories`, `POST /stories/{id}/vote`, `DELETE /stories/{id}/vote`, `POST /stories`, `PATCH /stories/{id}/approve` (admin) |
| **Profile tab** | `GET/PATCH /me`, `DELETE /me/profiling`, `GET /me/export`, `DELETE /me` |
| "Upgrade Now" | `POST /payments/mpesa/stk {phone}`, poll `GET /payments/status/{checkout_request_id}` |

## Key behaviours
- **Privacy/ODPC:** chat text is Fernet-encrypted at rest, only a 12-number trait vector is kept, and the transcript is hard-deleted on completion. Abandoned sessions are purged after 24h. Consent is timestamped at signup. Export and erasure endpoints are included.
- **Matching:** Claude scores 12 traits (finance/nightlife/goals); pgvector pre-filters nearest candidates, then category and overall % are computed (`services/matching.py`).
- **Freemium:** free users get 15 swipes per Nairobi day, the top 2 matches with overall score only, and the rest as `locked` cards with no identity, photo or real id. Black gets everything.
- **Payments:** KES 390 / 30 days (`PLANS` in `config.py`), idempotent callback, renewals extend from the current expiry.
