# ADR-0001: Modular monolith with a Vue SPA and a FastAPI API

- **Status:** Accepted
- **Date:** 2026-11-19
- **Decision owners:** Project maintainer

## Context

«مدرسه من» is a course project built by a single developer, but it must demonstrate professional engineering: clear boundaries, testability, and a structure that can grow into the planned modules (timetable, assignments, announcements, grades, messaging). The domain is cohesive (one school, one data model), traffic is low, and the team is one person. Splitting into services would add deployment, networking, and consistency costs with no benefit.

## Decision

Build a **modular monolith** in a single repository:

- `apps/api` — FastAPI application organized by domain module (`identity`, `people`, `timetable`, `assignments`, `announcements`, `grades`, `messaging`), with layers: `api` (HTTP) → `services` (use cases) → `repositories` (persistence) → `models`.
- `apps/web` — Vue 3 + TypeScript SPA that talks to the API over `/api/v1` and is served independently in development (Vite proxy).
- Cross-module communication goes through service interfaces, never through another module's tables.

## Alternatives considered

| Option | Pros | Cons | Why rejected |
|---|---|---|---|
| Microservices per domain | Independent deploys, isolation | Network complexity, distributed transactions, ops burden | Disproportionate for one developer, one school |
| Next.js full-stack (single app) | One runtime, simple deploy | Weak separation of API contract, harder to test domain logic in Python | The course requires FastAPI on the backend |
| Django monolith with templates | Batteries included, admin | Course requires Vue SPA + FastAPI; less explicit API-first design | Requirement mismatch |

## Consequences

**Positive:** simple local setup, one deployable unit, explicit module boundaries that can later be extracted, fast test cycles.

**Negative:** the monolith can erode into a big ball of mud if module boundaries are not enforced in review; scaling is vertical only.

**Follow-ups:** enforce import rules between modules in review; revisit only if a module needs an independent release cadence.

## References

- [ARCHITECTURE.md](../ARCHITECTURE.md)
- [SRS.md](../SRS.md)
