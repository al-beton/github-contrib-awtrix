from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    token: str | None
    login: str | None
    awtrix_url: str | None = None
    awtrix_app_name: str = "github_contribution_graph"
    awtrix_app_duration: int = 7


def load_dotenv(path: Path = Path(".env")) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    return values


def resolve_config(
    *,
    token: str | None = None,
    login: str | None = None,
    awtrix_url: str | None = None,
    awtrix_app_name: str | None = None,
    awtrix_app_duration: str | None = None,
    require_github: bool = True,
    require_awtrix: bool = False,
    env_file: Path = Path(".env"),
    environ: dict[str, str] | None = None,
) -> Config:
    env = os.environ if environ is None else environ
    dotenv = load_dotenv(env_file)

    resolved_token = token or env.get("GITHUB_TOKEN") or dotenv.get("GITHUB_TOKEN")
    resolved_login = login or env.get("GITHUB_LOGIN") or dotenv.get("GITHUB_LOGIN")
    resolved_awtrix_url = (
        awtrix_url or env.get("AWTRIX_URL") or dotenv.get("AWTRIX_URL")
    )
    resolved_awtrix_app_name = (
        awtrix_app_name
        or env.get("AWTRIX_APP_NAME")
        or dotenv.get("AWTRIX_APP_NAME")
        or "github_contribution_graph"
    )
    resolved_awtrix_app_duration = _parse_positive_int(
        awtrix_app_duration
        or env.get("AWTRIX_APP_DURATION")
        or dotenv.get("AWTRIX_APP_DURATION")
        or "7",
        "AWTRIX_APP_DURATION",
    )

    required_values: list[tuple[str, str | None]] = []
    if require_github:
        required_values.extend(
            [
                ("GITHUB_TOKEN", resolved_token),
                ("GITHUB_LOGIN", resolved_login),
            ]
        )
    if require_awtrix:
        required_values.append(("AWTRIX_URL", resolved_awtrix_url))

    missing = [name for name, value in required_values if not value]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"missing required config: {joined}")

    return Config(
        token=resolved_token,
        login=resolved_login,
        awtrix_url=resolved_awtrix_url,
        awtrix_app_name=resolved_awtrix_app_name,
        awtrix_app_duration=resolved_awtrix_app_duration,
    )


def _parse_positive_int(value: str, name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive integer") from exc
    if parsed <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return parsed
