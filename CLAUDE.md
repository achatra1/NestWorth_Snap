# CLAUDE.md

Guidance for Claude Code (and future contributors) working in this repo.

## Repo status

This is an **unmaintained prototype repo** (last commit 2026-01-02, originally built fast via AI-assisted tooling — see `frontend/AI_RULES.md`). It works, but has known rough edges below. Don't assume the READMEs are accurate — verify against actual code before relying on documented behavior.

## Stack

- **Frontend**: `frontend/` — React 18 + TypeScript + Vite (port 5137), Tailwind + shadcn/ui, pnpm (has `pnpm-lock.yaml`, not `package-lock.json`).
- **Backend**: `backend/` — FastAPI + Motor (async MongoDB) + JWT auth (argon2 password hashing), OpenAI for AI summaries, reportlab for PDF export.
- **Database**: MongoDB **Atlas** (cloud) — no local Mongo fallback configured. `backend/.env.example` documents required vars.

## Known issues

### Security — fix before exposing beyond localhost
- ~~`POST /api/v1/auth/reset-password-direct`~~ — **FIXED**. This endpoint reset any user's password given only their email (no token/verification) and was actually wired up as the app's primary reset flow (`Login.tsx` linked straight to `/reset-password` with no token, and `ResetPassword.tsx` ignored any token and called `-direct`). Removed the endpoint and model (`backend/routers/auth.py`, `backend/models/user.py`), and rewired the frontend to the proper token-based flow: `Login.tsx` → `/forgot-password` (request email) → backend issues a token → `/reset-password?token=...` → `ResetPassword.tsx` reads the token from the URL and calls the token-based `POST /api/v1/auth/reset-password`. If no token is present, the page now shows an error and a link back to `/forgot-password` instead of silently falling back to an insecure path.
- `forgot_password` (`auth.py`) returns the raw reset token in the API response when `APP_ENV=development`. Fine for local dev; make sure `APP_ENV` is never `development` outside your machine.
- No rate limiting on login/signup/reset endpoints.

### Config / deployment drift
- ~~Most frontend API calls hardcode `http://localhost:8000`~~ — **FIXED**. Added `frontend/src/lib/api.ts` exporting `API_BASE_URL` (from `VITE_API_BASE_URL`, falling back to `http://localhost:8000`) and `API_V1_URL` (`${API_BASE_URL}/api/v1`). All fetch call sites (`AuthContext.tsx`, `ForgotPassword.tsx`, `ResetPassword.tsx`, `Results.tsx`) now import from this single module instead of defining their own base URL or hardcoding one. Added `frontend/.env.example` documenting `VITE_API_BASE_URL`.
- ~~`backend/requirements.txt` has no pinned versions~~ — **FIXED**. Pinned to versions resolved and smoke-tested in a clean venv (Python 3.13): `fastapi==0.139.0`, `uvicorn[standard]==0.49.0`, `motor==3.7.1`, `pydantic[email]==2.13.4`, `pydantic-settings==2.14.2`, `python-dotenv==1.2.2`, `argon2-cffi==25.1.0`, `pyjwt==2.13.0`, `python-multipart==0.0.32`, `openai==2.44.0`, `pandas==3.0.3`, `openpyxl==3.1.5`, `reportlab==5.0.0`.
- No Dockerfile / docker-compose / CI config. Frontend and backend are run as two separate manual processes.
- `frontend/vercel.json` exists (SPA rewrite rule) suggesting Vercel was the intended frontend host, but there's no equivalent backend deploy config.

### Documentation drift
- `frontend/README.md` claims auth and data persistence are "frontend-only using localStorage" — **this is stale**. The app has a real FastAPI + MongoDB backend with JWT auth. Don't trust that section.
- Root-level `test_*.py` files (11 of them) are manual integration scripts that hit a live server at `localhost:8000`, not a real pytest suite. No pytest config exists.

### Other
- `delete_all_users.py` at repo root is a destructive script with no guardrails — know it's there before running arbitrary root-level scripts.
- **App fails to start if `OPENAI_API_KEY` is empty/unset.** `backend/integrations/openai_client.py` constructs `AsyncOpenAI(api_key=settings.OPENAI_API_KEY)` at **module import time**. With `openai==2.44.0` (pinned above), the client constructor raises `OpenAIError: Missing credentials` immediately if the key is empty — which crashes the whole FastAPI app on startup, not just AI-summary requests. `backend/config.py` defaults `OPENAI_API_KEY` to `""`, implying it was meant to be optional, but in practice it's a hard requirement even to boot the server. Found while smoke-testing the pinned dependency versions: import succeeded with a dummy key (`sk-test-dummy`) and failed with an empty one. Not fixed yet — options are (a) make `OPENAI_API_KEY` a required setting and fail fast with a clear error, or (b) lazily construct the OpenAI client inside the request path so the rest of the app still boots without it.

## Before deploying anywhere beyond local dev

1. ~~Remove or lock down `reset-password-direct`~~ — done, see above.
2. ~~Unify frontend API base URL handling to always use `VITE_API_BASE_URL`~~ — done, see above.
3. ~~Pin `backend/requirements.txt` versions~~ — done, see above.
4. Confirm `APP_ENV` is not `development` in the deployed environment.
