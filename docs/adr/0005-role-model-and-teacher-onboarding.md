# ADR-0005: Single-role accounts and teacher onboarding by invite code

- **Status:** Accepted
- **Date:** 2026-11-19
- **Decision owners:** Project maintainer

## Context

The platform serves parents, students, and teachers. Three questions had to be settled before authentication was built:

1. Can one account hold more than one role (e.g., a teacher who is also a parent)?
2. Who is allowed to create a teacher account?
3. How is a teacher's identity verified before they can see classes?

For a first release, the school office hands out one account per person and knows who teaches what. Self-service teacher signup would let anyone claim to be a teacher and see children's data.

## Decision

- A user has **exactly one primary role**: `parent`, `student`, or `teacher`, stored as an enum and immutable after registration.
- Parents and students self-register.
- Teacher registration requires a valid **invite code** supplied by the school, read from `TEACHER_INVITE_CODE`, compared in constant time, and never logged.
- A successful teacher registration writes an audit row (`action = "teacher.registered"`, metadata contains the invite code **identifier**, never the secret).
- Multi-role accounts and invite-code lifecycle management (single-use codes, expiry, per-teacher codes) are future work requiring a new ADR.

## Alternatives considered

| Option | Pros | Cons | Why rejected |
|---|---|---|---|
| Open teacher signup | Zero admin work | Anyone can see class data; unacceptable for minors | Security failure |
| Admin approves every teacher | Strong control | Needs an admin console that does not exist yet | Scope creep for F-002 |
| Email-domain restriction (e.g. `@school.ir`) | Simple rule | Easy to spoof with a personal address; schools use mixed domains | Weak guarantee |
| Multi-role from day one | Flexible | Complicates authorization, UI, and tests without a proven need | Premature |

## Consequences

**Positive:** the authorization model stays simple and testable; a teacher cannot self-onboard without the school's secret.

**Negative:** a teacher who is also a parent needs two accounts (documented limitation); the shared invite code cannot be revoked per teacher.

**Follow-ups:** F-003 links teachers to classes, which is where real verification of "who teaches what" happens; F-010 tracks per-teacher invite codes.

## References

- [SPEC F-002 §5](../features/F-002-identity/SPEC.md#5-functional-requirements)
- [ADR-0003](0003-authentication-session-strategy.md)
