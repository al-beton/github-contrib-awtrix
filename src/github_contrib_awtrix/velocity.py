from __future__ import annotations

from datetime import datetime
from math import floor, isfinite

from github_contrib_awtrix.grid import ContributionGrid

VELOCITY_COLOR = "#9b4256"


def commits_per_day(grid: ContributionGrid) -> float:
    today = datetime.fromisoformat(grid.generated_at).date()
    visible_days = [
        day
        for week in grid.weeks
        for day in week
        if datetime.fromisoformat(day.date).date() <= today
    ]
    if not visible_days:
        return 0

    total = sum(day.contribution_count for day in visible_days)
    return total / len(visible_days)


def format_commits_per_day(value: float) -> str:
    if not isfinite(value) or value <= 0:
        return "0/d"
    if value < 1:
        rounded_down = max(floor(value * 10) / 10, 0.1)
        return f"{rounded_down:.1f}/d"
    if value < 999.5:
        return f"{round(value):.0f}/d"
    return f"{_format_compact(value)}/d"


def velocity_label(grid: ContributionGrid) -> str:
    return format_commits_per_day(commits_per_day(grid))


def _trim_decimal(value: float) -> str:
    text = f"{value:.1f}"
    return text.removesuffix(".0")


def _format_compact(value: float) -> str:
    units = (
        ("", 1),
        ("k", 1_000),
        ("M", 1_000_000),
        ("B", 1_000_000_000),
        ("T", 1_000_000_000_000),
        ("P", 1_000_000_000_000_000),
    )
    top_suffix, top_divisor = units[-1]
    if value >= top_divisor * 999.5:
        return f"999{top_suffix}"
    for index, (suffix, divisor) in enumerate(units[1:], start=1):
        next_divisor = units[index + 1][1] if index + 1 < len(units) else None
        if next_divisor is None or value < next_divisor * 999.5:
            scaled = value / divisor
            rounded = round(scaled, 1) if scaled < 9.95 else round(scaled)
            if next_divisor is not None and rounded >= 1000:
                continue
            return f"{_trim_decimal(rounded)}{suffix}"
    return f"999{top_suffix}"
