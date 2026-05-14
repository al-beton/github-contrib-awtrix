from __future__ import annotations

from github_contrib_awtrix.grid import ContributionDay, ContributionGrid
from github_contrib_awtrix.velocity import commits_per_day, format_commits_per_day


def test_commits_per_day_ignores_future_padding() -> None:
    grid = ContributionGrid(
        login="al-beton",
        generated_at="2026-05-02T12:00:00+02:00",
        weeks=[
            [
                _day("2026-05-01", 2),
                _day("2026-05-02", 4),
                _day("2026-05-03", 100),
            ]
        ],
    )

    assert commits_per_day(grid) == 3


def test_format_commits_per_day() -> None:
    assert format_commits_per_day(0) == "0/d"
    assert format_commits_per_day(0.04) == "0.1/d"
    assert format_commits_per_day(0.44) == "0.4/d"
    assert format_commits_per_day(0.97) == "0.9/d"
    assert format_commits_per_day(12.2) == "12/d"
    assert format_commits_per_day(999) == "999/d"
    assert format_commits_per_day(1_234) == "1.2k/d"
    assert format_commits_per_day(10_200) == "10k/d"
    assert format_commits_per_day(842_200) == "842k/d"
    assert format_commits_per_day(1_234_000) == "1.2M/d"
    assert format_commits_per_day(10_200_000) == "10M/d"


def _day(day: str, count: int) -> ContributionDay:
    return ContributionDay(
        date=day,
        weekday=0,
        contribution_count=count,
        contribution_level="NONE",
        color="#000000",
    )
