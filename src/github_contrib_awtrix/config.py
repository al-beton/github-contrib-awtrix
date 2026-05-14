from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Config:
    token: str
    login: str
    awtrix_url: str | None = None


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

    missing = [
        name
        for name, value in (
            ("GITHUB_TOKEN", resolved_token),
            ("GITHUB_LOGIN", resolved_login),
        )
        if not value
    ]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"missing required config: {joined}")

    if resolved_token is None or resolved_login is None:
        raise ValueError("missing required config")

    return Config(
        token=resolved_token,
        login=resolved_login,
        awtrix_url=resolved_awtrix_url,
    )
