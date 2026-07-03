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
- **`POST /api/v1/auth/reset-password-direct`** (`backend/routers/auth.py:253-281`) resets any user's password given only their email — no token/verification. Full account-takeover vector. A proper token-based flow already exists at `/reset-password` (`auth.py:215-250`); the `-direct` endpoint appears to be a leftover dev shortcut and should be removed or gated to `APP_ENV=development` before any shared/deployed use.
- `forgot_password` (`auth.py:162-212`) returns the raw reset token in the API response when `APP_ENV=development`. Fine for local dev; make sure `APP_ENV` is never `development` outside your machine.
- No rate limiting on login/signup/reset endpoints.

### Config / deployment drift
- Most frontend API calls hardcode `http://localhost:8000` (`frontend/src/contexts/AuthContext.tsx:16`, `frontend/src/pages/Results.tsx:40,59,85,128`). Only `ForgotPassword.tsx` and `ResetPassword.tsx` read `VITE_API_BASE_URL`. Deploying as-is will leave most of the app calling localhost. Needs unifying onto one env-driven base URL before deploy.
- No `frontend/.env.example` documenting `VITE_API_BASE_URL`.
- `backend/requirements.txt` has **no pinned versions** — fresh installs can silently pull breaking major versions (FastAPI/pydantic/motor).
- No Dockerfile / docker-compose / CI config. Frontend and backend are run as two separate manual processes.
- `frontend/vercel.json` exists (SPA rewrite rule) suggesting Vercel was the intended frontend host, but there's no equivalent backend deploy config.

### Documentation drift
- `frontend/README.md` claims auth and data persistence are "frontend-only using localStorage" — **this is stale**. The app has a real FastAPI + MongoDB backend with JWT auth. Don't trust that section.
- Root-level `test_*.py` files (11 of them) are manual integration scripts that hit a live server at `localhost:8000`, not a real pytest suite. No pytest config exists.

### Other
- `delete_all_users.py` at repo root is a destructive script with no guardrails — know it's there before running arbitrary root-level scripts.

## Before deploying anywhere beyond local dev

1. Remove or lock down `reset-password-direct`.
2. Unify frontend API base URL handling to always use `VITE_API_BASE_URL` (no hardcoded localhost).
3. Pin `backend/requirements.txt` versions.
4. Confirm `APP_ENV` is not `development` in the deployed environment.
