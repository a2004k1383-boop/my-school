# Â«Ù…Ø¯Ø±Ø³Ù‡ Ù…Ù†Â» â€” My School

> One place for everything a family needs from school: timetable, assignments, announcements, and grades â€” instead of paper notes, scattered chat groups, and phone calls.

[![CI](https://img.shields.io/badge/CI-pending-lightgrey)](#) [![Vue 3](https://img.shields.io/badge/Vue-3-42b883)](https://vuejs.org) [![FastAPI](https://img.shields.io/badge/FastAPI-0.x-009688)](https://fastapi.tiangolo.com)

## What it is

A school communication platform with three roles:

| Role | Persian | Sees |
|---|---|---|
| Parent | ÙˆØ§Ù„Ø¯ | Their children's week: assignments, announcements, grades |
| Student | Ø¯Ø§Ù†Ø´â€ŒØ¢Ù…ÙˆØ² | Their own timetable, assignments, announcements, grades |
| Teacher | Ù…Ø¹Ù„Ù… | The classes they teach: publish assignments and announcements, record grades |

The repository is built as a course project in software engineering: it demonstrates requirements engineering, architectural decision records, TDD, and a documented delivery process.

## Status

| Milestone | Scope | Status |
|---|---|---|
| M0 | Repository foundation (F-001) | âœ… |
| M1 | Identity: registration + login (F-002) | ðŸš§ |
| M2 | School structure, timetable, assignments (F-003â€¦F-005) | Planned |
| M3 | Announcements, grades (F-006, F-007) | Planned |
| M4 | Messaging, notifications, production readiness | Planned |

Current deliverable: **login and registration pages** for the three roles, with a role-aware dashboard placeholder.

## Tech stack

- **Frontend:** Vue 3 (`<script setup>`, TypeScript), Vite, Vue Router, Pinia, Vitest, MSW â€” Persian/RTL, Vazirmatn.
- **Backend:** FastAPI, Pydantic v2, SQLAlchemy 2.x (async), Alembic, Argon2id, PyJWT, slowapi.
- **Data:** SQLite for local development and tests, PostgreSQL 16 in CI and production.
- **Quality:** ruff, mypy, ESLint, Prettier, pytest, Vitest, GitHub Actions.

## Repository layout

```
my-school/
â”œâ”€â”€ AGENTS.md                 # engineering rules for humans and AI agents
â”œâ”€â”€ Task-List.md              # feature ledger: every feature is registered before it is built
â”œâ”€â”€ docs/
â”‚   â”œâ”€â”€ SRS.md                # software requirements specification
â”‚   â”œâ”€â”€ ARCHITECTURE.md       # system architecture and boundaries
â”‚   â”œâ”€â”€ ROADMAP.md            # phased delivery plan
â”‚   â”œâ”€â”€ adr/                  # architecture decision records
â”‚   â”œâ”€â”€ features/             # SPEC + PLAN per feature
â”‚   â”œâ”€â”€ runbooks/             # local development, operations
â”‚   â””â”€â”€ submission/           # course submission pack
â”œâ”€â”€ apps/
â”‚   â”œâ”€â”€ api/                  # FastAPI service
â”‚   â””â”€â”€ web/                  # Vue 3 SPA
â””â”€â”€ .github/workflows/        # CI
```

## Quickstart

Prerequisites: Python â‰¥ 3.12, [uv](https://docs.astral.sh/uv/), Node â‰¥ 20, pnpm â‰¥ 9.

```bash
# 1) API
cd apps/api
cp .env.example .env          # Windows: copy .env.example .env
uv sync
uv run alembic upgrade head
uv run python scripts/seed_demo.py       # optional demo users
uv run uvicorn app.main:app --reload --port 8000

# 2) Web (new terminal, repository root)
pnpm install
pnpm dev:web                  # http://127.0.0.1:5173
```

API documentation: <http://127.0.0.1:8000/docs>

Demo accounts (after seeding): `parent@demo.example.com`, `student@demo.example.com`, `teacher@demo.example.com` â€” password `Demo1234`. Demo seeding refuses to run when `APP_ENV=production`.

## Quality gates

```bash
pnpm verify        # backend lint/type/tests + frontend lint/type/tests/build
```

## Documentation

Start with [`AGENTS.md`](AGENTS.md) (rules), [`Task-List.md`](Task-List.md) (what is planned), then:

- Requirements: [`docs/SRS.md`](docs/SRS.md)
- Architecture: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Decisions: [`docs/adr/`](docs/adr)
- Feature specs: [`docs/features/`](docs/features)

Every feature follows the same path: `Task-List.md` entry â†’ `SPEC.md` â†’ `PLAN.md` â†’ TDD implementation â†’ tests green â†’ docs updated.

## Contributing

1. Pick a `Ready` item from `Task-List.md`.
2. Read its `SPEC.md` and `PLAN.md`.
3. Write the failing test first.
4. Keep the docs and the code in the same commit.

## License

Coursework â€” all rights reserved. No open-source license is granted unless stated otherwise.
