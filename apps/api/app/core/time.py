"""Academic calendar helpers. All timezone rules live here (see ADR-0004)."""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.core.config import get_settings


def school_tz() -> ZoneInfo:
    return ZoneInfo(get_settings().school_timezone)


def utc_now() -> datetime:
    return datetime.now(UTC)


def to_school_tz(moment: datetime) -> datetime:
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=UTC)
    return moment.astimezone(school_tz())


def end_of_local_day(local_date: date) -> datetime:
    """Return the UTC instant of 23:59:59.999999 on a local school date."""
    local_end = datetime.combine(local_date, time(23, 59, 59, 999999), tzinfo=school_tz())
    return local_end.astimezone(UTC)


def week_bounds(local_date: date) -> tuple[date, date]:
    """Return the Saturday–Friday week containing ``local_date``."""
    # Python weekday(): Monday=0 … Sunday=6. Saturday=5.
    days_since_saturday = (local_date.weekday() - 5) % 7
    start = local_date - timedelta(days=days_since_saturday)
    return start, start + timedelta(days=6)
