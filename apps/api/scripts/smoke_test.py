"""End-to-end smoke check against the real database (run after migrations + seed).

Usage:
    uv run alembic upgrade head
    uv run python scripts/seed_demo.py
    uv run python scripts/smoke_test.py
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def main() -> int:
    failures = 0
    with TestClient(app) as client:
        health = client.get("/api/v1/health")
        print(f"health            -> {health.status_code} {health.json()}")
        failures += health.status_code != 200

        docs = client.get("/docs")
        print(f"openapi docs      -> {docs.status_code}")
        failures += docs.status_code != 200

        login = client.post(
            "/api/v1/auth/login",
            json={"email": "parent@demo.example.com", "password": "Demo1234"},
        )
        print(f"demo parent login -> {login.status_code}")
        failures += login.status_code != 200
        if login.status_code == 200:
            token = login.json()["access_token"]
            me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
            print(f"me                -> {me.status_code} {me.json().get('role')}")
            failures += me.status_code != 200

            refresh = client.post(
                "/api/v1/auth/refresh",
                headers={"X-Requested-With": "XMLHttpRequest"},
            )
            print(f"refresh           -> {refresh.status_code}")
            failures += refresh.status_code != 200

    print("SMOKE OK" if failures == 0 else f"SMOKE FAILED ({failures})")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
