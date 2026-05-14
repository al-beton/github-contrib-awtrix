from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from typing import Any

import certifi

from github_contrib_awtrix.grid import ContributionGrid, normalize_weeks

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

CONTRIBUTION_CALENDAR_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            weekday
            contributionCount
            contributionLevel
            color
          }
        }
      }
    }
  }
}
"""


class GitHubError(RuntimeError):
    pass


def fetch_contribution_grid(
    *,
    token: str,
    login: str,
    now: datetime | None = None,
) -> ContributionGrid:
    current_time = now or datetime.now().astimezone()
    from_time = current_time - timedelta(weeks=32)

    payload = {
        "query": CONTRIBUTION_CALENDAR_QUERY,
        "variables": {
            "login": login,
            "from": from_time.isoformat(),
            "to": current_time.isoformat(),
        },
    }
    data = _post_graphql(token=token, payload=payload)

    try:
        calendar = data["data"]["user"]["contributionsCollection"][
            "contributionCalendar"
        ]
    except (KeyError, TypeError) as exc:
        raise GitHubError("GitHub response did not contain contribution data") from exc

    weeks = normalize_weeks(calendar["weeks"], week_count=32)
    return ContributionGrid(
        login=login,
        generated_at=current_time.isoformat(),
        weeks=weeks,
    )


def _post_graphql(*, token: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        GITHUB_GRAPHQL_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        context = ssl.create_default_context(cafile=certifi.where())
        with urllib.request.urlopen(request, timeout=20, context=context) as response:
            response_body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GitHubError(f"GitHub request failed: HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise GitHubError(f"GitHub request failed: {exc.reason}") from exc

    data = json.loads(response_body)
    errors = data.get("errors")
    if errors:
        raise GitHubError(f"GitHub GraphQL returned errors: {errors}")
    return data
