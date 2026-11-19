# Local development runbook

## Prerequisites

| Tool | Version | Verify |
|---|---|---|
| Python | ≥ 3.12 | `python --version` |
| uv | latest | `uv --version` |
| Node.js | ≥ 20 | `node -v` |
| pnpm | ≥ 9 | `pnpm -v` |
| Git | any recent | `git --version` |

No Docker is required for local development: SQLite is the default database.

## First run

```powershell
# 1) API
cd apps/api
copy .env.example .env
uv sync
uv run alembic upgrade head
uv run python scripts/seed_demo.py
uv run uvicorn app.main:app --reload --port 8000

# 2) Web (new terminal, repository root)
pnpm install
pnpm dev:web
```

- API: <http://127.0.0.1:8000> — interactive docs at `/docs`
- Web: <http://127.0.0.1:5173> — Vite proxies `/api` to the API

## Demo accounts

| Role | Email | Password |
|---|---|---|
| Parent | `parent@demo.example.com` | `Demo1234` |
| Student | `student@demo.example.com` | `Demo1234` |
| Teacher | `teacher@demo.example.com` | `Demo1234` |

Seeding refuses to run when `APP_ENV=production`.

## Quality gates

```powershell
pnpm verify                       # everything
cd apps/api; uv run pytest -q     # backend only
cd apps/web; pnpm test            # frontend only
```

## Common problems

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: app` | Commands run from the wrong folder | Run from `apps/api` |
| `401` on every API call | `.env` missing or `JWT_SECRET` too short | Recreate `.env` from `.env.example` |
| `no such table: users` | Migrations not applied | `uv run alembic upgrade head` |
| CORS error in the browser | Web app opened on a different origin | Use `http://127.0.0.1:5173` or add the origin to `CORS_ORIGINS` |
| `429` while testing login | Rate limit (5/minute) | Wait a minute or restart the API |
| `alembic` cannot find the app | Wrong working directory | Run from `apps/api` (alembic.ini lives there) |

## Reset the database

```powershell
cd apps/api
Remove-Item var/dev.db
uv run alembic upgrade head
uv run python scripts/seed_demo.py
```
