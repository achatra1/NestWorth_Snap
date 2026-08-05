# Deployment

**Stack: Vercel (frontend) + Railway (backend) + MongoDB Atlas (DB), all on free/hobby tiers.**

Status: fully live as of 2026-08-03 (frontend on Vercel, backend on Railway connected to Atlas, CORS configured, end-to-end smoke test passed). This doc covers how to reproduce or redeploy the stack. See `CLAUDE.md`'s Deployment plan section for the full failure-by-failure history if a redeploy regresses any of the issues below — this doc only states the working configuration.

## 1. MongoDB Atlas

1. Create a free (M0) cluster.
2. Create a database user with a strong password.
3. Under **Network Access**, allow `0.0.0.0/0`.
   - Atlas rejects connections from non-allowlisted IPs with a generic TLS handshake failure (`TLSV1_ALERT_INTERNAL_ERROR`), not a timeout — if you see that error, check this first, before suspecting OpenSSL/runtime issues.
4. Copy the connection string for `MONGODB_URI`.

## 2. Railway backend

- **Root Directory**: repo root — **do not** point it at `backend/`. The app uses absolute imports (`from backend.config import settings`), which only resolve with the repo root as the working directory and `backend/` as a package.
- Build/deploy config lives in two files at the repo root:
  - `nixpacks.toml` — declares `nixPkgs` (`python311`, `stdenv.cc.cc.lib` for `libstdc++.so.6` needed by pandas/numpy), creates a venv at `/opt/venv`, installs `backend/requirements.txt` into it (working around Nix's PEP 668 externally-managed-environment restriction), and starts uvicorn with `LD_LIBRARY_PATH` appended (not prepended — prepending Nix's lib dir ahead of the system path risks shadowing the OpenSSL Python's `_ssl` module was built against, which manifests as the same Atlas TLS alert described above).
  - `railway.json` — deploy-level settings only (`healthcheckPath: /healthz`, `restartPolicyType`). Build config stays entirely in `nixpacks.toml`.
- Required environment variables:
  - `MONGODB_URI`
  - `JWT_SECRET`
  - `CORS_ORIGINS` (comma-separated; must include the live Vercel URL)
  - `OPENAI_API_KEY` (required at boot — see `CLAUDE.md` Known Issues; an empty value crashes the app on import, not just AI-summary requests)
  - `APP_ENV=production`
  - `PORT` is injected automatically by Railway; `railway.json`'s start command reads it.
- **Debugging a failed healthcheck**: Railway's healthcheck retry panel only shows pass/fail, never the actual error. Check the service's **Deploy Logs** tab (separate from Build Logs) for the real stdout/stderr, including Python tracebacks. If every attempt fails identically (not intermittently), that means the process crashed before binding to a port — check Deploy Logs first.

## 3. Vercel frontend

- Import `frontend/` as the **project root** (not the repo root).
- Set `VITE_API_BASE_URL` to the Railway backend's public URL.
- `frontend/vercel.json` provides the SPA rewrite rule.

## 4. Wire them together

1. Deploy backend first, note its public Railway URL.
2. Set `VITE_API_BASE_URL` on Vercel to that URL, deploy frontend, note its public Vercel URL.
3. Set `CORS_ORIGINS` on Railway to the Vercel URL, redeploy backend.
4. Smoke-test end-to-end: signup, login, complete onboarding, view projection, generate AI summary, download PDF.

## Known deployment risks (unresolved)

See `CLAUDE.md` Known Issues for the current list (no rate limiting, `OPENAI_API_KEY` required at boot, no CI/Dockerfile, `APP_ENV` must never be `development` outside a dev machine). Don't duplicate that list here — check `CLAUDE.md` for the live version.
