# Course submission â€” Â«Ù…Ø¯Ø±Ø³Ù‡ Ù…Ù†Â» / My School

> Fill the fields marked `TODO` before uploading to Eleren (Ø§ÛŒÙ„Ø±Ù†).

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
| Repository URL | TODO (filled after `gh repo create`) |
| Default branch | `main` |
| Feature branch / PR | `feat/f002-identity` |
| Release tag | `v0.1.0` |
| HEAD commit | TODO |
| Visibility | private â€” access granted to the instructor (collaborator) or made public |

## 3. What was delivered

- Rewritten engineering governance for the school domain: `AGENTS.md`, `Task-List.md`.
- Requirements and architecture: `docs/SRS.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`.
- Architecture decision records: `docs/adr/0001`â€¦`0005`.
- Feature F-001 (foundation) and F-002 (identity) with `SPEC.md` + `PLAN.md`.
- Backend: FastAPI registration, login, refresh rotation, logout, `/me`, health, migrations, seed.
- Frontend: Persian/RTL login, registration, dashboard, route guards, in-memory access token, silent refresh.
- Automated tests: 29 backend tests, 20 frontend tests.

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
| Backend tests | `cd apps/api && uv run pytest -q` | 29 passed |
| Backend lint | `uv run ruff check .` | TODO |
| Backend types | `uv run mypy app` | TODO |
| Frontend tests | `cd apps/web && pnpm test` | 20 passed |
| Frontend types | `pnpm typecheck` | TODO |
| Frontend build | `pnpm build` | TODO |
| CI | GitHub Actions on `main` | TODO |

## 6. Requirement coverage

| Course requirement | Where |
|---|---|
| Project folder with copied starter structure | repository root + `docs/REWRITE-MAP.md` (to add) |
| Rewritten `AGENTS.md` (English) | `AGENTS.md` |
| `Task-List.md` filled before implementation | `Task-List.md` |
| `SPEC.md` + `PLAN.md` per feature | `docs/features/F-001-foundation/`, `docs/features/F-002-identity/` |
| ADR per architectural decision | `docs/adr/` |
| Login and registration pages | `apps/web/src/modules/auth/views/` |
| Vue.js frontend | `apps/web` |
| FastAPI backend | `apps/api` |
| TDD | `tests/` + `docs/features/F-002-identity/PLAN.md Â§TDD Log` |
| GitHub repository | TODO |

## 7. Known limitations

- Email verification, password reset, and 2FA are out of scope for F-002.
- Teacher onboarding uses one shared invite code; per-teacher codes are future work (ADR-0005).
- DOM-based E2E (Playwright) is not part of this milestone; journeys are covered by API integration tests and component tests.
- PostgreSQL is exercised in CI only; local development uses SQLite.

## 8. Next milestones

F-003 school structure (classes, enrolments, parentâ€“child links) â†’ F-004 timetable â†’ F-005 assignments â†’ F-006 announcements â†’ F-007 grades.
