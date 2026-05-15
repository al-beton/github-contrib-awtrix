from __future__ import annotations

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

import pytest

from github_contrib_awtrix import commit_search
from github_contrib_awtrix.github import GitHubError


def test_build_commit_search_grid_groups_commits_by_day() -> None:
    grid = commit_search.build_commit_search_grid(
        author_email="bot@example.com",
        commit_dates=[
            date(2026, 4, 22),
            date(2026, 4, 22),
            date(2026, 4, 23),
        ],
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )

    counts = {day.date: day.contribution_count for week in grid.weeks for day in week}

    assert grid.login == "bot@example.com"
    assert len(grid.weeks) == 32
    assert all(len(week) == 7 for week in grid.weeks)
    assert grid.weeks[0][0].date == "2025-10-05"
    assert grid.weeks[-1][-1].date == "2026-05-16"
    assert counts["2026-04-22"] == 2
    assert counts["2026-04-23"] == 1
    assert counts["2026-05-16"] == 0


def test_build_commit_search_grid_includes_optional_repo_identity() -> None:
    grid = commit_search.build_commit_search_grid(
        author_email="bot@example.com",
        repo="owner/repo",
        commit_dates=[],
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )

    assert grid.login == "bot@example.com@owner/repo"


def test_build_commit_search_grid_includes_optional_org_identity() -> None:
    grid = commit_search.build_commit_search_grid(
        author_email="bot@example.com",
        org="owner",
        commit_dates=[],
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )

    assert grid.login == "bot@example.com@org:owner"


def test_build_commit_search_grid_can_use_org_without_author() -> None:
    grid = commit_search.build_commit_search_grid(
        author_email=None,
        org="owner",
        commit_dates=[],
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )

    assert grid.login == "org:owner"


def test_build_commit_search_grid_can_use_repo_without_author() -> None:
    grid = commit_search.build_commit_search_grid(
        author_email=None,
        repo="owner/repo",
        commit_dates=[],
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )

    assert grid.login == "owner/repo"


def test_build_commit_search_grid_requires_a_filter() -> None:
    with pytest.raises(ValueError, match="requires"):
        commit_search.build_commit_search_grid(
            author_email=None,
            commit_dates=[],
            now=datetime(2026, 5, 14, 12, tzinfo=UTC),
        )


def test_build_commit_search_grid_rejects_org_and_repo() -> None:
    with pytest.raises(ValueError, match="--org and --repo"):
        commit_search.build_commit_search_grid(
            author_email="bot@example.com",
            org="owner",
            repo="owner/repo",
            commit_dates=[],
            now=datetime(2026, 5, 14, 12, tzinfo=UTC),
        )


def test_build_commit_search_grid_maps_intensity_levels() -> None:
    grid = commit_search.build_commit_search_grid(
        author_email="bot@example.com",
        commit_dates=[
            date(2026, 4, 20),
            date(2026, 4, 21),
            date(2026, 4, 21),
            date(2026, 4, 22),
            date(2026, 4, 22),
            date(2026, 4, 22),
            date(2026, 4, 23),
            date(2026, 4, 23),
            date(2026, 4, 23),
            date(2026, 4, 23),
        ],
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )

    levels = {day.date: day.contribution_level for week in grid.weeks for day in week}

    assert levels["2026-04-20"] == "FIRST_QUARTILE"
    assert levels["2026-04-21"] == "SECOND_QUARTILE"
    assert levels["2026-04-22"] == "THIRD_QUARTILE"
    assert levels["2026-04-23"] == "FOURTH_QUARTILE"


def test_build_commit_search_grid_handles_empty_matches() -> None:
    grid = commit_search.build_commit_search_grid(
        author_email="missing@example.com",
        commit_dates=[],
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )

    assert sum(day.contribution_count for week in grid.weeks for day in week) == 0
    assert {day.contribution_level for week in grid.weeks for day in week} == {"NONE"}


def test_build_commit_search_grid_ignores_dates_outside_visible_window() -> None:
    grid = commit_search.build_commit_search_grid(
        author_email="bot@example.com",
        commit_dates=[
            date(2025, 10, 4),
            date(2025, 10, 4),
            date(2025, 10, 5),
            date(2026, 5, 15),
            date(2026, 5, 15),
        ],
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )

    days = {day.date: day for week in grid.weeks for day in week}

    assert days["2025-10-05"].contribution_count == 1
    assert days["2025-10-05"].contribution_level == "FOURTH_QUARTILE"
    assert "2025-10-04" not in days
    assert days["2026-05-15"].contribution_count == 0


def test_matching_author_dates_uses_exact_email_and_local_date() -> None:
    dates = commit_search.matching_author_dates(
        [
            {
                "commit": {
                    "author": {
                        "email": "bot@example.com",
                        "date": "2026-04-22T22:30:00Z",
                    }
                },
            },
            {
                "commit": {
                    "author": {
                        "email": "person@example.com",
                        "date": "2026-04-22T23:30:00Z",
                    }
                },
            },
        ],
        author_email="bot@example.com",
        target_time=datetime.fromisoformat("2026-05-14T12:00:00+02:00"),
    )

    assert dates == [date(2026, 4, 23)]


def test_matching_author_dates_uses_zoneinfo_dst_rules() -> None:
    dates = commit_search.matching_author_dates(
        [
            {
                "commit": {
                    "author": {
                        "email": "bot@example.com",
                        "date": "2026-03-28T23:30:00Z",
                    }
                },
            }
        ],
        author_email="bot@example.com",
        target_time=datetime(2026, 5, 14, 12, tzinfo=ZoneInfo("Europe/Berlin")),
    )

    assert dates == [date(2026, 3, 29)]


def test_fetch_commit_search_grid_filters_author_email_and_pages(monkeypatch) -> None:
    payloads = []
    pages = [
        {
            "total_count": 101,
            "incomplete_results": False,
            "items": [
                {
                    "commit": {
                        "author": {
                            "email": "bot@example.com",
                            "date": "2026-04-22T10:00:00Z",
                        }
                    },
                }
            ]
            * 100,
        },
        {
            "total_count": 101,
            "incomplete_results": False,
            "items": [
                {
                    "commit": {
                        "author": {
                            "email": "bot@example.com",
                            "date": "2026-04-23T10:00:00Z",
                        }
                    },
                },
                {
                    "commit": {
                        "author": {
                            "email": "person@example.com",
                            "date": "2026-04-23T11:00:00Z",
                        }
                    },
                },
            ],
        },
    ]

    def fake_get_commit_search(*, token, query, page):
        payloads.append((token, query, page))
        return pages.pop(0)

    monkeypatch.setattr(commit_search, "_get_commit_search", fake_get_commit_search)

    grid = commit_search.fetch_commit_search_grid(
        token="token",
        author_email="bot@example.com",
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )
    counts = {day.date: day.contribution_count for week in grid.weeks for day in week}

    assert counts["2026-04-22"] == 100
    assert counts["2026-04-23"] == 1
    assert payloads[0] == (
        "token",
        (
            "author-date:2025-10-04..2026-05-15 "
            "author-email:bot@example.com"
        ),
        1,
    )
    assert payloads[1][2] == 2


def test_fetch_commit_search_grid_can_narrow_to_repo(monkeypatch) -> None:
    queries: list[str] = []

    def fake_get_commit_search(*, token, query, page):
        queries.append(query)
        return {"total_count": 0, "incomplete_results": False, "items": []}

    monkeypatch.setattr(commit_search, "_get_commit_search", fake_get_commit_search)

    commit_search.fetch_commit_search_grid(
        token="token",
        author_email="bot@example.com",
        repo="owner/repo",
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )

    assert queries == [
        (
            "author-date:2025-10-04..2026-05-15 "
            "author-email:bot@example.com "
            "repo:owner/repo"
        )
    ]


def test_fetch_commit_search_grid_can_narrow_to_org(monkeypatch) -> None:
    queries: list[str] = []

    def fake_get_commit_search(*, token, query, page):
        queries.append(query)
        return {"total_count": 0, "incomplete_results": False, "items": []}

    monkeypatch.setattr(commit_search, "_get_commit_search", fake_get_commit_search)

    commit_search.fetch_commit_search_grid(
        token="token",
        author_email="bot@example.com",
        org="owner",
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )

    assert queries == [
        (
            "author-date:2025-10-04..2026-05-15 "
            "author-email:bot@example.com "
            "org:owner"
        )
    ]


def test_fetch_commit_search_grid_can_search_org_without_author(monkeypatch) -> None:
    calls: list[tuple[str, int]] = []

    def fake_get_github_json(
        *,
        token,
        url,
        params,
        accept="application/vnd.github+json",
    ):
        calls.append((url, int(params["page"])))
        if url.endswith("/orgs/owner/repos"):
            return [
                {
                    "full_name": "owner/active",
                    "pushed_at": "2026-04-22T10:00:00Z",
                },
                {
                    "full_name": "owner/old",
                    "pushed_at": "2025-09-01T10:00:00Z",
                },
            ]
        if url.endswith("/repos/owner/active/commits"):
            return [
                {
                    "commit": {
                        "author": {
                            "email": "one@example.com",
                            "date": "2026-04-22T10:00:00Z",
                        }
                    }
                }
            ]
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(commit_search, "_get_github_json", fake_get_github_json)

    grid = commit_search.fetch_commit_search_grid(
        token="token",
        org="owner",
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )
    counts = {day.date: day.contribution_count for week in grid.weeks for day in week}

    assert grid.login == "org:owner"
    assert counts["2026-04-22"] == 1
    assert calls == [
        ("https://api.github.com/orgs/owner/repos", 1),
        ("https://api.github.com/repos/owner/active/commits", 1),
    ]


def test_fetch_commit_search_grid_without_author_counts_every_author(
    monkeypatch,
) -> None:
    def fake_get_github_json(
        *,
        token,
        url,
        params,
        accept="application/vnd.github+json",
    ):
        assert url == "https://api.github.com/repos/owner/repo/commits"
        return [
            {
                "commit": {
                    "author": {
                        "email": "one@example.com",
                        "date": "2026-04-22T10:00:00Z",
                    }
                }
            },
            {
                "commit": {
                    "author": {
                        "email": "two@example.com",
                        "date": "2026-04-22T11:00:00Z",
                    }
                }
            },
        ]

    monkeypatch.setattr(commit_search, "_get_github_json", fake_get_github_json)

    grid = commit_search.fetch_commit_search_grid(
        token="token",
        repo="owner/repo",
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )
    counts = {day.date: day.contribution_count for week in grid.weeks for day in week}

    assert counts["2026-04-22"] == 2


def test_fetch_commit_search_grid_paginates_repository_commits(monkeypatch) -> None:
    pages = [
        [
            {
                "commit": {
                    "author": {
                        "email": "one@example.com",
                        "date": "2026-04-22T10:00:00Z",
                    }
                }
            }
        ]
        * 100,
        [
            {
                "commit": {
                    "author": {
                        "email": "two@example.com",
                        "date": "2026-04-23T11:00:00Z",
                    }
                }
            }
        ],
    ]

    def fake_get_github_json(
        *,
        token,
        url,
        params,
        accept="application/vnd.github+json",
    ):
        assert url == "https://api.github.com/repos/owner/repo/commits"
        return pages[int(params["page"]) - 1]

    monkeypatch.setattr(commit_search, "_get_github_json", fake_get_github_json)

    grid = commit_search.fetch_commit_search_grid(
        token="token",
        repo="owner/repo",
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )
    counts = {day.date: day.contribution_count for week in grid.weeks for day in week}

    assert counts["2026-04-22"] == 100
    assert counts["2026-04-23"] == 1


def test_fetch_commit_search_grid_with_author_still_uses_commit_search(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        commit_search,
        "_get_commit_search",
        lambda **_: {
            "total_count": 2,
            "incomplete_results": False,
            "items": [
                {
                    "commit": {
                        "author": {
                            "email": "one@example.com",
                            "date": "2026-04-22T10:00:00Z",
                        }
                    }
                },
                {
                    "commit": {
                        "author": {
                            "email": "two@example.com",
                            "date": "2026-04-22T11:00:00Z",
                        }
                    }
                },
            ],
        },
    )

    grid = commit_search.fetch_commit_search_grid(
        token="token",
        author_email="one@example.com",
        org="owner",
        now=datetime(2026, 5, 14, 12, tzinfo=UTC),
    )
    counts = {day.date: day.contribution_count for week in grid.weeks for day in week}

    assert counts["2026-04-22"] == 1


def test_fetch_commit_search_grid_rejects_org_and_repo() -> None:
    with pytest.raises(ValueError, match="--org and --repo"):
        commit_search.fetch_commit_search_grid(
            token="token",
            author_email="bot@example.com",
            org="owner",
            repo="owner/repo",
            now=datetime(2026, 5, 14, 12, tzinfo=UTC),
        )


def test_parse_org_rejects_invalid_value() -> None:
    with pytest.raises(ValueError, match="organization login"):
        commit_search.parse_org("owner/repo")


def test_parse_org_rejects_search_injection() -> None:
    with pytest.raises(ValueError, match="organization login"):
        commit_search.parse_org("owner fork:true")


def test_parse_org_rejects_leading_hyphen() -> None:
    with pytest.raises(ValueError, match="organization login"):
        commit_search.parse_org("-owner")


def test_parse_repo_rejects_invalid_value() -> None:
    with pytest.raises(ValueError, match="OWNER/REPO"):
        commit_search.parse_repo("owner/repo/extra")


def test_parse_repo_rejects_surrounding_whitespace() -> None:
    with pytest.raises(ValueError, match="OWNER/REPO"):
        commit_search.parse_repo(" owner/repo ")


def test_parse_repo_rejects_component_whitespace() -> None:
    with pytest.raises(ValueError, match="OWNER/REPO"):
        commit_search.parse_repo("owner /repo")


def test_parse_repo_rejects_search_injection() -> None:
    with pytest.raises(ValueError, match="OWNER/REPO"):
        commit_search.parse_repo("owner/repo fork:true")


def test_fetch_commit_search_grid_errors_on_incomplete_results(monkeypatch) -> None:
    monkeypatch.setattr(
        commit_search,
        "_get_commit_search",
        lambda **_: {"total_count": 1, "incomplete_results": True, "items": []},
    )

    with pytest.raises(GitHubError, match="incomplete"):
        commit_search.fetch_commit_search_grid(
            token="token",
            author_email="bot@example.com",
            now=datetime(2026, 5, 14, 12, tzinfo=UTC),
        )


def test_fetch_commit_search_grid_errors_on_search_cap(monkeypatch) -> None:
    monkeypatch.setattr(
        commit_search,
        "_get_commit_search",
        lambda **_: {"total_count": 1001, "incomplete_results": False, "items": []},
    )

    with pytest.raises(GitHubError, match="more than 1000"):
        commit_search.fetch_commit_search_grid(
            token="token",
            author_email="bot@example.com",
            now=datetime(2026, 5, 14, 12, tzinfo=UTC),
        )
