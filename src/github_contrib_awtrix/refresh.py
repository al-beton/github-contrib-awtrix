from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, cast

from github_contrib_awtrix.colors import ColorMode, normalize_color_mode
from github_contrib_awtrix.commit_search import parse_org, parse_repo

Source = Literal["profile", "commit-search"]
TOKEN_ENV_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class RefreshApp:
    app_name: str
    source: Source = "profile"
    login: str | None = None
    org: str | None = None
    repo: str | None = None
    author_email: str | None = None
    token_env: str | None = None
    color_mode: ColorMode | None = None
    velocity: bool | None = None
    awtrix_app_duration: str | None = None


@dataclass(frozen=True)
class RefreshConfig:
    apps: list[RefreshApp]


def load_refresh_config(path: Path) -> RefreshConfig:
    try:
        raw = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as exc:
        raise ValueError(f"invalid refresh config TOML: {exc}") from exc

    raw_apps = raw.get("apps")
    if not isinstance(raw_apps, list) or not raw_apps:
        raise ValueError("refresh config must contain at least one [[apps]] entry")

    apps = [_parse_app(index, raw_app) for index, raw_app in enumerate(raw_apps, 1)]
    return RefreshConfig(apps=apps)


def _parse_app(index: int, raw_app: object) -> RefreshApp:
    if not isinstance(raw_app, dict):
        raise ValueError(f"apps entry {index} must be a table")
    app = cast(dict[str, object], raw_app)

    app_name = _required_str(app, "app_name", index)
    source = _source(app.get("source"), index)
    login = _optional_str(app, "login", index)
    org = _optional_str(app, "org", index)
    repo = _optional_str(app, "repo", index)
    author_email = _optional_str(app, "author_email", index)
    token_env = _token_env(app.get("token_env"), index)
    color_mode = _color_mode(app.get("color_mode"), index)
    velocity = _optional_bool(app, "velocity", index)
    awtrix_app_duration = _optional_positive_int_str(
        app,
        "awtrix_app_duration",
        index,
    )

    if source == "profile":
        if login is None:
            raise ValueError(f"apps entry {index} profile source requires login")
        if org is not None or repo is not None or author_email is not None:
            raise ValueError(
                f"apps entry {index} profile source cannot use org, repo, "
                "or author_email"
            )
    else:
        if login is not None:
            raise ValueError(
                f"apps entry {index} commit-search source cannot use login"
            )
        if org is not None and repo is not None:
            raise ValueError(f"apps entry {index} cannot use both org and repo")
        if author_email is None and org is None and repo is None:
            raise ValueError(
                f"apps entry {index} commit-search source requires author_email, "
                "org, or repo"
            )
        if org is not None:
            parse_org(org)
        if repo is not None:
            parse_repo(repo)

    return RefreshApp(
        app_name=app_name,
        source=source,
        login=login,
        org=org,
        repo=repo,
        author_email=author_email,
        token_env=token_env,
        color_mode=color_mode,
        velocity=velocity,
        awtrix_app_duration=awtrix_app_duration,
    )


def _required_str(raw_app: dict[str, object], key: str, index: int) -> str:
    value = raw_app.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"apps entry {index} requires {key}")
    return value


def _optional_str(
    raw_app: dict[str, object],
    key: str,
    index: int,
) -> str | None:
    value = raw_app.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"apps entry {index} {key} must be a non-empty string")
    return value


def _optional_bool(
    raw_app: dict[str, object],
    key: str,
    index: int,
) -> bool | None:
    value = raw_app.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"apps entry {index} {key} must be true or false")
    return value


def _optional_positive_int_str(
    raw_app: dict[str, object],
    key: str,
    index: int,
) -> str | None:
    value = raw_app.get(key)
    if value is None:
        return None
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"apps entry {index} {key} must be a positive integer")
    return str(value)


def _source(value: object, index: int) -> Source:
    if value is None:
        return "profile"
    if value == "profile":
        return "profile"
    if value == "commit-search":
        return "commit-search"
    raise ValueError(f"apps entry {index} source must be profile or commit-search")


def _token_env(value: object, index: int) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not TOKEN_ENV_PATTERN.fullmatch(value):
        raise ValueError(
            f"apps entry {index} token_env must be an environment variable name"
        )
    return value


def _color_mode(value: object, index: int) -> ColorMode | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"apps entry {index} color_mode must be a string")
    try:
        return normalize_color_mode(value)
    except ValueError as exc:
        raise ValueError(f"apps entry {index} {exc}") from exc
