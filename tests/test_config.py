from __future__ import annotations

from pathlib import Path

import pytest

from github_contrib_awtrix.config import resolve_config
from github_contrib_awtrix.defaults import (
    DEFAULT_AWTRIX_APP_DURATION,
    DEFAULT_AWTRIX_APP_NAME,
)


def test_cli_flags_override_dotenv(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "GITHUB_TOKEN=dotenv-token",
                "GITHUB_LOGIN=dotenv-login",
                "AWTRIX_URL=http://dotenv-awtrix.local",
                "AWTRIX_APP_NAME=dotenv-app",
                "AWTRIX_APP_DURATION=9",
            ]
        )
    )

    config = resolve_config(
        token="cli-token",
        login="cli-login",
        awtrix_url="http://cli-awtrix.local",
        awtrix_app_name="cli-app",
        awtrix_app_duration="12",
        env_file=env_file,
        environ={},
    )

    assert config.token == "cli-token"
    assert config.login == "cli-login"
    assert config.awtrix_url == "http://cli-awtrix.local"
    assert config.awtrix_app_name == "cli-app"
    assert config.awtrix_app_duration == 12


def test_environment_overrides_dotenv(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("GITHUB_TOKEN=dotenv-token\nGITHUB_LOGIN=dotenv-login\n")

    config = resolve_config(
        env_file=env_file,
        environ={
            "GITHUB_TOKEN": "env-token",
            "GITHUB_LOGIN": "env-login",
        },
    )

    assert config.token == "env-token"
    assert config.login == "env-login"


def test_can_resolve_awtrix_without_github(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("AWTRIX_URL=http://awtrix.local\n")

    config = resolve_config(
        require_github=False,
        require_awtrix=True,
        env_file=env_file,
        environ={},
    )

    assert config.token is None
    assert config.login is None
    assert config.awtrix_url == "http://awtrix.local"
    assert config.awtrix_app_name == DEFAULT_AWTRIX_APP_NAME
    assert config.awtrix_app_duration == DEFAULT_AWTRIX_APP_DURATION


@pytest.mark.parametrize("duration", ["nope", "0", "-1"])
def test_invalid_awtrix_duration_fails(duration: str) -> None:
    with pytest.raises(ValueError, match="AWTRIX_APP_DURATION"):
        resolve_config(
            require_github=False,
            awtrix_app_duration=duration,
            environ={},
        )
