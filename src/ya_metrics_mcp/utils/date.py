"""Date utilities for Yandex Metrika API."""
from __future__ import annotations

import re
from datetime import date, timedelta


_DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_date(value: str | None) -> str | None:
    """Validate and return a YYYY-MM-DD date string, or raise ValueError."""
    if value is None:
        return None
    if not _DATE_PATTERN.match(value):
        raise ValueError(f"Date must be in YYYY-MM-DD format, got: {value!r}")
    return value


def default_date_range(days: int = 7) -> tuple[str, str]:
    """Return (date_from, date_to) for the last N days."""
    today = date.today()
    date_from = today - timedelta(days=days)
    return date_from.isoformat(), today.isoformat()
