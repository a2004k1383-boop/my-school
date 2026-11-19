# Demo script (3 minutes)

1. **Repository tour (40s)** — open `AGENTS.md`, then `Task-List.md`, then `docs/features/F-002-identity/SPEC.md` and `PLAN.md`. Point out that the spec and plan were written before the code, and that `docs/adr/0003-authentication-session-strategy.md` records the session decision.
2. **Tests (40s)** — `cd apps/api; uv run pytest -q` → 29 passed. `cd apps/web; pnpm test` → 20 passed.
3. **Register (40s)** — open <http://127.0.0.1:5173/register>, create a parent account, show the validation errors first (empty form, weak password), then the success redirect.
4. **Login (30s)** — log in, show the dashboard greeting with the role, reload the page to show the session restore, then log out.
5. **Teacher path (20s)** — try registering as a teacher without the invite code: the request is rejected with a field error.
6. **Close (10s)** — `docs/submission/SUBMISSION.md` lists the evidence and the repository URL.
