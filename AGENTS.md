# AGENTS.md — Engineering Rules for AI Agents

> Project: **«مدرسه من» / My School** — a school–parent–student communication platform.
> Stack: **Vue 3 + TypeScript** (frontend), **FastAPI + SQLAlchemy 2.x** (backend), **PostgreSQL** (production), **SQLite** (local tests).
> This file is binding for every human and AI contributor. Read it before touching the repository.

## 1. Mission and product context

You are contributing to a production-minded school communication platform used by three roles:

1. **Parent (والد)** — follows their children's week: assignments and due dates, school announcements, grades and progress.
2. **Student (دانش‌آموز)** — sees their own timetable, assignments, announcements, and grades.
3. **Teacher (معلم)** — publishes assignments and announcements for the classes they teach, and records grades.

The product replaces paper notes, scattered chat groups, and phone calls with one reliable place for school information. It is **not** a general social network, and it is **not** a full school-management system (no finance, no HR, no admissions).

Correctness of **authorization** (who may see which child's data), **academic time** (due dates and weeks in `Asia/Tehran`), **privacy of minors**, and **auditability of grade changes** is critical. A pretty UI that leaks another family's data is a failed feature.

Your job is to make the smallest correct, maintainable, secure change that satisfies an approved specification. Do not silently expand scope.

## 2. Source-of-truth hierarchy

When instructions conflict, use this order:

1. Explicit user instruction for the current task.
2. Approved feature `SPEC.md`.
3. Approved feature `PLAN.md`.
4. Accepted ADRs in `docs/adr/`.
5. `docs/SRS.md` and `docs/ARCHITECTURE.md`.
6. Existing implementation and tests.
7. Your assumptions.

Never treat an assumption as an approved requirement. Record unresolved product or technical questions in the feature spec and ask for clarification when the answer changes data integrity, security, user-visible behavior, or scope.

## 3. Mandatory feature intake gate

Before implementing any new feature or material behavior change:

1. Read this file, the relevant architecture, SRS, ADRs, and existing code.
2. Add the feature to `Task-List.md` with a unique ID, owner/status, dependencies, priority, and links to its documents.
3. Create the feature folder `docs/features/<FEATURE-ID>-<short-name>/`.
4. Create **both** `SPEC.md` and `PLAN.md` in that folder, using the templates in `docs/templates/`.
5. In `SPEC.md`, define problem, actors, scope, non-goals, user journey, requirements, business rules, API/UI behavior, data impact, security/privacy, edge cases, and measurable acceptance criteria.
6. In `PLAN.md`, list ordered implementation steps, tests to write first, migration/rollback approach, documentation changes, and completion checks.
7. Identify architectural decisions. If a decision changes system boundaries, data model strategy, consistency, security, deployment, integrations, or a long-lived dependency, create an ADR under `docs/adr/`. If no ADR is needed, state why in the plan.
8. Obtain human approval of the specification and plan when the work changes product behavior, data contracts, security, or architecture.
9. Only then begin implementation.

Do not create empty placeholder specs merely to bypass this gate. A small bug fix may use a lightweight issue entry, but any behavior change still requires an explicit test and documented expected behavior.

## 4. Required development method: TDD

Use Red → Green → Refactor for every behavior change:

1. **Red:** write a focused test that expresses the required behavior and fails for the expected reason.
2. **Green:** implement the minimum code needed to pass the test.
3. **Refactor:** improve structure without changing behavior; keep the tests green.
4. Add regression tests for discovered defects.
5. Run the relevant test suite after each meaningful change.

Do not write implementation first and retroactively add superficial tests. Tests must assert observable behavior, not private implementation details. Every TDD cycle is recorded in the feature `PLAN.md` §TDD Log with the command used and the observed red/green evidence.

### Test layers

- **Unit tests** — pure business rules: grade averaging, due-date math, week resolution, validation, error mapping.
- **Integration tests** — repositories, transactions, API endpoints, migrations, authorization boundaries.
- **Contract tests** — API schemas and error envelopes.
- **End-to-end tests** — critical journeys across browser and API (register → login → dashboard).
- **Security tests** — object-level access (a parent must not read another family's child), role escalation, rate limits, session/token behavior.
- **Accessibility tests** — the auth pages must pass a structural smoke check: every input labelled, errors announced, focus moved to the first invalid field.

SQLite is useful for fast local tests. PostgreSQL is authoritative for production behavior and must be used in CI for migration and concurrency-sensitive tests.

## 5. Architecture principles

- Start with a **modular monolith** and explicit domain boundaries (`identity`, `people`, `timetable`, `assignments`, `announcements`, `grades`, `messaging`).
- Keep business rules out of FastAPI route handlers and Vue components.
- Separate API, application/use-case, domain, and infrastructure concerns.
- Depend on interfaces/ports in application logic; isolate email, SMS, and storage vendors behind adapters.
- Use dependency injection at module boundaries.
- Prefer boring, proven technology over novelty.
- Avoid premature microservices, event sourcing, CQRS, and unnecessary abstractions.
- Make important side effects explicit and observable.
- Use UTC for persisted instants; use `Asia/Tehran` for academic calendar rules (week start, due dates, holidays) and display.
- Never assume a local wall-clock time uniquely identifies an instant.

## 6. Backend rules

- Use Python type hints throughout production code.
- Use FastAPI routers only for HTTP concerns: parsing, authentication context, response mapping, status codes.
- Put use cases in application services and invariants in domain logic.
- Use Pydantic v2 request/response schemas; never expose ORM objects directly.
- Use SQLAlchemy 2.x typed mappings and explicit transaction boundaries.
- Use Alembic for every schema change. Never rely on `create_all()` in production.
- Keep database sessions request-scoped and close them reliably.
- Do not perform network calls while holding a database transaction or row lock.
- Use stable error codes and a consistent error envelope (`application/problem+json`).
- Validate ownership and authorization server-side on every protected operation.
- Use pagination for potentially unbounded collections.
- Do not log passwords, tokens, grades, or unnecessary personal data.

## 7. Domain rules (school correctness)

These are invariants, not suggestions:

**Identity and roles**
- A user has exactly one primary role: `parent`, `student`, or `teacher`. Multi-role support is a future decision and requires an ADR.
- Self-registration is open to parents and students. Teacher registration requires a valid **teacher invite code** (`TEACHER_INVITE_CODE`) and is recorded in the audit trail.
- Email is unique, case-insensitive, and normalized (trimmed, lowercased).
- A disabled user cannot authenticate; existing sessions must stop working.

**Relationships (from F-003 onward)**
- A parent sees only the children explicitly linked to their account.
- A teacher sees only the classes they are assigned to.
- A student sees only their own records.
- Every query that returns child-scoped data must be filtered by relationship, not by trusting a client-supplied ID.

**Academic time**
- The academic week is defined in `Asia/Tehran`; a "week" is Saturday→Friday.
- Assignment due dates are stored as UTC instants, displayed in `Asia/Tehran`.
- A due date is inclusive to the end of its local day when the product says "until the end of the day". This must be explicit in the SPEC, not guessed.
- DST is not currently observed in Iran, but the code must not hard-code that assumption; timezone rules live in one module.

**Announcements**
- Read/unread state is per user and idempotent (marking read twice is not an error).
- Deleting an announcement does not delete its audit record.

**Grades**
- Grades are stored with their numeric scale and weight; averages are computed from stored facts, never from rounded display values.
- Any grade change by a teacher is audited: who, when, previous value, new value, reason (optional).
- Parents and students see only published grades; drafts are teacher-only.

## 8. Frontend rules

- Use Vue 3 Composition API with TypeScript and `<script setup>`.
- Keep pages, reusable components, composables, API clients, stores, and domain view models separate.
- Use Pinia for shared client state only where needed; do not mirror all server state globally.
- Use a typed API client checked against the OpenAPI schema.
- Centralize authentication handling, error mapping, and request correlation in one HTTP layer.
- Validate forms for usability, but treat backend validation as authoritative.
- Provide loading, empty, success, error, and retry states for every screen that fetches data.
- **Persian-first, RTL:** `dir="rtl"` at the document level, CSS logical properties (`margin-inline`, `padding-block`, …), Vazirmatn font, all user-facing strings in the `fa` locale module. No hard-coded Persian text inside components.
- Ensure keyboard navigation, semantic HTML, visible focus, labels, and accessible error messages.
- Do not put authorization decisions only in the UI.

## 9. API and compatibility

- Prefix public APIs with `/api/v1`.
- Use explicit request and response schemas.
- Use consistent naming, status codes, pagination, filtering, and error structures.
- Do not make breaking API changes without a documented migration/deprecation plan.
- Keep OpenAPI accurate and review generated schema changes.
- Use UTC ISO 8601 timestamps in API payloads and include timezone identifiers where local interpretation matters.

## 10. Security and privacy baseline

- Apply least privilege and deny by default.
- Enforce role permissions and resource ownership in backend use cases.
- Hash passwords with **Argon2id** via a maintained library.
- Browser sessions: short-lived access token in memory + refresh token in an `HttpOnly`, `SameSite=Lax`, `Secure`-in-production cookie; document refresh rotation, revocation, and CSRF mitigation in an ADR.
- Rate-limit login, registration, password reset, and other abuse-prone endpoints.
- Verify email addresses before enabling sensitive account actions (deferred feature; keep the design ready).
- Use short-lived, single-use password-reset tokens.
- Treat minors' data as sensitive: minimize collection, never log it, never expose it in error messages or URLs.
- Keep secrets out of source control and frontend bundles.
- Maintain audit records for privileged actions (teacher registration, grade changes, account disabling).
- Define retention, export, and deletion processes for personal data.
- Do not claim legal compliance without a documented legal and operational review.

## 11. Database and migrations

- SQLite is the default local development database and may be used for fast unit/integration tests that do not depend on PostgreSQL-specific behavior.
- PostgreSQL is the production database and the authoritative database for migration validation and concurrency tests.
- Use SQLAlchemy 2.x and Alembic.
- Keep migrations deterministic, reviewed, and reversible where practical.
- Test migrations from the previous released schema against PostgreSQL.
- Avoid SQLite-specific SQL in application logic.
- Never use SQLite in production.

## 12. External integrations and side effects

- Email and SMS providers must be behind adapter interfaces.
- Notifications (assignment reminders, announcements) use an outbox pattern: enqueue in the same transaction, deliver asynchronously.
- Do not send a message before the database transaction commits.
- Make webhook handlers authenticated, idempotent, and replay-safe.
- Retry transient failures with bounded exponential backoff; route exhausted failures to a reviewable failure state.

## 13. Observability and operations

- Use structured logs with request/correlation IDs.
- Expose health and readiness endpoints without leaking internals.
- Record metrics for API latency, error rates, authentication failures, and notification failures.
- Provide database backups, restore tests, migration procedures, and an incident runbook before production launch.
- Define retention and redaction for logs.
- Do not add monitoring infrastructure without a concrete operational requirement.

## 14. Code quality

- Follow the repository's formatter, linter, and type-checker configuration.
- Prefer clear names and small functions with one responsibility.
- Avoid broad exception catches; translate known exceptions at boundaries.
- Never suppress a failing test or weaken an assertion just to obtain a green build.
- Do not add dependencies without explaining why, checking maintenance/security posture, and updating the relevant ADR when material.
- Remove dead code and unused dependencies introduced by your change.
- Do not add TODO comments as a substitute for completing required work. If deferred, create a tracked task.

## 15. Required workflow for every task

**Before editing**

- Inspect repository structure, relevant modules, tests, and docs.
- Read linked SPEC, PLAN, and ADRs.
- Confirm the task is approved and not blocked.
- State assumptions and likely files to change in your work plan.

**During work**

- Follow TDD.
- Keep changes scoped.
- Update tests, API schemas, migrations, docs, and examples together.
- Never fabricate command output or claim tests ran if they did not.

**Before completion**

- Run formatter and linter.
- Run type checks.
- Run focused tests, then the relevant full suite.
- Run PostgreSQL integration tests when the feature touches persistence or authorization boundaries.
- Review migration upgrade and rollback behavior.
- Check authorization and privacy implications (especially child-scoped data).
- Update `Task-List.md`, feature `PLAN.md`, and relevant docs.
- Report exactly what changed, commands actually run, results, known limitations, and follow-up tasks.

## 16. Definition of Ready (DoR)

A feature is Ready only when:

- It has a `Task-List.md` entry and a unique ID.
- `SPEC.md` and `PLAN.md` exist and are reviewed.
- User journey and acceptance criteria are testable.
- Dependencies and non-goals are explicit.
- Data/API/security implications are identified.
- Required ADRs exist, or the plan records why none is required.
- Test strategy is defined, including PostgreSQL tests when relevant.

## 17. Definition of Done (DoD)

A feature is Done only when:

- All acceptance criteria pass.
- TDD evidence exists in the test suite and in `PLAN.md §TDD Log`.
- Relevant unit, integration, and E2E tests pass.
- Authorization, validation, error, and edge cases are covered.
- Migrations and rollback notes are complete.
- API documentation and user-facing behavior are updated.
- Logs/metrics are adequate for operations.
- No known critical security or data-integrity defect remains.
- `Task-List.md` and `PLAN.md` are updated.
- The agent provides an honest completion report.

## 18. Agent communication protocol

For each task, report:

1. Task ID and linked specification.
2. Understanding of expected behavior.
3. Assumptions and unresolved questions.
4. Planned files/modules and tests.
5. Implementation summary.
6. Tests and commands actually executed, with results.
7. Migration/operational impact.
8. Remaining risks or follow-up tasks.

If asked to implement a feature without its SPEC/PLAN, stop at the intake gate and create or request approval for those documents. Do not bypass this rule because the requested change appears small.

## 19. Repository and branch conventions

- Default branch: `main`. Feature branches: `feat/<feature-id>-<short-name>`.
- Commits follow Conventional Commits: `feat(identity): …`, `test(identity): …`, `docs(feature): …`, `fix(api): …`, `ci: …`, `chore: …`.
- A feature branch merges only when its tests and CI checks are green.
- Never force-push `main`; never commit `.env`, build output, coverage, or secrets.

## 20. Local quality gates

| Gate | Command | Must pass |
|---|---|---|
| Backend lint/format | `uv run ruff check .` (from `apps/api`) | yes |
| Backend types | `uv run mypy app` (from `apps/api`) | yes |
| Backend tests | `uv run pytest -q` (from `apps/api`) | yes |
| Frontend lint | `pnpm --filter @myschool/web lint` | yes |
| Frontend types | `pnpm --filter @myschool/web typecheck` | yes |
| Frontend tests | `pnpm --filter @myschool/web test` | yes |
| Frontend build | `pnpm --filter @myschool/web build` | yes |
| Everything | `pnpm verify` (repository root) | before merge |

Coverage thresholds: `apps/api/app` ≥ 80%, `apps/web/src/modules/auth` ≥ 80%. Do not game coverage with ignore comments on real logic.
