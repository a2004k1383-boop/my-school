# Feature Specification — F-002 Identity: registration, login, and sessions

- **Status:** Approved
- **Owner:** Project maintainer (student)
- **Related backlog item:** `F-002` in `Task-List.md`
- **Related ADRs:** [ADR-0003](../adr/0003-authentication-session-strategy.md), [ADR-0005](../adr/0005-role-model-and-teacher-onboarding.md)

## 1. Problem and objective

Parents and students need a trustworthy way to enter «مدرسه من». The school cannot send paper credentials to every family, and teachers must not be able to create accounts freely. We need self-service signup for families, controlled onboarding for teachers, and a session that survives a page refresh without storing long-lived secrets in the browser.

**Objective:** a parent or student can create an account and log in in under two minutes, sees a role-appropriate dashboard, and stays logged in across refreshes; a teacher can only register with a valid invite code; nobody can enumerate registered emails.

## 2. Actors and permissions

| Actor | Can | Cannot |
|---|---|---|
| Anonymous visitor | Open `/login`, `/register`, submit credentials | See any school data, dashboard, or user list |
| Parent | Register, log in, log out, view own profile, reach parent dashboard | Register as teacher without invite code, see other families |
| Student | Register, log in, log out, view own profile, reach student dashboard | Register as teacher without invite code, see other students |
| Teacher | Register **with invite code**, log in, reach teacher dashboard | Self-register without a valid code, access admin functions |

Role is chosen at registration and is **immutable** afterwards (changing role is a future admin feature, out of scope).

## 3. User journeys

**J1 — Parent registers.** `/register` → fills name, email, password, confirm, selects «والد», accepts terms → submit → account created → redirected to `/login?registered=1` with success message → logs in → `/dashboard` shows parent greeting.

**J2 — Teacher registers with invite.** Selects «معلم» → an extra «کد دعوت معلم» field appears and becomes required → wrong code shows a field error and creates nothing → correct code creates a teacher account.

**J3 — Login.** Email + password (+ optional «مرا به خاطر بسپار») → success → access token in memory, refresh cookie set → redirect to the originally requested page (`?redirect=`) or `/dashboard`.

**J4 — Session restore.** Reload page → app calls `POST /auth/refresh` silently → if the cookie is valid, gets a new access token and `/auth/me`, then renders the dashboard without a flash of the login page.

**J5 — Logout.** Dashboard → «خروج» → server revokes the refresh token family and clears the cookie → `/login`.

**Failure paths.** Wrong password and unknown email produce the **same** message («ایمیل یا رمز عبور نادرست است.»). Too many attempts → 429 with a Persian message. Disabled account → 403. Expired refresh → silent logout to `/login`.

## 4. Scope

### In scope

- Registration for `parent` and `student` (open) and `teacher` (invite code).
- Email/password login with rate limiting.
- Access token (JWT, 15 min, memory only) and rotating refresh token (HttpOnly cookie, 14 days; 30 days with «مرا به خاطر بسپار»).
- Logout, session restore, `/auth/me`.
- Role-based landing on a placeholder dashboard.
- Persian/RTL auth pages with accessible validation.

### Out of scope

- Email verification, password reset, 2FA, SSO (future features; the schema and services must not make them harder).
- Linking parents to children and teachers to classes (F-003).
- Admin console, user management, account deletion UI.
- Phone-based login and SMS delivery.

## 5. Functional requirements

| ID | Requirement |
|---|---|
| FR-01 | The system **shall** allow registration with full name, email, password, password confirmation, role, and terms acceptance. |
| FR-02 | The system **shall** normalize email (trim + lowercase) and enforce case-insensitive uniqueness. |
| FR-03 | The system **shall** store passwords only as Argon2id hashes. |
| FR-04 | The system **shall** require `TEACHER_INVITE_CODE` for `teacher` registration and reject invalid or missing codes with `403 invitation_required`, creating no user. |
| FR-05 | The system **shall** authenticate valid email/password pairs and return an access token plus a refresh cookie. |
| FR-06 | The system **shall** return an identical `401 invalid_credentials` response for unknown email and wrong password. |
| FR-07 | The system **shall** refuse disabled accounts with `403 account_disabled`. |
| FR-08 | The system **shall** rate-limit `login` and `register` per IP (and per email for login) and return `429` with `Retry-After`. |
| FR-09 | The system **shall** rotate the refresh token on every refresh and revoke the token family when a rotated token is reused. |
| FR-10 | The system **shall** revoke the refresh token family on logout and clear the cookie. |
| FR-11 | The system **shall** expose the current user via `GET /auth/me` for a valid bearer token. |
| FR-12 | The frontend **shall** keep the access token in memory only, attach it to API calls, and refresh once on `401` (single-flight). |
| FR-13 | The frontend **shall** render all labels, errors, and messages from the `fa` locale module and use RTL layout. |
| FR-14 | The system **shall** audit teacher registrations (who, when, invite code identifier — never the code itself). |

## 6. Business rules and invariants

- **BR-1** Email uniqueness is case-insensitive: `Ali@Example.com` and `ali@example.com` are the same account.
- **BR-2** Password policy: minimum 8 characters, maximum 128, must contain at least one letter and one digit. No composition rules beyond that.
- **BR-3** Full name: 3–100 characters after trimming; no control characters.
- **BR-4** A user has exactly one role. Default role is never assumed server-side; it comes from the validated request and is checked against allowed values.
- **BR-5** Teacher invite codes are read from configuration, compared in constant time, and never logged.
- **BR-6** Access token TTL is 15 minutes; refresh TTL is 14 days (30 with «مرا به خاطر بسپار»), and refresh tokens are single-use.
- **BR-7** Refresh token reuse is treated as theft: the entire family is revoked and the user must log in again.
- **BR-8** Disabled users (`is_active = false`) cannot log in and their existing refresh tokens are rejected on next use.
- **BR-9** Login updates `last_login_at` but never blocks the response on non-critical failures.

## 7. UX/API behavior

### 7.1 Pages

| Route | Purpose | States |
|---|---|---|
| `/login` | Email + password, remember-me, link to register | idle, submitting, field errors, form error, success redirect |
| `/register` | Name, email, password, confirm, role, invite code (teacher only), terms | idle, submitting, field errors, form error, success |
| `/dashboard` | Role-aware placeholder: greeting, user name/role, «خروج», coming-soon module cards | loading, loaded |

### 7.2 API contract

All error bodies use `application/problem+json` with `type`, `title`, `status`, `code`, `detail`, and optional `errors[]` (`field`, `message`).

| Method | Path | Body / Auth | Success | Errors |
|---|---|---|---|---|
| POST | `/api/v1/auth/register` | `{full_name, email, password, password_confirm, role, invite_code?, accepted_terms}` | `201` `UserPublic` | 422 `validation_error`, 409 `email_already_registered`, 403 `invitation_required`, 429 `rate_limited` |
| POST | `/api/v1/auth/login` | `{email, password, remember_me?}` | `200` `{access_token, token_type, expires_in, user}` + `Set-Cookie` | 401 `invalid_credentials`, 403 `account_disabled`, 422, 429 |
| POST | `/api/v1/auth/refresh` | cookie + `X-Requested-With` | `200` `{access_token, token_type, expires_in}` + rotated cookie | 401 `refresh_expired` / `refresh_reused` |
| POST | `/api/v1/auth/logout` | cookie | `204` | 401 |
| GET | `/api/v1/auth/me` | `Authorization: Bearer` | `200` `UserPublic` | 401 `token_expired` / `invalid_token` |
| GET | `/api/v1/health` | — | `200` `{status, version, db}` | — |

`UserPublic`: `id, full_name, email, role, is_active, created_at`.

Example register request:

```json
{
  "full_name": "سارا محمدی",
  "email": "sara@example.com",
  "password": "Parent1404",
  "password_confirm": "Parent1404",
  "role": "parent",
  "accepted_terms": true
}
```

Example error:

```json
{
  "type": "https://myschool.local/errors/email-already-registered",
  "title": "Email already registered",
  "status": 409,
  "code": "email_already_registered",
  "detail": "این ایمیل قبلاً ثبت شده است."
}
```

## 8. Data impact

New tables (migration `0001_identity`):

| Table | Columns | Constraints |
|---|---|---|
| `users` | `id` (UUID), `email` (varchar 254), `password_hash`, `full_name` (varchar 100), `role` (enum), `is_active`, `created_at`, `updated_at`, `last_login_at?` | unique index on `lower(email)`; check role in (`parent`,`student`,`teacher`) |
| `refresh_tokens` | `id`, `user_id` FK, `token_hash` (unique), `family_id`, `expires_at`, `revoked_at?`, `replaced_by?`, `user_agent?`, `ip?`, `created_at` | index on `family_id`, `user_id`; cascade delete with user |
| `audit_log` | `id`, `actor_id?`, `action`, `target_type`, `target_id`, `metadata` (JSON), `created_at` | index on `(target_type, target_id)`, `created_at` |

Retention: refresh tokens are deleted 30 days after expiry; audit rows are retained for the academic year.

## 9. Security and privacy

- Argon2id with library defaults (memory ≥ 64 MiB); password material never logged.
- Refresh cookie: `HttpOnly`, `SameSite=Lax`, `Secure` in production, `Path=/api/v1/auth`, `Max-Age` matching TTL.
- CSRF: refresh/logout require `X-Requested-With: XMLHttpRequest`; documented residual risk in ADR-0003.
- Rate limits: login 5/min per IP+email, 20/min per IP; register 3/min per IP.
- No user enumeration in messages, status codes, or timing-sensitive early returns.
- Access tokens carry `sub`, `role`, `type`, `jti`, `iat`, `exp`; signature secret from environment, minimum 32 bytes.
- Audit teacher registration without storing the invite code.
- Logs include request id, route, status, latency; never bodies, tokens, or email addresses.

## 10. Edge cases

- Duplicate registration racing the unique index → catch integrity error → `409` (not `500`).
- Email with uppercase/whitespace → normalized before uniqueness check.
- Password confirmation mismatch → `422` with `errors[]` on `password_confirm`.
- Teacher role with empty invite code → treated as missing.
- Long names (100+ chars) and control characters → `422`.
- Disabled account with a valid refresh cookie → refresh fails, cookie cleared.
- Refresh after 14 days → `401 refresh_expired`, UI redirects to login.
- Reuse of an already-rotated token → family revoked; subsequent refresh fails.
- Two tabs refreshing simultaneously → single-flight in the client; server tolerates a concurrent rotation by rejecting the older token.
- Network failure during submit → retry button, no duplicate user (idempotent by email uniqueness).

## 11. Acceptance criteria

**AC-1 (register parent)** — Given a valid parent payload, when I submit registration, then a `201` is returned, the user exists with role `parent`, and the response contains no password hash.

**AC-2 (duplicate email)** — Given an existing `sara@example.com`, when I register `SARA@example.com`, then `409 email_already_registered` is returned.

**AC-3 (teacher without invite)** — Given the role `teacher` and no invite code, when I submit, then `403 invitation_required` is returned and no user is created.

**AC-4 (teacher with invite)** — Given the configured invite code is `X`, when I register a teacher with `X`, then the account is created and an audit row exists.

**AC-5 (login success)** — Given valid credentials, when I log in, then I receive an access token and a refresh cookie with `HttpOnly` and `SameSite=Lax`.

**AC-6 (no enumeration)** — Given a wrong password and an unknown email, when I compare the two responses, then status, code, and message are identical.

**AC-7 (rate limit)** — Given 5 failed logins in a minute, when I try a 6th, then `429` with `Retry-After` is returned.

**AC-8 (refresh rotation)** — Given a valid refresh cookie, when I refresh, then a new cookie is issued and the old token fails.

**AC-9 (reuse detection)** — Given a rotated token is replayed, when I refresh with it, then the family is revoked and the request fails with `401`.

**AC-10 (logout)** — Given a logged-in session, when I log out, then `204` is returned, the cookie is cleared, and the refresh token no longer works.

**AC-11 (me)** — Given a valid access token, when I call `/auth/me`, then I receive my profile without sensitive fields; with an expired token I get `401 token_expired`.

**AC-12 (UI login)** — Given the login page, when I submit an invalid form, then field errors appear, focus moves to the first invalid field, and no request is sent.

**AC-13 (UI session restore)** — Given a valid refresh cookie, when I reload the app, then the dashboard renders without a login flash.

**AC-14 (RTL/accessibility)** — Given any auth page, when I run the accessibility smoke test, then every input has an associated label, errors are announced, and focus moves to the first invalid field.

## 12. Test strategy

- **Unit:** password policy, email normalization, invite-code comparison, token TTL math.
- **Integration (SQLite):** all AC-1…AC-11 backend scenarios against the real ASGI app and database.
- **PostgreSQL (CI):** the same migration and the unique-index race test.
- **Contract:** OpenAPI schema contains all endpoints, error models, and examples.
- **Frontend unit:** Vue Test Utils + MSW for AC-12, AC-13 and error mapping.
- **E2E (Playwright):** register → login → dashboard → logout against a seeded database.
- **Security:** no enumeration, cookie flags, revoke-on-reuse, rate-limit behavior.

## 13. Dependencies and open questions

- Depends on F-001 (repo, config, CI).
- **Open question Q1:** should teacher invite codes be single-use per teacher (tracked) or a rotating shared secret? *Default for now: shared secret from configuration, reusable; tracked in ADR-0005 as future work.*
- **Open question Q2:** do parents register before the school creates a child record? *Yes; linking happens in F-003.*

## 14. Definition of Ready

- [x] `Task-List.md` row `F-002` exists with `Specifying`/`Review` status.
- [x] This SPEC and the paired `PLAN.md` exist.
- [x] Acceptance criteria are objectively testable.
- [x] Dependencies (F-001) and non-goals are explicit.
- [x] Security/privacy implications documented.
- [x] ADR-0003 and ADR-0005 accepted.
