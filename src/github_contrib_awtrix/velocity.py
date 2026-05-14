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
    if value < 1_000:
        return f"{round(value):.0f}/d"
    if value < 10_000:
        return f"{_trim_decimal(value / 1_000):s}k/d"
    if value < 1_000_000:
        return f"{round(value / 1_000):.0f}k/d"
    if value < 10_000_000:
        return f"{_trim_decimal(value / 1_000_000):s}M/d"
    return f"{round(value / 1_000_000):.0f}M/d"


def velocity_label(grid: ContributionGrid) -> str:
    return format_commits_per_day(commits_per_day(grid))


def _trim_decimal(value: float) -> str:
    text = f"{value:.1f}"
    return text.removesuffix(".0")
