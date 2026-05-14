from __future__ import annotations

from pathlib import Path

from github_contrib_awtrix.config import resolve_config


def test_cli_flags_override_dotenv(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "GITHUB_TOKEN=dotenv-token",
                "GITHUB_LOGIN=dotenv-login",
                "AWTRIX_URL=http://dotenv-awtrix.local",
            ]
        )
    )

    config = resolve_config(
        token="cli-token",
        login="cli-login",
        awtrix_url="http://cli-awtrix.local",
        env_file=env_file,
        environ={},
    )

    assert config.token == "cli-token"
    assert config.login == "cli-login"
    assert config.awtrix_url == "http://cli-awtrix.local"


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
