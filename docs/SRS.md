# Software Requirements Specification — «مدرسه من» / My School

| Field | Value |
|---|---|
| Product | «مدرسه من» / My School — school–parent–student communication platform |
| Document | Software Requirements Specification (SRS) |
| Version | 2.0 — school-product baseline (supersedes the course-starter scheduling baseline) |
| Date | 2026-11-19 |
| Status | Baseline. Approved feature `SPEC.md` files and accepted ADRs take precedence over this document (`AGENTS.md` §2). |
| Companion documents | `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `Task-List.md`, `docs/adr/`, `docs/features/` |

## 1. Purpose and scope

### 1.1 Purpose

This document states the functional and non-functional requirements for «مدرسه من», a platform used by one school to publish its weekly timetable, assignments, announcements, and grades to parents and students, and by teachers to author that content.

The SRS is the requirements baseline for feature specifications, test plans, and release gates. It states *what* the product must do; it does not approve implementation. A feature may only be built after its own `SPEC.md` and `PLAN.md` exist (`AGENTS.md` §3).

### 1.2 Product scope

The product answers four weekly questions for every family:

1. **What does the week look like?** — the class timetable (برنامه هفتگی).
2. **What must be done, and by when?** — assignments (تکلیف) with due dates and completion state.
3. **What did the school say?** — announcements (اطلاعیه) with per-user read/unread state.
4. **How is my child progressing?** — grades (نمره), GPA (معدل), and a progress chart.

A later phase adds simple parent–teacher messaging (پیام) and outbox-driven notifications.

The product is an information and communication surface. It is **not** a school-management system (no admissions, finance, HR, attendance payroll, or exam authoring) and **not** a social network (no public profiles, feeds, or messages between families).

### 1.3 Out of scope for this release

- Multiple schools, multiple campuses, or tenant isolation beyond the single-school deployment.
- Native mobile applications; the product is a responsive browser SPA.
- Real-time chat, presence, push notifications, or websockets.
- File attachments, assignment file submission, or file-based grading; only completion state is tracked.
- Any financial, billing, or fee-related feature.
- Administrator console, self-service school-structure management, and account-deletion UI (see §11).
- Email verification, password reset, two-factor authentication, and SSO (design must not block them).

## 2. Definitions and glossary

| Persian term | English term | Definition |
|---|---|---|
| مدرسه من | My School | The product: one school's communication platform. |
| والد | Parent | Guardian account. Sees only the children explicitly linked to it. |
| دانش‌آموز | Student | Pupil account. Sees only its own records. |
| معلم | Teacher | Staff account. Publishes content and records grades for the classes it teaches. |
| کلاس | Class | A teaching group within one academic year (grade level plus section). |
| ثبت‌نام | Enrolment | The link between a student and one class in one academic year. |
| پیوند والد–فرزند | Parent link | The relationship between a parent account and one child, with a relationship type. |
| سال تحصیلی | Academic year | The school year; exactly one is active at a time and it bounds classes and grades. |
| برنامه هفتگی | Timetable | The weekly grid of subjects, teachers, and periods for a class. |
| زنگ | Period | A numbered teaching period on a day, with bell start and end times. |
| تکلیف | Assignment | A teacher-authored task for a class and subject with a due date and completion state. |
| اطلاعیه | Announcement | A teacher-authored notice for a class, with per-user read state. |
| نمره | Grade | A recorded assessment result with a value, a scale, and a weight. |
| معدل | GPA | The weighted average of a student's grades for a period, computed from stored facts. |
| کد دعوت معلم | Teacher invite code | The shared secret (`TEACHER_INVITE_CODE`) required to create a teacher account. |
| هفته تحصیلی | Academic week | Saturday 00:00 through Friday 23:59:59.999 in the school timezone. |
| ADR / SPEC / PLAN | — | Architecture Decision Record; feature specification; feature implementation plan. |

## 3. Actors and permissions

### 3.1 Actors

- **Anonymous visitor** — unauthenticated browser. May only reach the login and registration pages and submit credentials.
- **Parent (والد)** — self-registers. Follows one or more linked children.
- **Student (دانش‌آموز)** — self-registers. Follows its own class and records.
- **Teacher (معلم)** — registers only with a valid teacher invite code. Authors content and records grades for assigned classes.
- **School office (external)** — human process outside the system. Supplies class lists and links, which are loaded by audited maintainer scripts (F-003); there is no administrator role in this release (§11).

Every account has exactly one immutable primary role (ADR-0005). Multi-role accounts are not supported.

### 3.2 Permission matrix

| Capability | Anonymous | Parent | Student | Teacher |
|---|---|---|---|---|
| Register | Parent and student self-registration; teacher with invite code | — | — | — |
| Log in and log out | — | Own account only | Own account only | Own account only |
| Read own profile (`/auth/me`) | No | Yes | Yes | Yes |
| Read timetable | No | Linked children's classes | Own class | Classes taught |
| Read assignments | No | Linked children's published assignments | Own published assignments | Classes and subjects taught |
| Create and publish assignments | No | No | No | Classes and subjects taught |
| Mark assignment complete | No | No (read-only view) | Own assignments | No |
| Read announcements | No | Classes of linked children | Own class | Classes taught |
| Publish announcements | No | No | No | Classes taught |
| Mark announcement read | No | Own read state | Own read state | Own read state |
| Read grades | No | Linked children, published only | Own, published only | Recorded by that teacher, drafts included |
| Record and change grades | No | No | No | Classes and subjects taught; changes audited |
| Read GPA and progress chart | No | Linked children | Own | Own subject aggregates, never other teachers' data |
| Send messages (F-008, deferred) | No | Threads with teachers of linked children | No | Threads with parents of students taught |
| Manage classes, enrolments, and links | No | No | No | No — maintainer scripts only |

The backend enforces every row of this matrix on every request. The SPA hides controls for usability only; hidden controls are never the authorization boundary (`AGENTS.md` §8, §10).

## 4. Functional requirements

Requirements use the identifier form `FR-<MODULE>-###` and are written as testable *shall* statements. The phase column refers to `docs/ROADMAP.md`.

### 4.1 Identity and access — F-002 (Phase 0)

| ID | Requirement | Phase |
|---|---|---|
| FR-IDN-001 | The system **shall** register a user from full name, email, password, password confirmation, one role (`parent`, `student`, or `teacher`), and explicit terms acceptance. | 0 |
| FR-IDN-002 | The system **shall** trim and lowercase emails and enforce case-insensitive uniqueness, rejecting duplicates with `409 email_already_registered`. | 0 |
| FR-IDN-003 | The system **shall** store passwords only as Argon2id hashes and never return or log password material. | 0 |
| FR-IDN-004 | The system **shall** require a valid `TEACHER_INVITE_CODE` for teacher registration and reject a missing or wrong code with `403 invitation_required`, creating no user. | 0 |
| FR-IDN-005 | The system **shall** authenticate valid credentials and return a 15-minute access token in the response body plus a rotating refresh token in an `HttpOnly`, `SameSite=Lax` cookie scoped to `Path=/api/v1/auth`. | 0 |
| FR-IDN-006 | The system **shall** return an identical `401 invalid_credentials` response, with equal status, code, and message, for an unknown email and for a wrong password. | 0 |
| FR-IDN-007 | The system **shall** reject disabled accounts with `403 account_disabled` and reject their existing refresh tokens on next use. | 0 |
| FR-IDN-008 | The system **shall** rate-limit login and registration and return `429` with a `Retry-After` header when a limit is exceeded. | 0 |
| FR-IDN-009 | The system **shall** rotate the refresh token on every refresh and revoke the whole token family when a rotated token is presented again. | 0 |
| FR-IDN-010 | The system **shall** revoke the refresh token family on logout and clear the refresh cookie. | 0 |
| FR-IDN-011 | The system **shall** expose the authenticated user's own profile at `GET /api/v1/auth/me` and no other user's profile. | 0 |
| FR-IDN-012 | The system **shall** store exactly one role per user and treat it as immutable after registration. | 0 |
| FR-IDN-013 | The system **shall** write an audit record for every teacher registration containing actor, time, and invite-code identifier, never the code itself. | 0 |
| FR-IDN-014 | The SPA **shall** keep the access token in memory only and perform a single-flight refresh on the first `401` before retrying the original request. | 0 |

### 4.2 School structure and relationships — F-003 (Phase 1)

| ID | Requirement | Phase |
|---|---|---|
| FR-PPL-001 | The system **shall** represent a class as a named teaching group within one academic year and one grade level, with at most one homeroom teacher. | 1 |
| FR-PPL-002 | The system **shall** enrol a student in exactly one class per academic year and reject a second concurrent enrolment. | 1 |
| FR-PPL-003 | The system **shall** link a parent account to a child with a recorded relationship type and shall allow a parent to have several linked children. | 1 |
| FR-PPL-004 | The system **shall** record which teacher teaches which subject to which class, and treat that pair as the teacher's authoring scope. | 1 |
| FR-PPL-005 | The system **shall** allow exactly one active academic year at a time, with start and end dates expressed in the school timezone. | 1 |
| FR-PPL-006 | The system **shall** authorize every request for child-scoped data from stored relationships and **shall not** trust a client-supplied student, class, or parent identifier. | 1 |
| FR-PPL-007 | The system **shall** limit list endpoints for classes, enrolments, and links to the caller's own scope and return no partial data for out-of-scope identifiers. | 1 |
| FR-PPL-008 | The system **shall** provision classes, enrolments, links, and teaching assignments through audited maintainer scripts until an administrator capability exists. | 1 |

### 4.3 Weekly timetable — F-004 (Phase 2)

| ID | Requirement | Phase |
|---|---|---|
| FR-TBL-001 | The system **shall** store a timetable entry as one class, one weekday (Saturday through Friday), one period, one subject, and one teacher. | 2 |
| FR-TBL-002 | The system **shall** define, per academic year, the bell start and end time of each period, unique per weekday and period number. | 2 |
| FR-TBL-003 | The system **shall** reject a second timetable entry for the same class, weekday, and period with `409 timetable_conflict`. | 2 |
| FR-TBL-004 | The system **shall** show a student its own class timetable, a parent the timetable of each linked child, and a teacher only the classes it teaches. | 2 |
| FR-TBL-005 | The system **shall** present the current academic week, Saturday first, computed in the school timezone, and allow reading the previous and next week. | 2 |
| FR-TBL-006 | The system **shall** expose only subject, teacher display name, period, and room for a timetable entry, and no other student's data. | 2 |
| FR-TBL-007 | The system **shall** record the actor and timestamp of every timetable change. | 2 |

### 4.4 Assignments — F-005 (Phase 2)

| ID | Requirement | Phase |
|---|---|---|
| FR-ASG-001 | The system **shall** let a teacher create an assignment for a taught class and subject with a title, description, due date, and publish state. | 2 |
| FR-ASG-002 | The system **shall** store the due date as a UTC instant derived from the end of the chosen local day in the school timezone, and treat the deadline as inclusive of that instant. | 2 |
| FR-ASG-003 | The system **shall** keep drafts visible only to their author and expose published assignments to enrolled students and their linked parents. | 2 |
| FR-ASG-004 | The system **shall** present published assignments ordered by due date, paginated, with the state upcoming, due today, or overdue computed server-side in the school timezone. | 2 |
| FR-ASG-005 | The system **shall** let the authoring teacher edit or delete an assignment for a taught class, recording actor and timestamp for each change. | 2 |
| FR-ASG-006 | The system **shall** let a student mark a published assignment complete or incomplete, idempotently, and expose that state read-only to linked parents. | 2 |
| FR-ASG-007 | The system **shall** show a parent each linked child's assignments and completion state separately, without merging two children's records. | 2 |
| FR-ASG-008 | The system **shall** enqueue assignment reminders in the same transaction as the assignment change and deliver them only after commit (F-009). | 2 |
| FR-ASG-009 | The system **shall** reject an assignment whose due date is before its creation instant, or whose class is outside the teacher's scope. | 2 |

### 4.5 Announcements — F-006 (Phase 3)

| ID | Requirement | Phase |
|---|---|---|
| FR-ANN-001 | The system **shall** let a teacher publish an announcement to a taught class; whole-school targeting is deferred with the administrator role (§11). | 3 |
| FR-ANN-002 | The system **shall** keep drafts visible only to their author and expose published announcements to the target class. | 3 |
| FR-ANN-003 | The system **shall** record read state per user and per announcement and treat marking an announcement read twice as success without changing stored state. | 3 |
| FR-ANN-004 | The system **shall** expose an unread count per user, counting an announcement once even when the user is linked to several children in the same class. | 3 |
| FR-ANN-005 | The system **shall** show a parent the announcements of each linked child's class, deduplicated, with the child or class that caused the item to appear. | 3 |
| FR-ANN-006 | The system **shall** hide a deleted or archived announcement from all users while retaining its audit record. | 3 |
| FR-ANN-007 | The system **shall** list announcements newest first, paginated, with author, target, and publication time in the school timezone. | 3 |

### 4.6 Grades, GPA, and progress — F-007 (Phase 3)

| ID | Requirement | Phase |
|---|---|---|
| FR-GRD-001 | The system **shall** let a teacher record a grade for one student in a taught class and subject, with title, numeric value, scale, weight, and assessment date. | 3 |
| FR-GRD-002 | The system **shall** accept a value only within `0 ≤ value ≤ scale`, with `scale > 0` and `weight > 0`, and reject anything else with `422`. | 3 |
| FR-GRD-003 | The system **shall** keep draft grades visible only to the recording teacher and expose published grades to the student and linked parents. | 3 |
| FR-GRD-004 | The system **shall** audit every grade creation, change, and deletion with actor, timestamp, previous value, new value, and an optional reason. | 3 |
| FR-GRD-005 | The system **shall** compute averages and GPA from stored values and weights, never from rounded display values. | 3 |
| FR-GRD-006 | The system **shall** render a progress chart per subject across the active academic year with term boundaries taken from the school calendar. | 3 |
| FR-GRD-007 | The system **shall** return only the caller's permitted grades: a student its own, a parent those of linked children, a teacher those it recorded. | 3 |

### 4.7 Parent–teacher messaging — F-008 (Phase 4, deferred)

| ID | Requirement | Phase |
|---|---|---|
| FR-MSG-001 | The system **shall** let a parent start a message thread with a teacher of a linked child's class. | 4 |
| FR-MSG-002 | The system **shall** let that teacher reply in the thread, and **shall not** allow messaging between parents, between students, or across unrelated classes. | 4 |
| FR-MSG-003 | The system **shall** expose a thread only to its participants and **shall not** allow enumerating or opening other threads. | 4 |
| FR-MSG-004 | The system **shall** store messages immutably after sending and apply the retention rules of §5. | 4 |
| FR-MSG-005 | The system **shall** reject attachments and messages exceeding the configured length limit. | 4 |

## 5. Non-functional requirements

**Security and privacy (minors' data is sensitive)**

- **NFR-SEC-001** Every protected operation **shall** be authorized server-side from the stored role and relationships, deny by default, before any data is read.
- **NFR-SEC-002** Passwords **shall** be hashed with Argon2id at library defaults (memory cost ≥ 64 MiB) and never logged, returned, or included in errors.
- **NFR-SEC-003** The session model **shall** follow ADR-0003: short-lived access JWT held in memory, rotating refresh token in an `HttpOnly`, `SameSite=Lax` cookie that is `Secure` in production, revocation on reuse.
- **NFR-SEC-004** Cookie-authenticated state-changing calls **shall** require `X-Requested-With: XMLHttpRequest` and pass the CORS allowlist.
- **NFR-SEC-005** Login **shall** be limited to 5 attempts per minute per IP plus email and 20 per minute per IP; registration to 3 per minute per IP.
- **NFR-SEC-006** The system **shall** collect no national identifier, home address, phone number, or birth date in Phases 0–1 unless an approved SPEC requires it.
- **NFR-SEC-007** Secrets **shall** come from environment variables only; the API **shall** refuse to start without a JWT secret of at least 32 bytes.
- **NFR-PRIV-001** Logs **shall** contain request id, route, status, and latency, and **shall not** contain bodies, tokens, emails, grades, or children's names.
- **NFR-PRIV-002** Error responses **shall** reveal nothing outside the caller's scope; an unknown and a forbidden child-scoped resource **shall** return the same status and body shape.
- **NFR-PRIV-003** Retention, export, and deletion procedures **shall** be documented and reviewed before Phase 4, and account deletion **shall not** ship without legal review.

**Performance and availability (targets are provisional; reference environment 2 vCPU, 2 GB)**

- **NFR-PERF-001** Ordinary API reads **shall** stay at p95 ≤ 400 ms and writes at p95 ≤ 800 ms with 30 concurrent authenticated users, excluding email and SMS delivery.
- **NFR-PERF-002** The parent dashboard (timetable, 20 assignments, unread count) **shall** render at p95 ≤ 1 s warm.
- **NFR-PERF-003** Auth and dashboard pages **shall** reach p75 LCP ≤ 2.5 s on a throttled 4G mid-range mobile profile.
- **NFR-AVL-001** Production **shall** provide 99.5% monthly availability during the academic term, excluding announced maintenance windows.
- **NFR-AVL-002** A committed write **shall** survive notification failure; notification work runs after commit through the outbox (F-009).

**Accessibility, localization, audit, operations**

- **NFR-ACC-001** All pages **shall** meet WCAG 2.1 AA: keyboard operable, visible focus, semantic headings, programmatic labels, accessible error messages, and correct reading order in RTL.
- **NFR-ACC-002** Automation **shall** run an axe smoke check on the auth and dashboard pages, and no critical violation may remain at release.
- **NFR-ACC-003** Text contrast **shall** be at least 4.5:1, and status **shall not** be conveyed by colour alone.
- **NFR-L10N-001** Persian (`fa`) **shall** be the only UI language in this release; every user-facing string **shall** live in `apps/web/src/shared/i18n/fa.ts`.
- **NFR-L10N-002** The UI **shall** be RTL at the document level, using CSS logical properties and Vazirmatn, and **shall** isolate LTR values such as emails and invite codes.
- **NFR-L10N-003** Academic dates **shall** display in the school timezone and Persian calendar conventions, while API payloads remain UTC ISO 8601 instants.
- **NFR-AUD-001** The system **shall** append audit records for teacher registration, grade changes, account disablement, announcement deletion, and structure provisioning.
- **NFR-AUD-002** An audit record **shall** carry actor, action, target, timestamp, request id, and redacted metadata, and **shall** be readable through the operations runbook in this release.
- **NFR-AUD-003** Every authorization denial on child-scoped data **shall** be logged as a security event without payload data.
- **NFR-BAK-001** Production **shall** keep nightly managed PostgreSQL backups with 30-day retention, targeting RPO ≤ 24 hours and RTO ≤ 8 hours.
- **NFR-BAK-002** A restore drill **shall** be executed and recorded before each release tag.
- **NFR-MAINT-001** Every behavior change **shall** be test-driven, with `apps/api` coverage ≥ 80% and auth module coverage ≥ 80%, and all lint, type, test, and build gates green.
- **NFR-MAINT-002** Every schema change **shall** ship as a reviewed Alembic migration with a tested downgrade path.
- **NFR-OBS-001** The API **shall** emit structured logs with request id and latency, and `GET /api/v1/health` **shall** report status, version, and database connectivity.
- **NFR-OBS-002** Latency, error rate, authentication failures, and notification failures **shall** be measurable from Phase 4 onward.

## 6. Academic time and calendar rules

- **TR-001** All persisted instants **shall** be UTC; API timestamps **shall** be ISO 8601 with `Z`.
- **TR-002** The school timezone **shall** come from one configuration value (`SCHOOL_TIMEZONE=Asia/Tehran`) and **shall** govern every calendar rule and display.
- **TR-003** The academic week **shall** run Saturday 00:00 to Friday 23:59:59.999 in the school timezone.
- **TR-004** A due date described as "until the end of the day" **shall** be the instant 23:59:59.999 local, converted to UTC, and inclusive.
- **TR-005** Timezone conversion **shall** live only in `apps/api/app/core/time.py`; no other module **shall** call `zoneinfo` directly.
- **TR-006** The code **shall not** hard-code the absence of daylight saving time; tests **shall** include a DST-observing zone fixture to prove correct gap and overlap handling.
- **TR-007** A response whose meaning depends on a local calendar **shall** include the school timezone identifier alongside the UTC instant.
- **TR-008** A local wall-clock time **shall never** be treated as uniquely identifying an instant without an explicit timezone.

## 7. External interfaces

### 7.1 REST API

- **IF-API-001** The API **shall** expose JSON over HTTPS under `/api/v1`, with an OpenAPI 3.1 document available to developers and CI.
- **IF-API-002** Errors **shall** use `application/problem+json` with `type`, `title`, `status`, `code`, `detail`, and optional `errors[]`; the request id is returned in the `X-Request-ID` header.
- **IF-API-003** Collection endpoints **shall** paginate and **shall** reject unknown query parameters rather than silently ignoring them.

### 7.2 Browser client

- **IF-UI-001** The client **shall** be a responsive SPA supporting the last two versions of Chrome, Firefox, Edge, and Safari at widths from 360 px upward, in RTL.
- **IF-UI-002** Every screen that fetches data **shall** provide loading, empty, success, error, and retry states.

### 7.3 Email and SMS adapters (later phases)

- **IF-NOT-001** Email and SMS delivery **shall** sit behind adapter interfaces and be invoked only after the database transaction commits (F-009).
- **IF-NOT-002** Messages **shall** be templated in Persian and **shall** contain no grades or other sensitive values beyond what the recipient is authorized to see in the product.
- **IF-NOT-003** SMS **shall** require a configured vendor and explicit opt-in, and **shall** be rate-limited per recipient.

### 7.4 Interfaces explicitly excluded

No calendar synchronization, third-party analytics, advertising, or public API for external consumers in this release.

## 8. Constraints and assumptions

### 8.1 Constraints

- **C-001** Single school, single campus, single active academic year per deployment.
- **C-002** Iranian academic calendar: `Asia/Tehran`, Saturday-start week, Persian calendar display.
- **C-003** Teacher onboarding uses a shared invite code from configuration (ADR-0005); per-teacher codes are future work.
- **C-004** No administrator role in this release; structure data is loaded by maintainer scripts (FR-PPL-008).
- **C-005** No payments, fees, or financial records of any kind.
- **C-006** SQLite (`aiosqlite`) for local development and fast tests; PostgreSQL 16 is authoritative for production and CI migration tests.
- **C-007** Python 3.12+, Node 20+, `uv` for the backend, `pnpm` for the frontend.
- **C-008** Sizing assumption: up to about 1,000 accounts, 40 classes, 1,200 students, 30 concurrent users at peak.
- **C-009** Minors' data is treated as sensitive: minimum collection, no logging, and no exposure in URLs or error text.

### 8.2 Assumptions

- **A-001** The school office maintains class lists, enrolments, parent links, and teaching assignments outside the system and delivers them for import.
- **A-002** Every family has a working email address; SMS is an optional later channel.
- **A-003** A teacher may teach several classes and subjects; a class has at most one homeroom teacher.
- **A-004** Grades use a per-grade numeric scale (the Iranian 0–20 scale by default) with weights, so GPA is a weighted average of stored facts.
- **A-005** No realtime requirement exists; screens refresh on navigation and on explicit retry.

## 9. Acceptance and release criteria

| Phase | Features | Release criteria (all must hold) |
|---|---|---|
| 0 | F-001, F-002 | Parent and student register and log in; teacher registers only with a valid invite code; refresh, reuse detection, and logout pass; dashboard renders in RTL; axe smoke passes; CI is green on SQLite tests and a PostgreSQL migration run. |
| 1 | F-003 | A parent sees only linked children, a teacher only assigned classes, a student only itself; out-of-scope identifiers return no data; authorization tests cover every child-scoped endpoint. |
| 2 | F-004, F-005 | A student sees the correct weekly grid; a teacher publishes an assignment; due dates are correct across week boundaries and timezone edges; parents see each child's assignments separately. |
| 3 | F-006, F-007 | Read/unread is idempotent and counted once per user; unpublished content never leaks; grade changes are audited; GPA matches a hand-computed weighted average; the progress chart matches stored values. |
| 4 | F-008, F-009, F-010 | Threads are participant-only; notifications survive commit and retry bounded; backups restore in a drill; security review closes all critical findings; the runbook is exercised. |

**Release gate:** every P0 feature is `Done` per `AGENTS.md` §17, no critical security or data-integrity issue is open, the restore drill has passed, and the resolved product decisions in §11 are recorded in the affected SPECs.

## 10. Traceability

| Module | Requirements | Feature | Specification | Task-List status |
|---|---|---|---|---|
| Repository foundation | Constraints in §8, gates in §5 | F-001 | `docs/features/F-001-foundation/SPEC.md` | In Progress |
| Identity and access | FR-IDN-001 … FR-IDN-014 | F-002 | `docs/features/F-002-identity/SPEC.md` | Specifying |
| School structure and relationships | FR-PPL-001 … FR-PPL-008 | F-003 | `docs/features/F-003-school-structure/SPEC.md` (to be written) | Proposed |
| Weekly timetable | FR-TBL-001 … FR-TBL-007 | F-004 | `docs/features/F-004-timetable/SPEC.md` (to be written) | Proposed |
| Assignments | FR-ASG-001 … FR-ASG-009 | F-005 | `docs/features/F-005-assignments/SPEC.md` (to be written) | Proposed |
| Announcements | FR-ANN-001 … FR-ANN-007 | F-006 | `docs/features/F-006-announcements/SPEC.md` (to be written) | Proposed |
| Grades, GPA, progress | FR-GRD-001 … FR-GRD-007 | F-007 | `docs/features/F-007-grades/SPEC.md` (to be written) | Proposed |
| Messaging | FR-MSG-001 … FR-MSG-005 | F-008 | `docs/features/F-008-messaging/SPEC.md` (to be written) | Deferred |
| Notifications | FR-ASG-008, IF-NOT-001 … IF-NOT-003 | F-009 | `docs/features/F-009-notifications/SPEC.md` (to be written) | Proposed |
| Operations and hardening | NFR-AUD, NFR-BAK, NFR-OBS, NFR-PRIV-003 | F-010 | `docs/features/F-010-production-readiness/SPEC.md` (to be written) | Proposed |

## 11. Product decisions requiring confirmation

These decisions must be resolved in the affected feature SPEC before that feature is marked `Ready`:

1. Is an administrator role introduced (and by which ADR), or do structure changes remain script-driven for the whole course deliverable?
2. How many periods per day exist, and who owns the bell times per academic year?
3. Is GPA credit-weighted per subject or a simple weighted average of grade weights across subjects?
4. May announcements target a whole grade level or the whole school in this release, or only a single class?
5. Does assignment completion need teacher verification, or is student self-report sufficient for the course deliverable?
6. Which Persian-calendar formatting library and which SMS vendor are approved (both require ADR review before use)?
