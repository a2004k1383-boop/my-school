# Starter → project rewrite map

The course starter (`agentic-scheduling-blueprint`) describes an **appointment-booking** platform. «مدرسه من» is a **school communication** platform. This file records, per starter file, what happened to it and why — required by the assignment's "copy the starter, then rewrite it" step.

| # | Starter file | What it was | Action | Target | Rationale |
|---|---|---|---|---|---|
| 1 | `AGENTS.md` | Engineering rules for a booking platform (providers, customers, slots) | Rewritten | `AGENTS.md` | Kept the structure (intake gate, TDD, DoR/DoD, agent protocol); replaced the domain with school roles, minors' privacy, academic time, and grade audit rules. |
| 2 | `Task-List.md` | F-001…F-017 backlog for bookings, availability, payments | Rewritten | `Task-List.md` | New feature set F-001…F-010 for school modules; unchanged status model and intake checklist. |
| 3 | `README.md` | Booking product marketing + `frontend/`/`backend/` layout | Rewritten | `README.md` | Describes «مدرسه من», real repository layout, quickstart, docs index. |
| 4 | `docs/SRS.md` | Booking requirements | Rewritten | `docs/SRS.md` | New actors, FR-* identifiers per school module, NFRs (WCAG 2.1 AA, RTL, minors' data), traceability to Task-List. |
| 5 | `docs/ARCHITECTURE.md` | Booking architecture | Rewritten | `docs/ARCHITECTURE.md` | Modular monolith for Vue 3 + FastAPI, module boundaries (`identity`, `people`, `timetable`, …), C4-lite diagrams. |
| 6 | `docs/ROADMAP.md` | Booking phases | Rewritten | `docs/ROADMAP.md` | Delivery phases M0–M4 mapped to the school feature backlog. |
| 7 | `docs/adr/0001-modular-monolith.md` | ADR: modular monolith | Rewritten | same path | Same decision, re-argued for this product and stack. |
| 8 | `docs/adr/0002-database-environments.md` | ADR: SQLite dev / Postgres prod | Rewritten | same path | Same decision, portability rules restated (UUID, timestamps, expression indexes). |
| 9 | `docs/adr/0003-booking-concurrency.md` | ADR: overlap prevention and locking | Replaced | `docs/adr/0003-authentication-session-strategy.md` | No booking domain. The equivalent "correctness under concurrency" decision here is refresh-token rotation and reuse detection. |
| 10 | `docs/adr/0004-timezone-model.md` | ADR: UTC + IANA timezones | Replaced | `docs/adr/0004-academic-time-model.md` | Same principle applied to the school calendar: UTC storage, `Asia/Tehran` rules, Saturday–Friday week. |
| 11 | `docs/templates/ADR.template.md` | ADR template | Kept | same path | Format is domain-neutral. |
| 12 | `docs/templates/FEATURE-SPEC.template.md` | SPEC template | Kept | same path | Domain-neutral; used for F-001 and F-002. |
| 13 | `docs/templates/FEATURE-PLAN.template.md` | PLAN template | Kept | same path | Domain-neutral; TDD log added inside the feature plan. |
| — | *(new)* | — | Added | `docs/adr/0005-role-model-and-teacher-onboarding.md` | Needed a decision for single-role accounts and invite-code teacher onboarding. |
| — | *(new)* | — | Added | `docs/features/F-001-foundation/`, `docs/features/F-002-identity/` | The starter has no implemented features; each delivered feature needs SPEC + PLAN. |
| — | *(new)* | — | Added | `apps/api`, `apps/web`, `.github/workflows/ci.yml` | The starter contains documents only; the assignment requires working login/registration. |
| — | *(new)* | — | Added | `docs/runbooks/local-development.md`, `docs/submission/` | Operational and submission artefacts. |

## Deviations from the starter

1. **No booking concepts survive.** Availability slots, providers, payments, and calendar sync were removed rather than renamed, because they do not exist in a school communication product.
2. **Frontend/backend folders** became `apps/api` and `apps/web` (pnpm workspace + uv project) so both applications live in one repository with one command set.
3. **ADR-0003 and ADR-0004 were replaced, not edited in place**, because the decisions they recorded no longer apply; the new ADRs keep the numbering to preserve the decision sequence.
4. **The starter had no code**, so the implementation is new; the starter's documents were treated as the specification skeleton, not as code to port.
