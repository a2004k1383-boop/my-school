# Delivery Roadmap — «مدرسه من» / My School

This roadmap sequences the ten features of `Task-List.md` into five phases. It is a planning aid, not an authorization to skip the intake gate: every feature still needs an approved `SPEC.md` and `PLAN.md` before implementation (`AGENTS.md` §3). Target dates are recorded as **TBD** because no calendar is committed; sequence and exit criteria are binding, dates are not.

## Phase 0 — Foundation and identity (course deliverable)

**Goal:** a working, tested, secure entry point: a new contributor runs the repository, and a parent, a student, or an invited teacher can register, log in, see a role-aware dashboard, and log out.

**Features:** F-001 (repository foundation) and F-002 (identity: registration, login, sessions), including the login, registration, and dashboard pages. **Status:** F-001 `In Progress`; F-002 `Specifying`.

**Scope:** monorepo (`apps/api`, `apps/web`, `docs/`), pinned toolchains, `.env.example`, health endpoint, CI gates; `users`, `refresh_tokens`, and `audit_log` via migration `0001_identity`; Argon2id hashing, teacher invite code, rate limiting; in-memory access token plus rotating refresh cookie; Persian RTL auth pages and a role-aware dashboard; ADR-0001 … ADR-0005 accepted and the three product documents rewritten.

**Exit criteria — "done" means**

- A parent and a student register, log in, survive a reload, and log out; a teacher registers only with a valid invite code, and the registration is audited.
- Refresh rotation, reuse detection, logout, and `/auth/me` are covered by automated tests on SQLite, with the migration chain also run against PostgreSQL in CI.
- Invalid credentials, duplicate email, disabled account, and rate-limited requests return the documented problem+json errors, with no user enumeration.
- The auth and dashboard pages pass the axe smoke check, are keyboard usable in RTL, and `pnpm verify` plus CI are green.

**Demo scenario:** register a parent («والد»), log in, land on the parent dashboard, reload to prove silent session restore, log out; then attempt teacher registration without a code (rejected) and with the configured code (accepted), and show the audit row.

## Phase 1 — School structure and relationships

**Goal:** the school's real structure exists in the system, so every later feature can answer "who may see this child's data" from stored relationships instead of client-supplied identifiers.

**Features:** F-003 (classes, enrolments, parent–child links, teacher assignments).

**Scope:** academic year, classes with grade level and homeroom teacher, periods with bell times, enrolments, parent links, teaching assignments, and audited maintainer scripts that load structure data while no administrator role exists.

**Exit criteria**

- Every child-scoped endpoint is filtered by relationship; another family's student id returns the same response as an unknown id.
- A student holds exactly one class per academic year and a duplicate enrolment is rejected.
- Seeded demo data covers one academic year, at least three classes, and two families.

**Demo scenario:** sign in as a parent with two linked children in different classes, show that the second family's child is invisible; sign in as a teacher and show only the assigned classes.

## Phase 2 — Weekly timetable and assignments

**Goal:** the two questions families ask most often — "what is today's schedule?" and "what is due?" — are answered correctly, including at week and timezone boundaries.

**Features:** F-004 (weekly timetable), F-005 (assignments with due dates and completion state).

**Scope:** a Saturday-first weekly grid per class with subject, teacher, period, room, and previous/next week navigation; assignment drafts and publishing with end-of-day due dates in the school timezone; server-side due states; reminder rows enqueued to the outbox.

**Exit criteria**

- A due date set for a Friday evening is still open on Friday 23:30 Tehran time and overdue on Saturday 00:01.
- Parent, student, and teacher each see exactly the timetable and assignments allowed by the permission matrix, and no draft is visible to a family.
- Reminder rows are written in the same transaction as the assignment change but delivered only after commit.

**Demo scenario:** publish an assignment due tomorrow, show it on the student dashboard, mark it complete as the student, and show the completion state on the parent view.

## Phase 3 — Announcements and grades

**Goal:** the school can inform families and show progress, with a read state families trust and a grade history the school can defend.

**Features:** F-006 (announcements with targeting and read/unread), F-007 (grades, GPA, progress chart).

**Scope:** announcement drafts and publishing per class, per-user read state, unread counts, and deletion that keeps the audit record; grade entry with value, scale, weight, and publish state; audit records for every grade change; weighted GPA from stored values and a progress chart per subject.

**Exit criteria**

- Marking an announcement read twice succeeds and changes no stored state; unread counts stay correct after a second child in the same class is linked.
- A parent never sees a draft grade or another child's grade; a teacher correction produces an audit record with previous value, new value, and actor.
- The displayed GPA matches a hand-computed weighted average of stored grades, not of rounded display values.

**Demo scenario:** publish an announcement, show the unread badge for parent and student, read it once, then publish a grade and show it appear for both with the audit trail behind it.

## Phase 4 — Messaging, notifications, production readiness

**Goal:** close the loop with simple parent–teacher messaging, reliable out-of-app notifications, and the operational evidence needed to run the product.

**Features:** F-008 (parent–teacher messaging), F-009 (outbox, email/SMS adapters, reminder scheduler), F-010 (backups, observability, security review, runbook).

**Scope:** participant-only threaded messaging between a parent and a teacher of a linked child's class with immutable messages; an outbox worker with bounded exponential backoff, retry bookkeeping, and a reviewable failure state; nightly backups with a restore drill, metrics and alerting, a security review, retention and deletion procedures, and an incident runbook.

**Exit criteria**

- A message thread is invisible to every account that is not a participant.
- A failed notification is retried without duplicating the message and without blocking the originating transaction.
- A restore drill from the latest backup reproduces a working environment within the stated RPO and RTO, and no critical or high security finding remains open.

**Demo scenario:** start a thread as a parent, answer as the teacher, trigger a notification, show the outbox retry on a simulated failure, then restore the database from backup.

## Milestones

| Milestone | Phase | Features | Target date | Gate |
|---|---|---|---|---|
| M0 — Foundation ready | 0 | F-001 | TBD | Clean clone runs both apps; CI green |
| M1 — Identity complete | 0 | F-002 | TBD | Register, login, refresh, logout, RTL dashboard, axe smoke |
| M2 — Structure in place | 1 | F-003 | TBD | Relationship-scoped authorization proven by tests |
| M3 — Weekly view usable | 2 | F-004, F-005 | TBD | Timetable and due dates correct at boundaries |
| M4 — School feed and progress | 3 | F-006, F-007 | TBD | Idempotent read state; audited grades; correct GPA |
| M5 — Communication and operations | 4 | F-008, F-009 | TBD | Participant-only threads; outbox retries observable |
| M6 — Production ready | 4 | F-010 | TBD | Restore drill, security review, runbook exercised |

## Sequencing rules

- A phase starts only when the previous phase's exit criteria are met, or when the missing item is tracked as an explicitly approved exception.
- F-008 stays `Deferred` until Phases 0–3 are stable; it is the first feature to cut if the schedule tightens.
- Any new requirement enters through `Task-List.md` and its own SPEC/PLAN; the permission matrix in `docs/SRS.md` §3.2 and the module boundaries in `docs/ARCHITECTURE.md` §5 are re-checked at the start of every phase.
