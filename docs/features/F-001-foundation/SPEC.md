# Feature Specification — F-001 Repository foundation

- **Status:** Approved
- **Owner:** Project maintainer (student)
- **Related backlog item:** `F-001`
- **Related ADRs:** [ADR-0001](../../adr/0001-modular-monolith.md), [ADR-0002](../../adr/0002-database-environments.md)

## 1. Problem and objective

Every later feature depends on a repository that is boring to set up and hard to break: one command to run the API, one to run the web app, deterministic dependencies, automated quality gates, and configuration that never leaks secrets. Without this, each feature re-litigates tooling.

**Objective:** a new contributor clones the repository and, following `README.md`, runs both applications and the full test suite within ten minutes on Windows or Linux.

## 2. Actors and permissions

Developers and CI only; no end user interacts with this feature.

## 3. User journeys

**J1 — First run.** Clone → `uv sync` in `apps/api` → `pnpm install` at root → copy `.env.example` → migrate → `pnpm dev:api` and `pnpm dev:web` → health endpoint and login page respond.

**J2 — Quality gate.** `pnpm verify` runs lint, type checks, unit/integration tests, and build for both apps and fails on the first regression.

## 4. Scope

**In scope:** monorepo layout, pinned toolchain (`uv`, `pnpm`), environment configuration, health endpoint, CORS, logging, CI workflow, formatter/linter/type-checker configuration, `.gitignore`, `README`, runbook.

**Out of scope:** deployment infrastructure, container orchestration, database provisioning, monitoring stack, feature code.

## 5. Functional requirements

| ID | Requirement |
|---|---|
| FR-01 | The repository **shall** use the layout `apps/api`, `apps/web`, `docs/`, `.github/`. |
| FR-02 | `apps/api` **shall** be installable with `uv sync` from a lockfile. |
| FR-03 | The root **shall** provide `pnpm install`, `pnpm dev:api`, `pnpm dev:web`, `pnpm verify`. |
| FR-04 | Configuration **shall** come from environment variables validated at startup; missing required values fail fast with a clear message. |
| FR-05 | `GET /api/v1/health` **shall** return status, version, and database connectivity. |
| FR-06 | CI **shall** run backend lint/type/tests and frontend lint/type/tests/build on every push and pull request. |
| FR-07 | The API **shall** allow CORS only for configured origins. |
| FR-08 | `.env`, build output, coverage, and caches **shall** be git-ignored. |

## 6. Business rules and invariants

- No secret is ever committed; `.env.example` documents every variable with a safe placeholder.
- Tests use SQLite; CI additionally runs migrations against PostgreSQL 16.
- The API refuses to start in production without a JWT secret of at least 32 bytes.

## 7. UX/API behavior

`GET /api/v1/health` → `200 {"status":"ok","version":"0.1.0","db":"ok"}`; database failure → `503 {"status":"degraded","db":"error"}`.

## 8. Data impact

None beyond the initial migration from F-002.

## 9. Security and privacy

Secrets via environment; `.env` ignored; CI uses throwaway secrets; no production data in tests.

## 10. Edge cases

Missing `DATABASE_URL` → startup error listing the variable. Port already in use → documented in the runbook. Node or Python version too old → preflight check with a readable message.

## 11. Acceptance criteria

**AC-1** Given a clean clone, when I follow the README, then both apps start and `/api/v1/health` returns `200`.
**AC-2** Given a deliberate lint error, when I run `pnpm verify`, then it fails with a non-zero exit code.
**AC-3** Given CI on a pull request, when it runs, then backend and frontend jobs pass on a fresh checkout.
**AC-4** Given `.env` exists, when I run `git status`, then it is not listed.

## 12. Test strategy

Smoke tests for health and configuration validation; a CI job that builds both apps from scratch; a check that `git check-ignore .env` succeeds.

## 13. Dependencies and open questions

None. Python 3.12+ and Node 20+ are required.

## 14. Definition of Ready

- [x] Backlog entry exists.
- [x] SPEC and PLAN exist.
- [x] Acceptance criteria testable.
- [x] ADR-0001 and ADR-0002 accepted.
