from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from github_contrib_awtrix import cli
from github_contrib_awtrix.grid import ContributionGrid


def test_no_flags_prints_help(capsys) -> None:
    exit_code = cli.main([])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "usage: github-contrib-awtrix" in captured.out
    assert captured.err == ""


def test_json_stdout(monkeypatch, capsys, sample_grid: ContributionGrid) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_LOGIN", "al-beton")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)

    exit_code = cli.main(["--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert exit_code == 0
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
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)

    json_path = tmp_path / "out" / "grid.json"

    exit_code = cli.main(["--json", str(json_path)])

    assert exit_code == 0
    assert json.loads(json_path.read_text())["weeks"] == 32


def test_png_file(monkeypatch, tmp_path: Path, sample_grid: ContributionGrid) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_LOGIN", "al-beton")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)

    png_path = tmp_path / "preview.png"

    exit_code = cli.main(["--png", str(png_path)])

    assert exit_code == 0
    with Image.open(png_path) as image:
        assert image.size == (320, 80)


def test_push_only_fails_before_fetching(monkeypatch, capsys) -> None:
    def fail_fetch(**_) -> ContributionGrid:
        raise AssertionError("push-only should not fetch GitHub data")

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_LOGIN", raising=False)
    monkeypatch.setattr(cli, "fetch_contribution_grid", fail_fetch)

    with pytest.raises(SystemExit) as exc_info:
        cli.main(["--push"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert "--push is specified in the spec but not implemented yet" in captured.err


def test_push_failure_keeps_prior_outputs(
    monkeypatch,
    tmp_path: Path,
    sample_grid: ContributionGrid,
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_LOGIN", "al-beton")
    monkeypatch.setattr(cli, "fetch_contribution_grid", lambda **_: sample_grid)

    json_path = tmp_path / "grid.json"

    with pytest.raises(SystemExit) as exc_info:
        cli.main(["--json", str(json_path), "--push"])

    assert exc_info.value.code == 2
    assert json_path.exists()
