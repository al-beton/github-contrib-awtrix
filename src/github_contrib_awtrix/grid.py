from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, TypedDict

EMPTY_COLOR = "#ebedf0"
EMPTY_LEVEL = "NONE"


class ContributionDayJson(TypedDict):
    date: str
    weekday: int
    contributionCount: int
    contributionLevel: str
    color: str


@dataclass(frozen=True)
class ContributionDay:
    date: str
    weekday: int
    contribution_count: int
    contribution_level: str
    color: str

    @classmethod
    def from_github(cls, data: dict[str, Any]) -> ContributionDay:
        return cls(
            date=str(data["date"]),
            weekday=int(data["weekday"]),
            contribution_count=int(data["contributionCount"]),
            contribution_level=str(data["contributionLevel"]),
            color=str(data["color"]),
        )

    @classmethod
    def empty(cls, day: date, weekday: int) -> ContributionDay:
        return cls(
            date=day.isoformat(),
            weekday=weekday,
            contribution_count=0,
            contribution_level=EMPTY_LEVEL,
            color=EMPTY_COLOR,
        )

    def to_json(self) -> ContributionDayJson:
        return {
            "date": self.date,
            "weekday": self.weekday,
            "contributionCount": self.contribution_count,
            "contributionLevel": self.contribution_level,
            "color": self.color,
        }


@dataclass(frozen=True)
class ContributionGrid:
    login: str
    generated_at: str
    weeks: list[list[ContributionDay]]

    def to_json(self) -> dict[str, Any]:
        return {
            "login": self.login,
            "generatedAt": self.generated_at,
            "weeks": 32,
            "grid": [[day.to_json() for day in week] for week in self.weeks],
        }


def normalize_weeks(
    github_weeks: list[dict[str, Any]],
    *,
    week_count: int,
) -> list[list[ContributionDay]]:
    selected = github_weeks[-week_count:]
    weeks = [
        _normalize_week(
            [ContributionDay.from_github(day) for day in week["contributionDays"]]
        )
        for week in selected
    ]

    while len(weeks) < week_count:
        weeks.insert(0, _empty_week_before(weeks[0]))

    return weeks


def _normalize_week(days: list[ContributionDay]) -> list[ContributionDay]:
    if not days:
        raise ValueError("cannot normalize an empty GitHub week")

    normalized = list(days)
    while len(normalized) < 7:
        last = normalized[-1]
        next_date = date.fromisoformat(last.date) + timedelta(days=1)
        normalized.append(ContributionDay.empty(next_date, (last.weekday + 1) % 7))

    return normalized[:7]


def _empty_week_before(next_week: list[ContributionDay]) -> list[ContributionDay]:
    first_day = date.fromisoformat(next_week[0].date)
    start = first_day - timedelta(days=7)
    first_weekday = next_week[0].weekday
    return [
        ContributionDay.empty(
            start + timedelta(days=index), (first_weekday + index) % 7
        )
        for index in range(7)
    ]
