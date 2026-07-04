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
- Root-level `test_*.py` files (16 of them) are manual integration scripts that hit a live server at `localhost:8000`, not a real pytest suite. No pytest config exists. See [Documentation & file inventory](#documentation--file-inventory).

### Other
- `delete_all_users.py` at repo root is a destructive script with no guardrails — know it's there before running arbitrary root-level scripts.
- **App fails to start if `OPENAI_API_KEY` is empty/unset.** `backend/integrations/openai_client.py` constructs `AsyncOpenAI(api_key=settings.OPENAI_API_KEY)` at **module import time**. With `openai==2.44.0` (pinned above), the client constructor raises `OpenAIError: Missing credentials` immediately if the key is empty — which crashes the whole FastAPI app on startup, not just AI-summary requests. `backend/config.py` defaults `OPENAI_API_KEY` to `""`, implying it was meant to be optional, but in practice it's a hard requirement even to boot the server. Found while smoke-testing the pinned dependency versions: import succeeded with a dummy key (`sk-test-dummy`) and failed with an empty one. Not fixed yet — options are (a) make `OPENAI_API_KEY` a required setting and fail fast with a clear error, or (b) lazily construct the OpenAI client inside the request path so the rest of the app still boots without it.

## Deployment plan

**Decision (2026-07-03): Vercel (frontend) + Railway (backend) + MongoDB Atlas (DB), all on free/hobby tiers.**

1. ~~Remove or lock down `reset-password-direct`~~ — done, see above.
2. ~~Unify frontend API base URL handling to always use `VITE_API_BASE_URL`~~ — done, see above.
3. ~~Pin `backend/requirements.txt` versions~~ — done, see above.
4. ~~Add Railway build/start config~~ — **done 2026-07-04**. Added `railway.json` at repo root. This was necessary, not optional: `backend/main.py` and every router use absolute imports (`from backend.config import settings`), which only resolve if the process's working directory is the **repo root** with `backend/` as a package — but `requirements.txt` lives inside `backend/`. Railway's Nixpacks auto-detection would have gotten this wrong (it looks for `requirements.txt` at whatever it treats as the project root). `railway.json` pins: `buildCommand: pip install -r backend/requirements.txt`, `startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT`, `healthcheckPath: /healthz` (already exists in `main.py` and reports DB connectivity without crashing the app if Mongo is briefly unreachable). **Important: when creating the Railway service, leave its Root Directory as the repo root — do not point it at `backend/`,** or these paths break.
5. Not yet done — MongoDB Atlas: create a free (M0) cluster, a database user, and under Network Access allow `0.0.0.0/0` (Railway doesn't publish static outbound IPs on the free/hobby plan, so a fixed allowlist isn't practical there). Copy the resulting `mongodb+srv://...` connection string.
6. Not yet done — Railway backend deploy: create a project from this GitHub repo, root directory = repo root (see step 4), and set env vars: `MONGODB_URI` (from step 5), `JWT_SECRET` (generate one, e.g. `python -c "import secrets; print(secrets.token_urlsafe(48))"` — do not reuse the placeholder in `.env.example`), `CORS_ORIGINS` (Vercel frontend URL, set after step 7 once it's known — Railway lets you edit env vars post-deploy and redeploy), `OPENAI_API_KEY` (a real key — required just to boot, see the startup-crash bug below), `APP_ENV=production`. Railway injects `PORT` automatically; `railway.json`'s start command already reads it.
7. Not yet done — Vercel frontend deploy: import `frontend/` as the project root (not the repo root — `frontend/vercel.json` and `package.json` live there), set `VITE_API_BASE_URL` to the Railway backend's public URL (known after step 6).
8. Not yet done — go back and set `CORS_ORIGINS` on Railway to the real Vercel URL from step 7, then redeploy the backend (chicken-and-egg: the two URLs each depend on the other's service existing first).
9. Not yet done — smoke-test signup/login/projection/PDF export end-to-end against the deployed stack once all three are live.

## Documentation & file inventory

Living audit of every doc/script/data file in the repo — not code. Goal: `CLAUDE.md` is the source of truth; everything else either has a clear ongoing purpose (keep), overlaps with something else (consolidate), or is dead weight from the original AI-assisted build (remove). Update this table as files are added, merged, or deleted — don't let it drift the way the READMEs did.

| File | Purpose | Verdict |
|---|---|---|
| `CLAUDE.md` | Source of truth for repo status, known issues, deployment plan, this inventory. | **Keep** — authoritative. |
| `frontend/README.md` | Frontend setup/usage doc. | **Keep, but fix** — "frontend-only localStorage" section is stale (see Documentation drift above); needs a rewrite to reflect the real backend. |
| `Backend-dev-plan.md` (723 lines) | Original pre-build plan for the FastAPI backend (executive summary, why, scope). Historical design rationale, written before the backend existed. | **Consolidate then remove** — anything still true belongs in `CLAUDE.md`'s Stack section; the plan-vs-actual gap isn't worth maintaining as a second document. Not yet actioned. |
| `BROWSER_REFRESH_INSTRUCTIONS.md` (24 lines) | One-off note: "the profile save fix has been applied, hard-refresh your browser." Describes a bug that's already fixed. | **Remove** — no ongoing value, purely a stale support note. Not yet actioned. |
| `PROFILE_PREPOPULATION_IMPLEMENTATION.md` (115 lines) | Changelog-style writeup of one feature's implementation (files touched, what changed). | **Remove** — this is what commit messages and `git log`/`git blame` are for; it will only get staler as the code around it changes. Not yet actioned. |
| `PRD.md` (root) | **Canonical PRD** — problem statement, goals, personas, MVP scope, market analysis, product spec. Converted from `NestWorth PRD v1.docx` on 2026-07-03 (python-docx script; two embedded images — UI Mock, Appendix diagrams — were not carried over, noted inline in the file). | **Keep — this is now the source of truth PRD.** Decided 2026-07-03: docx is canonical, this is its maintained markdown copy. |
| `NestWorth PRD v1.docx` (1.8 MB binary) | Original stakeholder-authored PRD ("Downloadable PRD Reference" commit) — the canonical source `PRD.md` was converted from. | **Keep as source-of-record for the two embedded images**; `PRD.md` is what should actually be read/edited going forward since binaries don't diff. If this file is edited again, `PRD.md` needs re-conversion. |
| ~~`PRD` (root, no extension, plaintext)~~ | Old duplicate PRD export. | **REMOVED** 2026-07-03 — superseded by `PRD.md`. |
| ~~`frontend/PRD.md`~~ | "Deep Mode PRD Generation" output from the AI app-builder tool (dyad) that originally scaffolded this app. | **REMOVED** 2026-07-03 — superseded by root `PRD.md`. |
| `frontend/PRD-Template.md` (229 lines) | Blank template with `[placeholder]` text, generated by the same tool. Not filled in. | **Remove** — dead template, not a real doc. |
| `frontend/.prd-metadata.json` | Metadata pointing at `PRD.md`/`PRD-Template.md`, used by the dyad tool. | **Keep only if still using dyad**; otherwise remove alongside the PRD template. |
| `frontend/AI_RULES.md` (19 lines) | Tech-stack constraints for the dyad AI app-builder (React Router in `App.tsx`, shadcn/ui, Tailwind, etc.). | **Keep only if still using dyad** to make edits; the durable parts (tech stack) are now also captured in `CLAUDE.md`. Otherwise remove. |
| Root `test_*.py` (16 files) | Manual integration scripts that `curl`/`urlopen` a live `localhost:8000` server (auth, profile, projections, password reset, onboarding flows). Not a pytest suite — no fixtures, no config, run ad hoc. | **Consolidate** — move into `backend/tests/` and convert to real `pytest` tests (or at minimum a `scripts/manual/` folder) so they stop cluttering repo root and start running in CI once CI exists. Not yet actioned. |
| `test_browser_results.html` | Looks like a generated output artifact from a test run, not source. | **Remove** — regenerable output shouldn't be committed; add pattern to `.gitignore` if these scripts are kept. |
| `delete_all_users.py` | Destructive admin script, no confirmation prompt, sits at repo root next to everything else. | **Move + guard** — relocate to `backend/scripts/` and add a confirmation prompt / require an explicit `--yes` flag before it runs. Not yet actioned; flagged as a risk in Known issues above. |
| `Example.xlsx`, `One Time costs.xlsx`, `Recurring costs.xlsx`, `Ref Data Childcare cost byZip.xlsx` | Source spreadsheets for the reference cost data compiled into `frontend/src/data/*.ts` (per `frontend/README.md`). | **Keep** — legitimate data provenance; low priority to reorganize into a `data/` or `reference/` subfolder for tidiness. |

Remaining rows are still tracking-list-only (not yet actioned) — say the word on any of them and I'll execute it.
