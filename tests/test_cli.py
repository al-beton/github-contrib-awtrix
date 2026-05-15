from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from github_contrib_awtrix import cli
from github_contrib_awtrix.config import Config
from github_contrib_awtrix.grid import ContributionGrid


def test_no_command_prints_help(capsys) -> None:
    exit_code = cli.main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "usage: github-contrib-awtrix" in captured.out
    assert captured.err == ""


def test_json_stdout(monkeypatch, capsys, sample_grid: ContributionGrid) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_LOGIN", "al-beton")
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setenv("AWTRIX_APP_DURATION", "7")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)
    monkeypatch.setattr(cli.AwtrixClient, "push_grid", lambda *_, **__: None)

    exit_code = cli.main(["push", "--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert exit_code == 0
    assert "Pushed AWTRIX CustomApp" in captured.err
    assert data["login"] == "al-beton"
    assert len(data["grid"]) == 32
    assert len(data["grid"][0]) == 7
    assert set(data["grid"][0][0]) == {
        "date",
        "weekday",
        "contributionCount",
        "contributionLevel",
        "color",
    }


def test_json_file(monkeypatch, tmp_path: Path, sample_grid: ContributionGrid) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_LOGIN", "al-beton")
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setenv("AWTRIX_APP_DURATION", "7")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)
    monkeypatch.setattr(cli.AwtrixClient, "push_grid", lambda *_, **__: None)

    json_path = tmp_path / "out" / "grid.json"

    exit_code = cli.main(["push", "--json", str(json_path)])

    assert exit_code == 0
    assert json.loads(json_path.read_text())["weeks"] == 32


def test_png_file(monkeypatch, tmp_path: Path, sample_grid: ContributionGrid) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_LOGIN", "al-beton")
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setenv("AWTRIX_APP_DURATION", "7")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)
    monkeypatch.setattr(cli.AwtrixClient, "push_grid", lambda *_, **__: None)

    png_path = tmp_path / "preview.png"

    exit_code = cli.main(["push", "--png", str(png_path)])

    assert exit_code == 0
    with Image.open(png_path) as image:
        assert image.size == (320, 80)


def test_install_uses_awtrix_only_config(monkeypatch, tmp_path: Path) -> None:
    installed: list[str] = []

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_LOGIN", raising=False)
    monkeypatch.delenv("AWTRIX_APP_NAME", raising=False)
    monkeypatch.delenv("AWTRIX_APP_DURATION", raising=False)
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setattr(
        cli.AwtrixClient,
        "install_app",
        lambda _, app_name, **__: installed.append(app_name),
    )

    exit_code = cli.main(["install"])

    assert exit_code == 0
    assert installed == ["github_contribution_graph"]


def test_uninstall_uses_awtrix_only_config(monkeypatch, tmp_path: Path) -> None:
    removed: list[str] = []

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_LOGIN", raising=False)
    monkeypatch.delenv("AWTRIX_APP_NAME", raising=False)
    monkeypatch.delenv("AWTRIX_APP_DURATION", raising=False)
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setattr(
        cli.AwtrixClient,
        "uninstall_app",
        lambda _, app_name: removed.append(app_name),
    )

    exit_code = cli.main(["uninstall"])

    assert exit_code == 0
    assert removed == ["github_contribution_graph"]


def test_push_passes_awtrix_duration(
    monkeypatch,
    sample_grid: ContributionGrid,
) -> None:
    durations: list[int] = []

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_LOGIN", "al-beton")
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setenv("AWTRIX_APP_DURATION", "7")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)
    monkeypatch.setattr(
        cli.AwtrixClient,
        "push_grid",
        lambda *_, duration_seconds, **__: durations.append(duration_seconds),
    )

    exit_code = cli.main(["push", "--awtrix-app-duration", "12"])

    assert exit_code == 0
    assert durations == [12]


def test_push_failure_keeps_prior_outputs(
    monkeypatch,
    tmp_path: Path,
    sample_grid: ContributionGrid,
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_LOGIN", "al-beton")
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setenv("AWTRIX_APP_DURATION", "7")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)
    monkeypatch.setattr(
        cli.AwtrixClient,
        "push_grid",
        lambda *_, **__: (_ for _ in ()).throw(OSError("no route")),
    )

    json_path = tmp_path / "grid.json"

    with pytest.raises(SystemExit) as exc_info:
        cli.main(["push", "--json", str(json_path)])

    assert exc_info.value.code == 1
    assert json_path.exists()


def test_doctor_checks_github_and_awtrix(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        cli,
        "resolve_config",
        lambda **_: Config(
            token="token",
            login="al-beton",
            awtrix_url="http://awtrix.local",
        ),
    )
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: None)
    monkeypatch.setattr(cli.AwtrixClient, "get_stats", lambda _: {"app": "Time"})

    exit_code = cli.main(["doctor"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "GitHub OK for al-beton" in captured.out
    assert "AWTRIX OK at http://awtrix.local" in captured.out


def test_push_passes_color_mode_to_awtrix(
    monkeypatch,
    sample_grid: ContributionGrid,
) -> None:
    pushed: list[str] = []

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_LOGIN", "al-beton")
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)
    monkeypatch.setattr(
        cli.AwtrixClient,
        "push_grid",
        lambda *_, color_mode, **__: pushed.append(color_mode),
    )

    exit_code = cli.main(["push", "--color-mode", "purple"])

    assert exit_code == 0
    assert pushed == ["purple"]


def test_push_passes_velocity_to_awtrix(
    monkeypatch,
    sample_grid: ContributionGrid,
) -> None:
    pushed: list[bool] = []

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_LOGIN", "al-beton")
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)
    monkeypatch.setattr(
        cli.AwtrixClient,
        "push_grid",
        lambda *_, velocity, **__: pushed.append(velocity),
    )

    exit_code = cli.main(["push", "--velocity"])

    assert exit_code == 0
    assert pushed == [True]


def test_push_no_velocity_overrides_env(
    monkeypatch,
    sample_grid: ContributionGrid,
) -> None:
    pushed: list[bool] = []

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_LOGIN", "al-beton")
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setenv("GITHUB_CONTRIB_VELOCITY", "true")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)
    monkeypatch.setattr(
        cli.AwtrixClient,
        "push_grid",
        lambda *_, velocity, **__: pushed.append(velocity),
    )

    exit_code = cli.main(["push", "--no-velocity"])

    assert exit_code == 0
    assert pushed == [False]


def test_refresh_config_pushes_multiple_apps(
    monkeypatch,
    tmp_path: Path,
    sample_grid: ContributionGrid,
) -> None:
    fetches: list[tuple[str | None, str | None, str | None, str | None]] = []
    pushed: list[tuple[str, str, bool, int]] = []

    config_path = tmp_path / "rotation.toml"
    config_path.write_text(
        """
[[apps]]
app_name = "github_green"
source = "profile"
login = "octocat"
token_env = "PROFILE_TOKEN"
color_mode = "green"
velocity = true

[[apps]]
app_name = "github_purple"
source = "commit-search"
org = "example-org"
token_env = "ORG_TOKEN"
color_mode = "purple"
velocity = false
awtrix_app_duration = 12
"""
    )

    monkeypatch.setenv("PROFILE_TOKEN", "profile-token")
    monkeypatch.setenv("ORG_TOKEN", "org-token")
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setenv("AWTRIX_APP_DURATION", "7")

    def fake_fetch_contribution_grid(**kwargs):
        fetches.append((None, kwargs["login"], None, kwargs["token"]))
        return sample_grid

    def fake_fetch_commit_search_grid(**kwargs):
        fetches.append(
            (kwargs["author_email"], kwargs["org"], kwargs["repo"], kwargs["token"])
        )
        return sample_grid

    monkeypatch.setattr(cli, "fetch_contribution_grid", fake_fetch_contribution_grid)
    monkeypatch.setattr(cli, "fetch_commit_search_grid", fake_fetch_commit_search_grid)
    monkeypatch.setattr(
        cli.AwtrixClient,
        "push_grid",
        lambda _, app_name, __, duration_seconds, color_mode, velocity: pushed.append(
            (app_name, color_mode, velocity, duration_seconds)
        ),
    )

    exit_code = cli.main(["refresh", "--config", str(config_path)])

    assert exit_code == 0
    assert fetches == [
        (None, "octocat", None, "profile-token"),
        (None, "example-org", None, "org-token"),
    ]
    assert pushed == [
        ("github_green", "green", True, 7),
        ("github_purple", "purple", False, 12),
    ]


def test_refresh_config_falls_back_to_default_token(
    monkeypatch,
    tmp_path: Path,
    sample_grid: ContributionGrid,
) -> None:
    tokens: list[str] = []

    config_path = tmp_path / "rotation.toml"
    config_path.write_text(
        """
[[apps]]
app_name = "github_green"
source = "profile"
login = "octocat"
"""
    )

    monkeypatch.setenv("GITHUB_TOKEN", "default-token")
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setattr(
        cli,
        "fetch_contribution_grid",
        lambda **kwargs: tokens.append(kwargs["token"]) or sample_grid,
    )
    monkeypatch.setattr(cli.AwtrixClient, "push_grid", lambda *_, **__: None)

    exit_code = cli.main(["refresh", "--config", str(config_path)])

    assert exit_code == 0
    assert tokens == ["default-token"]


def test_commit_search_source_does_not_require_login_or_repo(
    monkeypatch,
    sample_grid: ContributionGrid,
) -> None:
    pushed: list[str] = []

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.delenv("GITHUB_LOGIN", raising=False)
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: None)
    monkeypatch.setattr(
        cli,
        "fetch_commit_search_grid",
        lambda **_: sample_grid,
    )
    monkeypatch.setattr(
        cli.AwtrixClient,
        "push_grid",
        lambda *_, color_mode, **__: pushed.append(color_mode),
    )

    exit_code = cli.main(
        [
            "push",
            "--source",
            "commit-search",
            "--author-email",
            "bot@example.com",
            "--color-mode",
            "purple",
        ]
    )

    assert exit_code == 0
    assert pushed == ["purple"]


def test_commit_search_source_requires_at_least_one_filter(
    monkeypatch,
    sample_grid: ContributionGrid,
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.delenv("GITHUB_LOGIN", raising=False)
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setattr(
        cli,
        "fetch_commit_search_grid",
        lambda **_: sample_grid,
    )

    with pytest.raises(SystemExit) as exc_info:
        cli.main(
            [
                "push",
                "--source",
                "commit-search",
            ]
        )

    assert exc_info.value.code == 1


def test_commit_search_source_allows_org_without_author_email(
    monkeypatch,
    sample_grid: ContributionGrid,
) -> None:
    calls: list[tuple[str | None, str | None]] = []

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.delenv("GITHUB_LOGIN", raising=False)
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setattr(
        cli,
        "fetch_commit_search_grid",
        lambda **kwargs: calls.append((kwargs["author_email"], kwargs["org"]))
        or sample_grid,
    )
    monkeypatch.setattr(cli.AwtrixClient, "push_grid", lambda *_, **__: None)

    exit_code = cli.main(
        [
            "push",
            "--source",
            "commit-search",
            "--org",
            "AdvantageLabs",
        ]
    )

    assert exit_code == 0
    assert calls == [(None, "AdvantageLabs")]


def test_commit_search_source_writes_outputs_before_push(
    monkeypatch,
    tmp_path: Path,
    sample_grid: ContributionGrid,
) -> None:
    pushed: list[bool] = []

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.delenv("GITHUB_LOGIN", raising=False)
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setattr(
        cli,
        "fetch_commit_search_grid",
        lambda **_: sample_grid,
    )
    monkeypatch.setattr(
        cli.AwtrixClient,
        "push_grid",
        lambda *_, velocity, **__: pushed.append(velocity),
    )

    json_path = tmp_path / "grid.json"
    exit_code = cli.main(
        [
            "push",
            "--source",
            "commit-search",
            "--repo",
            "owner/repo",
            "--author-email",
            "bot@example.com",
            "--velocity",
            "--json",
            str(json_path),
        ]
    )

    assert exit_code == 0
    assert json.loads(json_path.read_text())["login"] == "al-beton"
    assert pushed == [True]


def test_commit_search_source_passes_org(
    monkeypatch,
    sample_grid: ContributionGrid,
) -> None:
    scopes: list[str | None] = []

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.delenv("GITHUB_LOGIN", raising=False)
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setattr(
        cli,
        "fetch_commit_search_grid",
        lambda **kwargs: scopes.append(kwargs["org"]) or sample_grid,
    )
    monkeypatch.setattr(cli.AwtrixClient, "push_grid", lambda *_, **__: None)

    exit_code = cli.main(
        [
            "push",
            "--source",
            "commit-search",
            "--org",
            "AdvantageLabs",
            "--author-email",
            "bot@example.com",
        ]
    )

    assert exit_code == 0
    assert scopes == ["AdvantageLabs"]


def test_commit_search_source_rejects_org_and_repo(
    monkeypatch,
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.delenv("GITHUB_LOGIN", raising=False)
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")

    with pytest.raises(SystemExit) as exc_info:
        cli.main(
            [
                "push",
                "--source",
                "commit-search",
                "--org",
                "AdvantageLabs",
                "--repo",
                "owner/repo",
                "--author-email",
                "bot@example.com",
            ]
        )

    assert exc_info.value.code == 1
