# Implementation Plan — F-001 Repository foundation

- **Status:** In Progress
- **Related SPEC:** [SPEC.md](SPEC.md)
- **Related ADRs:** [0001](../../adr/0001-modular-monolith.md), [0002](../../adr/0002-database-environments.md)

## 1. Implementation approach

Create the monorepo skeleton first, then wire configuration and health, then CI. No feature code lands before the gates exist.

## 2. Ordered tasks

| # | Task | Files | Red first | Green |
|---|---|---|---|---|
| T1 | Directory layout + root scripts | `package.json`, `pnpm-workspace.yaml`, `apps/api`, `apps/web` | — | layout exists |
| T2 | Backend project + settings | `pyproject.toml`, `app/core/config.py` | `test_settings_requires_secret` | settings |
| T3 | Health endpoint + logging middleware | `app/api/v1/health.py`, `app/core/logging.py` | `test_health_ok`, `test_health_db_down` | endpoints |
| T4 | CORS + error handlers | `app/main.py`, `app/core/errors.py` | `test_cors_allowlist` | middleware |
| T5 | CI workflow | `.github/workflows/ci.yml` | — | green run |
| T6 | Docs: README, runbook, `.env.example` | `README.md`, `docs/runbooks/local-development.md` | — | docs |

## 3. Database and migration plan

No tables in F-001; Alembic is configured so F-002 can add `0001_identity`.

## 4. API and frontend plan

Only `/api/v1/health`; the web app is scaffolded with Vite, router, Pinia, and Tailwind, showing a placeholder page until F-002.

## 5. Test plan

- `test_health_ok` — `200` with version.
- `test_health_db_down` — `503` when the session factory raises.
- `test_settings_requires_secret` — startup fails without `JWT_SECRET`.
- CI: fresh install, lint, type, test, build.

## 6. Observability and operations

Request id header, access logs, health endpoint, runbook.

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Tooling drift between machines | Lockfiles (`uv.lock`, `pnpm-lock.yaml`) |
| CI slower than useful | Cache `uv` and `pnpm`, run jobs in parallel |

## 8. Rollout and rollback

Not deployed; rollback is deleting the scaffold branch.

## 9. Completion checklist

- [ ] Health endpoint tested.
- [ ] CI green on a fresh checkout.
- [ ] README runbook verified on a clean terminal.
- [ ] `.env` ignored.

## 10. TDD Log

| # | Cycle | Test / command | Red evidence | Green evidence |
|---|---|---|---|---|
| 1 | health | `pytest tests/test_health.py` | | |
