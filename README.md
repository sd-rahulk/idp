# AegisFlow

AegisFlow is an evidence-first autonomous multi-agent cybersecurity workflow system for the university IDP milestone. It combines a Next.js App Router workspace with a Python FastAPI worker and Supabase Auth/Postgres/Storage.

The milestone vertical slice is source-code assessment: a user signs up, creates a project, uploads a ZIP, starts a scan, the worker builds a deterministic plan, safely extracts the artifact, runs real source checks, persists evidence-backed findings, validates duplicates, and generates a printable report. No LLM credential is required.

## Architecture

```text
Browser -> Next.js (Auth/RLS-protected API) -> Supabase Auth/Postgres/Storage
                                      |                 ^
                                      v                 |
                              Python FastAPI worker -----
                                      |
                       Planner -> Coordinator -> Agents
                              -> Validator -> Report
```

The browser never receives a service-role key. The worker is a separate process and must be deployed independently from Vercel.

## Prerequisites

- Node.js 20+ and npm
- Python 3.11+
- A Supabase development project
- Optional: Docker for packaging the worker; Docker is not required for local source-only development

## Environment setup

1. Copy `.env.example` to `.env.local` for the web app and to `.env` for the worker.
2. Fill in `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `DATABASE_URL`, and a long random `WORKER_AUTH_SECRET`.
3. In Supabase SQL Editor, run `supabase/migrations/202609210001_aegisflow.sql`.
4. Configure email confirmation URLs to include `http://localhost:3000/auth/callback` for local development.

## Start locally

```powershell
npm.cmd install
npm.cmd run dev
```

In a second terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r apps/worker/requirements.txt
python -m uvicorn app.main:app --app-dir apps/worker --reload --port 8000
```

Open http://localhost:3000. The worker exposes `GET /health` and receives authenticated internal scan starts at `POST /internal/scans/{scan_id}/run`.

## Tests and checks

```powershell
npm.cmd run typecheck
npm.cmd run lint
python -m pytest apps/worker/tests
```

The deterministic source rules are also usable without Semgrep. Semgrep integration is intentionally an extension point for pinned rules and is not allowed to execute the uploaded project.

## Safe source fixture

`fixtures/intentional-vulnerable-app` is a small, explicitly labeled fixture used for the review walkthrough. ZIP the folder and upload it from the project intake page. It contains deliberate matches for hardcoded credentials, dynamic execution, disabled TLS verification, and unsafe SQL construction. The UI redacts credential values in evidence.

## Troubleshooting

- “Supabase is not configured”: copy the public Supabase variables into `apps/web/.env.local` or the repo root `.env.local` and restart Next.js.
- Scan remains queued: confirm the worker is running, `WORKER_BASE_URL` is reachable from Next.js, and `WORKER_AUTH_SECRET` matches.
- Artifact download fails: confirm the worker has both Supabase URL and service-role key, and that the `source-artifacts` bucket exists from the migration.
- Email confirmation loops: add the callback URL to Supabase Auth redirect allow-list.

## Deployment architecture

Deploy `apps/web` to Vercel with only public Supabase variables plus server-only integration variables. Deploy `apps/worker` to a container host with egress controls, the database URL, Supabase service role, and worker secret. Do not run the worker as a Vercel persistent process.

## Status

See [docs/implementation-status.md](docs/implementation-status.md) for an honest milestone checklist, [docs/demo-script.md](docs/demo-script.md) for the implementation review walkthrough, and [docs/security-model.md](docs/security-model.md) for scope and limitations.
