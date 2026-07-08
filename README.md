# NestWorth Snap

AI-powered baby budget planning app. React/Vite frontend + FastAPI/MongoDB backend.

See `CLAUDE.md` for full repo status, known issues, and the deployment plan.

## Running locally

### Prerequisites

- Python 3.11+
- Node.js + [pnpm](https://pnpm.io/) 10+
- A MongoDB Atlas connection string (or other MongoDB URI) — no local Mongo fallback is configured
- An OpenAI API key (required just to boot the backend — see note below)

### Backend

Run from the **repo root**, not `backend/` — the app uses absolute imports (`from backend.config import settings`) that only resolve with the repo root as the working directory.

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Copy `backend/.env.example` to `backend/.env` and fill in `MONGODB_URI`, `JWT_SECRET`, and `OPENAI_API_KEY`.

**Note:** the OpenAI client is constructed at module import time, so an empty/missing `OPENAI_API_KEY` crashes the whole app on startup, not just AI-summary requests (see `CLAUDE.md` Known issues). If you don't have a real key yet, a syntactically plausible dummy (e.g. `sk-test-dummy`) lets the app boot — AI-summary requests will just fail with an auth error.

Verify it's running:
- `http://localhost:8000/healthz` — health check (also confirms Mongo connectivity; check console logs, since a Mongo issue logs a warning rather than crashing)
- `http://localhost:8000/docs` — Swagger UI

### Frontend

In a separate terminal, from `frontend/`:

```powershell
pnpm install
pnpm dev
```

Runs at `http://localhost:5137`.

If `pnpm install` pauses on an interactive "Choose which packages to build" prompt (this happens the first time pnpm encounters packages like `@swc/core`/`esbuild` that ship native build scripts), press `a` to select all, then Enter — or run `pnpm approve-builds` directly. This is normal pnpm 10+ behavior, not an error.

The frontend defaults to talking to `http://localhost:8000` (see `frontend/src/lib/api.ts`). Only create `frontend/.env` (from `frontend/.env.example`) if you need to point it elsewhere.
