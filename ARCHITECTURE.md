# Architecture

System overview for NestWorth. See `CLAUDE.md` for repo status, known issues, and the deployment history. See `DEPLOYMENT.md` for how the deployed stack is provisioned.

## Topology

```
Browser
  │
  ▼
Vercel (frontend/, React + Vite, static build)
  │  fetch() calls to API_BASE_URL (frontend/src/lib/api.ts)
  ▼
Railway (backend/, FastAPI + Uvicorn)
  │  Motor (async pymongo)
  ▼
MongoDB Atlas (users, profiles, projections collections)
  │
  ▼
OpenAI API (AI summary generation, backend/integrations/openai_client.py)
```

Frontend and backend are deployed independently and communicate only over HTTP(S); there is no server-side rendering or shared process.

## Backend structure

- `backend/main.py` — FastAPI app, router registration, `/healthz`
- `backend/routers/` — one file per resource, all mounted under `/api/v1`:
  - `auth.py` — `/api/v1/auth/signup`, `/login`, `/logout`, `/me`, `/forgot-password`, `/reset-password`
  - `profiles.py` — `/api/v1/profiles` (create/update), `/api/v1/profiles/me`
  - `projections.py` — `/api/v1/projections/calculate`
  - `summaries.py` — `/api/v1/summaries/generate`, `/generate-assumptions`
  - `exports.py` — `/api/v1/exports/pdf`
- `backend/models/` — Pydantic models (`user.py`, `profile.py`, `projection.py`)
- `backend/database.py` — Motor client / MongoDB connection
- `backend/integrations/openai_client.py` — OpenAI client construction (see `CLAUDE.md` Known Issues re: import-time construction requiring a non-empty `OPENAI_API_KEY`)
- `backend/config.py` — Pydantic settings, reads env vars
- `backend/scripts/` — one-off admin scripts (currently `delete_all_users.py`, requires `--yes`)
- `backend/tests/manual/` — ad hoc integration scripts that hit a live server; not a pytest suite (no fixtures/config)

## Auth flow

1. `POST /api/v1/auth/signup` or `/login` — backend hashes/verifies password with argon2, issues a JWT
2. Frontend stores the JWT (see `AuthContext.tsx`) and sends it as `Authorization: Bearer <token>` on subsequent requests
3. Protected routes use a FastAPI dependency to decode the JWT and load the current user
4. Password reset is token-based: `forgot-password` issues a token (returned in the API response only when `APP_ENV=development`), `reset-password` consumes `?token=...` from the URL — see `CLAUDE.md` Known Issues for the history of the insecure `-direct` endpoint that this replaced

## Request flow: profile → projection → summary → PDF

1. **Onboarding** — frontend collects the 10-question financial profile, `POST /api/v1/profiles` persists it (`profiles` collection), keyed to the authenticated user
2. **Projection** — `POST /api/v1/projections/calculate` reads the stored profile, looks up regional childcare costs and one-time/recurring cost tables, and runs a deterministic 5-year monthly/yearly projection with warnings (negative cashflow, low savings buffer, high childcare cost ratio)
3. **AI summary** — `POST /api/v1/summaries/generate` sends the calculated projection (not raw user input) to the OpenAI API to produce an empathetic narrative; the model is constrained to the numbers already computed, not free to invent figures
4. **PDF export** — `POST /api/v1/exports/pdf` renders the projection + summary to a PDF via reportlab and returns it for download

## Frontend reference data

`frontend/src/data/*.ts` (`childcareCostsByZip.ts`, `oneTimeCosts.ts`, `recurringCosts.ts`) are TypeScript tables compiled from the root-level source spreadsheets (`Example.xlsx`, `One Time costs.xlsx`, `Recurring costs.xlsx`, `Ref Data Childcare cost byZip.xlsx`). These are the same tables the backend's projection engine consults — the spreadsheets are the data's provenance/source-of-record, not something read at runtime. To update reference data, edit the spreadsheets and regenerate (or hand-edit) the corresponding `.ts` file; there is no automated spreadsheet→TS pipeline currently.

## Known architectural gaps

See `CLAUDE.md` Known Issues for the full list (no rate limiting, `OPENAI_API_KEY` required at boot, no CI, etc.) — not duplicated here to avoid drift between the two documents.
