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
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)
    monkeypatch.setattr(cli.AwtrixClient, "push_grid", lambda *_: None)

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
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)
    monkeypatch.setattr(cli.AwtrixClient, "push_grid", lambda *_: None)

    json_path = tmp_path / "out" / "grid.json"

    exit_code = cli.main(["push", "--json", str(json_path)])

    assert exit_code == 0
    assert json.loads(json_path.read_text())["weeks"] == 32


def test_png_file(monkeypatch, tmp_path: Path, sample_grid: ContributionGrid) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_LOGIN", "al-beton")
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)
    monkeypatch.setattr(cli.AwtrixClient, "push_grid", lambda *_: None)

    png_path = tmp_path / "preview.png"

    exit_code = cli.main(["push", "--png", str(png_path)])

    assert exit_code == 0
    with Image.open(png_path) as image:
        assert image.size == (320, 80)


def test_install_uses_awtrix_only_config(monkeypatch) -> None:
    installed: list[str] = []

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_LOGIN", raising=False)
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setattr(
        cli.AwtrixClient,
        "install_app",
        lambda _, app_name: installed.append(app_name),
    )

    exit_code = cli.main(["install"])

    assert exit_code == 0
    assert installed == ["github_contribution_graph"]


def test_push_failure_keeps_prior_outputs(
    monkeypatch,
    tmp_path: Path,
    sample_grid: ContributionGrid,
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_LOGIN", "al-beton")
    monkeypatch.setenv("AWTRIX_URL", "http://awtrix.local")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)
    monkeypatch.setattr(
        cli.AwtrixClient,
        "push_grid",
        lambda *_: (_ for _ in ()).throw(OSError("no route")),
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
