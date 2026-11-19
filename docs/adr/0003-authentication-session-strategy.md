# ADR-0003: Authentication session strategy

- **Status:** Accepted
- **Date:** 2026-11-19
- **Decision owners:** Project maintainer

## Context

The SPA needs a session that survives page reloads without exposing long-lived credentials to JavaScript. The product handles minors' data, so XSS impact must be bounded. The course requires JWT-based authentication to be demonstrated, and the backend must stay stateless for access checks.

## Decision

**Access token:** JWT (HS256), 15 minutes, claims `sub`, `role`, `type=access`, `jti`, `iat`, `exp`. Returned in the JSON body and held **in memory** in the Pinia store. It is never written to `localStorage` or `sessionStorage`.

**Refresh token:** opaque 256-bit random value, returned in an `HttpOnly`, `SameSite=Lax`, `Secure` (production only) cookie scoped to `Path=/api/v1/auth`, with `Max-Age` 14 days (30 with «مرا به خاطر بسپار»). Only its SHA-256 hash is stored in `refresh_tokens`, with `family_id`, `expires_at`, `revoked_at`, and `replaced_by`.

**Rotation and reuse detection:** every refresh issues a new token and marks the old one replaced. Presenting an already-replaced token revokes the whole family and fails with `401 refresh_reused`.

**CSRF:** state-changing cookie endpoints require `X-Requested-With: XMLHttpRequest`. Combined with `SameSite=Lax`, this blocks simple cross-site form posts; a custom header forces a CORS preflight for cross-origin calls.

**Logout:** revokes the family server-side and clears the cookie.

## Alternatives considered

| Option | Pros | Cons | Why rejected |
|---|---|---|---|
| Access + refresh both in localStorage | Simple client code | Any XSS steals a 14-day credential | Unacceptable for minors' data |
| Server-side sessions (session id cookie) | Easy revocation | Stateful; needs shared store; JWT requirement of the course | Course requires JWT |
| Both tokens in HttpOnly cookies | No token in JS | Needs CSRF token for every call; harder API clients | Adds ceremony without clear gain for this scope |
| Long-lived access token only | Fewest moving parts | No revocation, long theft window | Violates security baseline |

## Consequences

**Positive:** XSS cannot read the refresh token; access token theft is limited to 15 minutes; reuse of a stolen refresh token is detectable and kills the family.

**Negative:** the client must implement single-flight refresh; a race between two tabs can log the user out (acceptable, documented); refresh cookie requires correct `Path` and CORS credentials configuration.

**Residual risk:** if an attacker can run script in the origin, they can still call refresh and use the session while the page is open. Mitigated by CSP and input escaping, which are tracked in F-010.

## References

- [SPEC F-002 §9](../features/F-002-identity/SPEC.md#9-security-and-privacy)
- [ADR-0005](0005-role-model-and-teacher-onboarding.md)
