# Implementation Plan — F-002 Identity: registration, login, and sessions

- **Status:** In Progress
- **Related SPEC:** [SPEC.md](SPEC.md)
- **Related ADRs:** [0003](../../adr/0003-authentication-session-strategy.md), [0005](../../adr/0005-role-model-and-teacher-onboarding.md)

## 1. Implementation approach

Modular monolith: `apps/api` (FastAPI) and `apps/web` (Vue 3), one repository.

Backend layering: `api/v1/auth.py` (HTTP) → `services/auth_service.py` (use cases) → `repositories/` (SQLAlchemy) → `models/`. Security primitives live in `core/security.py` (hashing, JWT, refresh-token hashing). Configuration in `core/config.py` via `pydantic-settings`.

Frontend: `modules/auth` owns the store, API calls, validation, and views; `shared/api/http.ts` owns fetch, bearer injection, single-flight refresh, and problem+json parsing; `shared/i18n` owns the Persian copy.

## 2. Ordered tasks

| # | Task | Files | Red test first | Green | Docs |
|---|---|---|---|---|---|
| T1 | Repo skeleton, config, health endpoint | `apps/api/app/main.py`, `core/config.py`, `api/v1/health.py`, `pyproject.toml` | `test_health_returns_ok` | health router + settings | README |
| T2 | Test harness (async DB, app factory, factories) | `tests/conftest.py` | a smoke test that uses the client | fixtures | PLAN |
| T3 | User model + migration | `models/user.py`, `alembic/versions/0001_identity.py` | model test (unique email) | model + migration | ARCHITECTURE |
| T4 | Password hashing + policy | `core/security.py`, `domain/password_policy.py` | `test_hash_*`, `test_policy_*` | implementation | ADR-0003 |
| T5 | Register endpoint | `schemas/auth.py`, `services/auth_service.py`, `api/v1/auth.py` | B01–B05 | implementation | SPEC examples |
| T6 | Login + rate limit | same + `core/rate_limit.py` | B06–B09 | implementation | README |
| T7 | Refresh rotation + reuse detection | `models/refresh_token.py`, service | B10–B12 | implementation | ADR-0003 |
| T8 | Logout + me + JWT errors | `api/v1/auth.py`, `core/security.py` | B13–B14 | implementation | OpenAPI |
| T9 | Problem+json handlers + audit log | `core/errors.py`, `models/audit_log.py` | B15–B16 | implementation | SPEC §7.2 |
| T10 | Seed script + runbook | `scripts/seed_demo.py`, `docs/runbooks/local-development.md` | seed test | implementation | runbook |
| T11 | Frontend scaffold, router, auth store, HTTP client | `apps/web/src/...` | F10, F11 | implementation | README |
| T12 | Login/Register/Dashboard views + a11y | views, components, `fa.ts` | F01–F09, F12, F13 | implementation | SPEC copy deck |
| T13 | E2E + screenshots + CI | `e2e/`, `.github/workflows/ci.yml` | F14 | implementation | submission |

## 3. Database and migration plan

- `0001_identity`: `users`, `refresh_tokens`, `audit_log`; unique index `uq_users_email_lower` on `lower(email)`; indexes on `refresh_tokens.family_id`, `refresh_tokens.user_id`, `audit_log.created_at`.
- SQLite compatibility: use `UUID` stored as `CHAR(36)`, avoid `citext`, avoid `server_default=now()`; timestamps set in Python (UTC).
- PostgreSQL: run the same migration in CI; the partial unique index is created portably with an expression index.
- Rollback: `alembic downgrade -1` drops the three tables (tested in CI on an empty database).

## 4. API and frontend plan

Endpoints exactly as in `SPEC.md §7.2`. Response models are Pydantic v2; the OpenAPI schema is the contract.

Frontend routes: `/login`, `/register`, `/dashboard` (guarded), `/404`. Store actions: `register`, `login`, `logout`, `bootstrap`. `http.ts` retries once after refresh; parallel 401s share one refresh promise.

## 5. Test plan

### Backend (pytest)

| ID | Test | Asserts |
|---|---|---|
| B01 | register parent | 201, persisted, no hash in response |
| B02 | duplicate email (case-insensitive) | 409 `email_already_registered` |
| B03 | invalid email / weak password / mismatch | 422 + `errors[]` |
| B04 | teacher without/invalid invite | 403 `invitation_required`, no user |
| B05 | teacher with valid invite | 201 + audit row |
| B06 | login success | token + cookie flags (`HttpOnly`, `SameSite=Lax`, `Path=/api/v1/auth`) |
| B07 | wrong password vs unknown email | identical 401 |
| B08 | disabled user | 403 `account_disabled` |
| B09 | sixth failed login | 429 + `Retry-After` |
| B10 | refresh rotates | new cookie, old token 401, `replaced_by` set |
| B11 | refresh reuse | family revoked, 401 `refresh_reused` |
| B12 | expired/absent refresh | 401 `refresh_expired` |
| B13 | logout | 204, cookie cleared, token revoked |
| B14 | `/me` valid/missing/expired | 200 / 401 / 401 `token_expired` |
| B15 | audit + problem+json | teacher registration audited; error envelope shape |
| B16 | OpenAPI contract | endpoints, tags, error models present |
| B17 | migration | `alembic upgrade head` on SQLite; Postgres in CI |

### Frontend (Vitest + MSW)

| ID | Test | Asserts |
|---|---|---|
| F01 | login renders | accessible names, RTL |
| F02 | empty submit | field errors, no request, `aria-invalid` |
| F03 | invalid email | message, focus first invalid, no request |
| F04 | 401 | Persian alert, email kept, password cleared |
| F05 | login success | store hydrated, redirect honours `?redirect=` |
| F06 | password mismatch | confirm-field error |
| F07 | teacher role | invite field appears and is required |
| F08 | register success | redirect to `/login?registered=1` |
| F09 | 409 | field-level email error |
| F10 | guards | anonymous → login; authenticated → dashboard |
| F11 | single-flight refresh | two 401s → one refresh call |
| F12 | logout | store cleared, redirect |
| F13 | axe smoke | no critical violations |
| F14 | Playwright | full journey + screenshots |

## 6. Observability and operations

- Request-id middleware; structured JSON logs in production, human logs in dev.
- `/health` reports DB connectivity; no secrets.
- Login failures counted without exposing emails.
- Runbook: reset local DB, re-run migrations, seed demo users.

## 7. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Refresh-token races in multiple tabs | Server: rotation + reuse detection; client: single-flight |
| Accidental user enumeration via timing | Same code path and message; constant work for unknown users (dummy hash verify) |
| SQLite/Postgres drift | CI runs migrations and tests against both |
| Teacher invite leakage | Env-only secret, constant-time compare, never logged, audit stores identifier only |

## 8. Rollout and rollback

Single migration; deploy backend before frontend. Rollback: downgrade migration and revert the frontend bundle together — sessions are invalidated by design (refresh tokens dropped).

## 9. Completion checklist

- [ ] AC-1…AC-14 pass.
- [ ] TDD tests added and recorded in §10.
- [ ] SQLite tests pass; PostgreSQL migration test passes in CI.
- [ ] Lint and type checks pass for both apps.
- [ ] Migration reviewed and tested.
- [ ] Security/privacy review complete (enumeration, cookies, rate limits, logging).
- [ ] Docs and `Task-List.md` updated.

## 10. TDD Log

| # | Cycle | Test / command | Red evidence | Green evidence |
|---|---|---|---|---|
| 1 | Academic time | `uv run pytest tests/test_unit.py -q` | `zoneinfo._common.ZoneInfoNotFoundError: 'No time zone found with key Asia/Tehran'` — Windows ships no IANA database | added `tzdata>=2024.1`; 7 passed |
| 2 | Focus management | `pnpm --filter @myschool/web test` | `expected <body></body> to be <input id="email">` — the view was mounted detached, so `document.activeElement` was `<body>` | mounted with `attachTo: document.body`; 20 passed |
| 3 | API contract | `uv run pytest -q` | Tests were committed at `983356a` before any implementation; at that commit `apps/api` has no `pyproject.toml` and no `app` package, so collection cannot import the application (exit 2) | implementation commit `197380d`; `29 passed`, coverage 93% |
| 4 | Web auth flows | `pnpm --filter @myschool/web test` | Authored from `SPEC.md` before the views existed (tests referenced `loginUser`/`registerUser` mocks and would fail on import) | implementation commit `fcbadd9`; `20 passed` |
| 5 | End-to-end smoke | `uv run python scripts/smoke_test.py` | Login with the seeded account returned `422` — `email-validator` rejects the reserved `.local` domain | demo domain changed to `demo.example.com`; `SMOKE OK` (health, docs, login, me, refresh) |

> Note: tests 3 and 4 were authored before their implementation commits (see `git log`), but the red state was a collection/import failure rather than a behavioural assertion failure. The two behavioural red→green cycles actually observed are #1, #2 and #5.
