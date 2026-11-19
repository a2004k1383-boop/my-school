# ADR-0002: SQLite for local development and PostgreSQL for production

- **Status:** Accepted
- **Date:** 2026-11-19
- **Decision owners:** Project maintainer

## Context

The project must be easy to run on a student laptop (Windows, no Docker guarantee) while still demonstrating production-grade persistence decisions. Production will run on a managed PostgreSQL instance. Tests must be fast enough to run on every save.

## Decision

- **Local development and unit/integration tests:** SQLite via `aiosqlite`, file for dev, in-memory for tests.
- **CI and production:** PostgreSQL 16 via `DATABASE_URL`; CI runs the full migration chain and the integration suite against it.
- **Schema management:** Alembic only; the application never calls `create_all()` outside test fixtures.
- **Portability rules:** no `citext`, no PostgreSQL-only defaults in models; use expression indexes compatible with both engines; timestamps generated in Python (UTC); UUIDs stored as `CHAR(36)`.

## Alternatives considered

| Option | Pros | Cons | Why rejected |
|---|---|---|---|
| PostgreSQL only (Docker required) | One engine everywhere | Blocks contributors without Docker; slower onboarding | Course environment does not guarantee Docker |
| SQLite only | Zero setup | No real concurrency, no production parity | Does not demonstrate production readiness |
| MySQL/MariaDB | Ubiquitous | Weaker JSON/constraint ergonomics for this domain | No added value here |

## Consequences

**Positive:** instant local start, fast tests, and a CI check that catches Postgres drift.

**Negative:** two engines mean occasional behavioural differences; developers must run CI (or Docker) before touching migrations.

**Follow-ups:** add a `docker compose` profile for Postgres as soon as Docker is available; keep the migration test in CI mandatory.

## References

- [ARCHITECTURE.md](../ARCHITECTURE.md#10-persistence-and-migrations)
