# Course submission — «مدرسه من» / My School

> Fill the fields marked `TODO` before uploading to Eleren (ایلرن).

## 1. Student and course

| Field | Value |
|---|---|
| Student name | TODO |
| Student number | TODO |
| Course | TODO |
| Instructor | TODO |
| Submission date | TODO |

## 2. Repository

| Field | Value |
|---|---|
| Repository URL | <https://github.com/a2004k1383-boop/my-school> |
| Default branch | `main` |
| Release tag | `v0.1.0` |
| HEAD commit | see `git log -1 --oneline` (tagged `v0.1.0`) |
| Visibility | **private** — add the instructor as a collaborator, or make the repository public before submitting |
| CI | GitHub Actions: `api` and `web` jobs green |

## 3. What was delivered

- Rewritten engineering governance for the school domain: `AGENTS.md`, `Task-List.md`.
- Requirements and architecture: `docs/SRS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`.
- Architecture decision records: `docs/adr/0001`…`0005`.
- Feature F-001 (foundation) and F-002 (identity) with `SPEC.md` + `PLAN.md`.
- Backend: FastAPI registration, login, refresh rotation, logout, `/me`, health, migrations, seed.
- Frontend: Persian/RTL login, registration, dashboard, route guards, in-memory access token, silent refresh.
- Automated tests: 29 backend tests, 20 frontend tests.
- Starter → project mapping: `docs/REWRITE-MAP.md`.

## 4. How to run (3 commands)

```bash
cd apps/api && uv sync && uv run alembic upgrade head && uv run uvicorn app.main:app --port 8000
pnpm install && pnpm dev:web
# open http://127.0.0.1:5173
```

Demo login: `parent@demo.example.com` / `Demo1234` (after `uv run python scripts/seed_demo.py`).

## 5. Evidence

| Check | Command | Result |
|---|---|---|
| Backend tests | `cd apps/api && uv run pytest -q` | **29 passed**, coverage **93%** |
| Backend lint | `uv run ruff check .` | **All checks passed** |
| Backend format | `uv run ruff format --check .` | **35 files already formatted** |
| Backend types | `uv run mypy app` | **no issues in 24 source files** |
| Migration | `uv run alembic upgrade head` | `0001_identity` applied |
| Seed + smoke | `uv run python scripts/seed_demo.py && uv run python scripts/smoke_test.py` | **SMOKE OK** (health, docs, login, me, refresh) |
| Frontend tests | `cd apps/web && pnpm test` | **20 passed** (4 files) |
| Frontend types | `pnpm typecheck` | clean |
| Frontend lint | `pnpm lint` | clean |
| Frontend build | `pnpm build` | 171 kB JS / 57 kB gzip |
| CI | GitHub Actions on `main` | **success** (api + web) |

## 6. Requirement coverage

| Course requirement | Where |
|---|---|
| Project folder with copied starter structure | repository root + `docs/REWRITE-MAP.md` |
| Rewritten `AGENTS.md` (English) | `AGENTS.md` |
| `Task-List.md` filled before implementation | `Task-List.md` |
| `SPEC.md` + `PLAN.md` per feature | `docs/features/F-001-foundation/`, `docs/features/F-002-identity/` |
| ADR per architectural decision | `docs/adr/` |
| Login and registration pages | `apps/web/src/modules/auth/views/` |
| Vue.js frontend | `apps/web` |
| FastAPI backend | `apps/api` |
| TDD | `apps/api/tests/`, `apps/web/src/**/tests/`, `PLAN.md §TDD Log` |
| GitHub repository | <https://github.com/a2004k1383-boop/my-school> |

## 7. Known limitations

- Email verification, password reset, and 2FA are out of scope for F-002.
- Teacher onboarding uses one shared invite code; per-teacher codes are future work (ADR-0005).
- Browser E2E (Playwright) is not part of this milestone; journeys are covered by API integration tests and component tests.
- PostgreSQL is exercised in CI only; local development uses SQLite.
- Demo accounts are seeded only in development.

## 8. Next milestones

F-003 school structure (classes, enrolments, parent–child links) → F-004 timetable → F-005 assignments → F-006 announcements → F-007 grades.
