# Task List — «مدرسه من» / My School

This file is the project-wide intake and delivery control. **Every feature must be registered here before implementation.** A task is not Ready until its `SPEC.md` and `PLAN.md` exist and are reviewed. The backlog is ordered so that each feature builds on a stable foundation.

## Status definitions

- `Proposed` — captured, not yet specified.
- `Specifying` — SPEC/PLAN are being prepared.
- `Review` — awaiting product/architecture approval.
- `Ready` — approved and eligible for implementation.
- `In Progress` — implementation underway using TDD.
- `Blocked` — waiting on a dependency or decision.
- `In Review` — implementation complete, awaiting review/verification.
- `Done` — Definition of Done satisfied.
- `Deferred` — intentionally postponed with rationale.

## Priority definitions

- `P0` — release blocker, security, or core data integrity.
- `P1` — required for the first usable release.
- `P2` — valuable, can follow the initial release.
- `P3` — optional enhancement.

## Feature intake checklist

For every new feature:

- [ ] Assign a unique ID (`F-###`).
- [ ] Add the row below with priority, dependencies, status, and doc links.
- [ ] Create `docs/features/F-###-short-name/SPEC.md` from `docs/templates/FEATURE-SPEC.template.md`.
- [ ] Create `docs/features/F-###-short-name/PLAN.md` from `docs/templates/FEATURE-PLAN.template.md`.
- [ ] Define the parent / student / teacher journey as applicable.
- [ ] Add testable acceptance criteria and edge cases.
- [ ] Identify data, API, authorization, privacy, and operational impact.
- [ ] Create the required ADR(s), or document why none is needed.
- [ ] Review and approve before implementation.
- [ ] Implement Red → Green → Refactor, logging each cycle in `PLAN.md`.
- [ ] Update this list and the feature `PLAN.md` at completion.

## Backlog

| ID | Feature / Workstream | Priority | Status | Dependencies | Specification | Plan | Evidence |
|---|---|---:|---|---|---|---|---|
| F-001 | Repository foundation: monorepo layout, tooling, configuration, CI, health check | P0 | In Review | — | `docs/features/F-001-foundation/SPEC.md` | `docs/features/F-001-foundation/PLAN.md` | commit `6a46779`; health smoke OK |
| F-002 | Identity: registration, login, sessions, roles, teacher invite code | P0 | In Review | F-001 | `docs/features/F-002-identity/SPEC.md` | `docs/features/F-002-identity/PLAN.md` | commits `983356a`, `197380d`, `fcbadd9`; 29 API + 20 web tests |
| F-003 | School structure: classes, enrolments, parent–child links, teacher assignments | P0 | Proposed | F-002 | `docs/features/F-003-school-structure/SPEC.md` | `docs/features/F-003-school-structure/PLAN.md` | — |
| F-004 | Weekly timetable per class and student | P1 | Proposed | F-003 | `docs/features/F-004-timetable/SPEC.md` | `docs/features/F-004-timetable/PLAN.md` | — |
| F-005 | Assignments: create, publish, due dates, submission state, reminders | P1 | Proposed | F-003, F-004 | `docs/features/F-005-assignments/SPEC.md` | `docs/features/F-005-assignments/PLAN.md` | — |
| F-006 | Announcements: targeting, publish, read/unread state | P1 | Proposed | F-003 | `docs/features/F-006-announcements/SPEC.md` | `docs/features/F-006-announcements/PLAN.md` | — |
| F-007 | Grades: recording, publishing, GPA, progress chart | P1 | Proposed | F-003 | `docs/features/F-007-grades/SPEC.md` | `docs/features/F-007-grades/PLAN.md` | — |
| F-008 | Parent–teacher messaging (simple threads) | P2 | Deferred | F-003, F-006 | `docs/features/F-008-messaging/SPEC.md` | `docs/features/F-008-messaging/PLAN.md` | — |
| F-009 | Notifications: outbox, email/SMS adapters, reminder scheduler | P2 | Proposed | F-005, F-006 | `docs/features/F-009-notifications/SPEC.md` | `docs/features/F-009-notifications/PLAN.md` | — |
| F-010 | Production readiness: backups, observability, security review, runbook | P2 | Proposed | F-001–F-007 | `docs/features/F-010-production-readiness/SPEC.md` | `docs/features/F-010-production-readiness/PLAN.md` | — |

## Current sprint

Sprint 1 delivers **F-001** (foundation) and **F-002** (identity: registration + login pages).

- [x] F-001 is `Done` when the repo runs locally with one command and CI is green. — implementation complete, CI verification pending first push.
- [x] F-002 is `Done` when a parent and a student can register, log in, reach the dashboard, and log out — with tests, ADRs, and docs in place. — implemented; 29 API tests + 20 web tests pass; awaiting CI on the pushed repository.

## Change log

| Date | Change |
|---|---|
| 2026-11-19 | Backlog rewritten for «مدرسه من» (school domain) from the course starter; F-001 started, F-002 specified. |
