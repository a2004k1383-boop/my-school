# ADR-0004: Academic time model

- **Status:** Accepted
- **Date:** 2026-11-19
- **Decision owners:** Project maintainer

## Context

Assignments have due dates, the timetable is weekly, and announcements are dated. Iranian school weeks run Saturday→Friday, the school's timezone is `Asia/Tehran`, and the product must display times correctly even if a family moves abroad or the server runs in UTC. Iran does not currently observe daylight saving time, but that is a political decision, not a property of the software.

## Decision

- Persist all instants in **UTC** (`TIMESTAMP` with timezone-free storage, values converted at the boundary).
- Store the school timezone once in configuration (`SCHOOL_TIMEZONE=Asia/Tehran`) and use it for every conversion and every calendar rule.
- The academic week is **Saturday 00:00 → Friday 23:59:59.999** in the school timezone.
- A due date is stored as an instant computed from a **local date at end of day** in the school timezone; the "until end of day" rule is explicit in each feature SPEC.
- All timezone logic lives in `app/core/time.py`; no other module calls `zoneinfo` directly.
- Never persist naive local times; never assume the server timezone.

## Alternatives considered

| Option | Pros | Cons | Why rejected |
|---|---|---|---|
| Store local naive datetimes | Trivial display | Ambiguous across zones; breaks if school zone changes | Data corruption risk |
| Store UTC and let each client localize to its own zone | Simple server | A family abroad would see a different due day than the school | Wrong domain semantics |
| Store only dates for due dates | Simple for "end of day" | Loses the moment of publication and ordering | Insufficient for audit/reminders |

## Consequences

**Positive:** one unambiguous representation; correct week boundaries; reminders can be scheduled precisely.

**Negative:** every date input must be interpreted with the school timezone; tests must pin the timezone explicitly.

**Follow-ups:** add DST-gap tests using a school in `Europe/Berlin` as a fixture, to prove the code does not hard-code Iran's rules.

## References

- [AGENTS.md §7](../../AGENTS.md)
- [SRS.md §6](../SRS.md)
