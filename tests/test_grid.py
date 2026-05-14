from __future__ import annotations

from datetime import date, timedelta

from github_contrib_awtrix.grid import EMPTY_COLOR, normalize_weeks


def test_normalize_weeks_selects_latest_32_and_pads_partial_week() -> None:
    start = date(2025, 9, 28)
    github_weeks = []

    for week_index in range(33):
        days = []
        day_count = 5 if week_index == 32 else 7
        for day_index in range(day_count):
            current_date = start + timedelta(days=(week_index * 7) + day_index)
            days.append(
                {
                    "date": current_date.isoformat(),
                    "weekday": day_index,
                    "contributionCount": day_index,
                    "contributionLevel": "NONE",
                    "color": "#ebedf0",
                }
            )
        github_weeks.append({"contributionDays": days})

    weeks = normalize_weeks(github_weeks, week_count=32)

    assert len(weeks) == 32
    assert all(len(week) == 7 for week in weeks)
    assert weeks[0][0].date == "2025-10-05"
    assert weeks[-1][-1].contribution_count == 0
    assert weeks[-1][-1].color == EMPTY_COLOR
