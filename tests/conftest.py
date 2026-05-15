from __future__ import annotations

from datetime import date, timedelta

import pytest

from github_contrib_awtrix.grid import ContributionDay, ContributionGrid


@pytest.fixture
def sample_grid() -> ContributionGrid:
    start = date(2026, 1, 4)
    weeks: list[list[ContributionDay]] = []
    colors = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

    for week_index in range(32):
        week: list[ContributionDay] = []
        for day_index in range(7):
            current_date = start + timedelta(days=(week_index * 7) + day_index)
            count = (week_index + day_index) % len(colors)
            week.append(
                ContributionDay(
                    date=current_date.isoformat(),
                    weekday=day_index,
                    contribution_count=count,
                    contribution_level="NONE" if count == 0 else "FIRST_QUARTILE",
                    color=colors[count],
                )
            )
        weeks.append(week)

    return ContributionGrid(
        login="octocat",
        generated_at="2026-05-14T12:00:00+02:00",
        weeks=weeks,
    )
