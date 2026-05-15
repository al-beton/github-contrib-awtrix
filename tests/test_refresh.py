from __future__ import annotations

from pathlib import Path

import pytest

from github_contrib_awtrix.refresh import load_refresh_config


def test_load_refresh_config_parses_apps(tmp_path: Path) -> None:
    path = tmp_path / "rotation.toml"
    path.write_text(
        """
[[apps]]
app_name = "github_green"
source = "profile"
login = "octocat"
color_mode = "green"
velocity = true

[[apps]]
app_name = "github_purple"
source = "commit-search"
org = "example-org"
color_mode = "purple"
velocity = false
awtrix_app_duration = 10
"""
    )

    config = load_refresh_config(path)

    assert len(config.apps) == 2
    assert config.apps[0].app_name == "github_green"
    assert config.apps[0].source == "profile"
    assert config.apps[0].login == "octocat"
    assert config.apps[0].color_mode == "green"
    assert config.apps[0].velocity is True
    assert config.apps[1].app_name == "github_purple"
    assert config.apps[1].source == "commit-search"
    assert config.apps[1].org == "example-org"
    assert config.apps[1].awtrix_app_duration == "10"


def test_load_refresh_config_requires_apps(tmp_path: Path) -> None:
    path = tmp_path / "rotation.toml"
    path.write_text("")

    with pytest.raises(ValueError, match="at least one"):
        load_refresh_config(path)


def test_load_refresh_config_validates_source_fields(tmp_path: Path) -> None:
    path = tmp_path / "rotation.toml"
    path.write_text(
        """
[[apps]]
app_name = "github_green"
source = "profile"
org = "example-org"
"""
    )

    with pytest.raises(ValueError, match="profile source requires login"):
        load_refresh_config(path)


def test_load_refresh_config_rejects_org_and_repo(tmp_path: Path) -> None:
    path = tmp_path / "rotation.toml"
    path.write_text(
        """
[[apps]]
app_name = "github_purple"
source = "commit-search"
org = "example-org"
repo = "example-org/example-repo"
"""
    )

    with pytest.raises(ValueError, match="both org and repo"):
        load_refresh_config(path)
