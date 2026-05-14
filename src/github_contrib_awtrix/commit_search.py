from __future__ import annotations

import json
import os
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import UTC, date, datetime, timedelta, tzinfo
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import certifi

from github_contrib_awtrix.github import GitHubError
from github_contrib_awtrix.grid import ContributionDay, ContributionGrid

WEEK_COUNT = 32
GITHUB_COMMIT_SEARCH_URL = "https://api.github.com/search/commits"
OWNER_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
REPO_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")
GITHUB_EMPTY_COLOR = "#ebedf0"
GITHUB_LEVEL_COLORS = {
    "NONE": GITHUB_EMPTY_COLOR,
    "FIRST_QUARTILE": "#9be9a8",
    "SECOND_QUARTILE": "#40c463",
    "THIRD_QUARTILE": "#30a14e",
    "FOURTH_QUARTILE": "#216e39",
}


def fetch_commit_search_grid(
    *,
    token: str,
    author_email: str | None = None,
    org: str | None = None,
    repo: str | None = None,
    now: datetime | None = None,
) -> ContributionGrid:
    _validate_search_filters(author_email=author_email, org=org, repo=repo)
    current_time = _current_time(now)
    today = current_time.date()
    start = visible_window_start(today)
    query_start = start - timedelta(days=1)
    query_end = today + timedelta(days=1)

    nodes = _search_commits(
        token=token,
        author_email=author_email,
        start=query_start,
        end=query_end,
        org=org,
        repo=repo,
    )
    commit_dates = matching_author_dates(
        nodes,
        author_email=author_email,
        target_time=current_time,
    )
    return build_commit_search_grid(
        author_email=author_email,
        commit_dates=commit_dates,
        org=org,
        repo=repo,
        now=current_time,
    )


def parse_org(org: str) -> str:
    if not OWNER_PATTERN.fullmatch(org):
        raise ValueError("org must be a GitHub organization login")
    return org


def parse_repo(repo: str) -> tuple[str, str]:
    owner, separator, name = repo.partition("/")
    if (
        not owner
        or separator != "/"
        or not name
        or "/" in name
        or not OWNER_PATTERN.fullmatch(owner)
        or not REPO_PATTERN.fullmatch(name)
    ):
        raise ValueError("repo must be in OWNER/REPO form")
    return owner, name


def visible_window_start(today: date) -> date:
    days_since_sunday = (today.weekday() + 1) % 7
    current_week_start = today - timedelta(days=days_since_sunday)
    return current_week_start - timedelta(weeks=WEEK_COUNT - 1)


def matching_author_dates(
    nodes: list[dict[str, Any]],
    *,
    author_email: str | None,
    target_time: datetime,
) -> list[date]:
    dates: list[date] = []
    for node in nodes:
        commit = node.get("commit") or {}
        author = commit.get("author") or {}
        if author_email is not None and author.get("email") != author_email:
            continue
        raw_date = author.get("date")
        if not isinstance(raw_date, str):
            continue
        dates.append(_parse_github_datetime(raw_date, target_time=target_time).date())
    return dates


def build_commit_search_grid(
    *,
    author_email: str | None,
    commit_dates: list[date],
    org: str | None = None,
    repo: str | None = None,
    now: datetime | None = None,
) -> ContributionGrid:
    _validate_search_filters(author_email=author_email, org=org, repo=repo)
    current_time = _current_time(now)
    today = current_time.date()
    start = visible_window_start(today)
    counts = Counter(day for day in commit_dates if start <= day <= today)
    max_count = max(counts.values(), default=0)

    weeks: list[list[ContributionDay]] = []
    for week_index in range(WEEK_COUNT):
        week: list[ContributionDay] = []
        for day_index in range(7):
            current_date = start + timedelta(days=(week_index * 7) + day_index)
            count = counts[current_date] if current_date <= today else 0
            level = _level_for_count(count, max_count)
            week.append(
                ContributionDay(
                    date=current_date.isoformat(),
                    weekday=day_index,
                    contribution_count=count,
                    contribution_level=level,
                    color=GITHUB_LEVEL_COLORS[level],
                )
            )
        weeks.append(week)

    identity = _identity(author_email=author_email, org=org, repo=repo)
    return ContributionGrid(
        login=identity,
        generated_at=current_time.isoformat(),
        weeks=weeks,
    )


def _search_commits(
    *,
    token: str,
    author_email: str | None,
    start: date,
    end: date,
    org: str | None,
    repo: str | None,
) -> list[dict[str, Any]]:
    _validate_search_filters(author_email=author_email, org=org, repo=repo)
    query_parts = [
        f"author-date:{start.isoformat()}..{end.isoformat()}",
    ]
    if author_email is not None:
        query_parts.append(f"author-email:{author_email}")
    if org is not None:
        query_parts.append(f"org:{parse_org(org)}")
    if repo is not None:
        parse_repo(repo)
        query_parts.append(f"repo:{repo}")

    items: list[dict[str, Any]] = []
    page = 1
    while True:
        data = _get_commit_search(
            token=token,
            query=" ".join(query_parts),
            page=page,
        )
        if data.get("incomplete_results"):
            raise GitHubError("GitHub commit search returned incomplete results")

        total_count = int(data.get("total_count") or 0)
        if total_count > 1000:
            raise GitHubError(
                "GitHub commit search returned more than 1000 matches; "
                "narrow the query with --org or --repo for now"
            )

        page_items = data.get("items") or []
        if not isinstance(page_items, list):
            raise GitHubError("GitHub commit search response did not contain items")

        items.extend(page_items)
        if len(items) >= total_count or len(page_items) < 100:
            return items
        page += 1


def _get_commit_search(*, token: str, query: str, page: int) -> dict[str, Any]:
    params = urllib.parse.urlencode(
        {
            "q": query,
            "per_page": "100",
            "page": str(page),
        }
    )
    request = urllib.request.Request(
        f"{GITHUB_COMMIT_SEARCH_URL}?{params}",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.cloak-preview+json",
        },
    )
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(request, timeout=20, context=context) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GitHubError(
            f"GitHub commit search failed: HTTP {exc.code} {detail}"
        ) from exc
    except urllib.error.URLError as exc:
        raise GitHubError(f"GitHub commit search failed: {exc.reason}") from exc

    return json.loads(response_body)


def _validate_search_filters(
    *,
    author_email: str | None,
    org: str | None,
    repo: str | None,
) -> None:
    if org is not None and repo is not None:
        raise ValueError("--org and --repo cannot be used together")
    if author_email is None and org is None and repo is None:
        raise ValueError("commit-search requires --author-email, --org, or --repo")


def _identity(*, author_email: str | None, org: str | None, repo: str | None) -> str:
    if author_email is None:
        if org is not None:
            return f"org:{org}"
        if repo is not None:
            return repo
        raise ValueError("commit-search requires --author-email, --org, or --repo")
    if org is not None:
        return f"{author_email}@org:{org}"
    if repo is not None:
        return f"{author_email}@{repo}"
    return author_email


def _level_for_count(count: int, max_count: int) -> str:
    if count <= 0 or max_count <= 0:
        return "NONE"
    ratio = count / max_count
    if ratio <= 0.25:
        return "FIRST_QUARTILE"
    if ratio <= 0.5:
        return "SECOND_QUARTILE"
    if ratio <= 0.75:
        return "THIRD_QUARTILE"
    return "FOURTH_QUARTILE"


def _parse_github_datetime(raw_date: str, *, target_time: datetime) -> datetime:
    parsed = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.astimezone()

    timezone = _conversion_timezone(target_time)
    if timezone is None:
        return parsed.astimezone()
    return parsed.astimezone(timezone)


def _current_time(now: datetime | None) -> datetime:
    current_time = now or datetime.now().astimezone()
    if current_time.tzinfo is None:
        return current_time.astimezone()
    return current_time


def _conversion_timezone(target_time: datetime) -> tzinfo | None:
    if target_time.tzinfo is UTC or isinstance(target_time.tzinfo, ZoneInfo):
        return target_time.tzinfo
    return _system_zoneinfo()


def _system_zoneinfo() -> ZoneInfo | None:
    timezone_name = os.environ.get("TZ")
    if timezone_name:
        return _load_zoneinfo(timezone_name)

    localtime = "/etc/localtime"
    if os.path.islink(localtime):
        target = os.path.realpath(localtime)
        marker = "/zoneinfo/"
        if marker in target:
            return _load_zoneinfo(target.split(marker, 1)[1])

    for timezone_name in time.tzname:
        timezone = _load_zoneinfo(timezone_name)
        if timezone is not None:
            return timezone
    return None


def _load_zoneinfo(timezone_name: str) -> ZoneInfo | None:
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return None
