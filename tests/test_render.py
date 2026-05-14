from __future__ import annotations

from pathlib import Path

from PIL import Image

from github_contrib_awtrix.colors import contribution_color
from github_contrib_awtrix.grid import ContributionDay, ContributionGrid
from github_contrib_awtrix.render import frame_colors, render_terminal, write_png


def test_terminal_render_has_8_rows(sample_grid: ContributionGrid) -> None:
    output = render_terminal(sample_grid)

    assert len(output.splitlines()) == 8


def test_png_render_is_32_by_8_at_10x(
    tmp_path: Path,
    sample_grid: ContributionGrid,
) -> None:
    path = tmp_path / "preview.png"

    write_png(sample_grid, path)

    with Image.open(path) as image:
        assert image.size == (320, 80)


def test_green_color_mode_uses_black_empty_cells(sample_grid: ContributionGrid) -> None:
    colors = frame_colors(sample_grid, color_mode="green")

    assert colors[0][0] == "#000000"
    assert colors[0][1] == "#00240f"
    assert colors[-1] == ["#000000"] * 32


def test_display_color_modes_have_distinct_scales(
) -> None:
    days = [
        ContributionDay(
            date="2026-01-01",
            weekday=index,
            contribution_count=index,
            contribution_level=level,
            color="#ebedf0",
        )
        for index, level in enumerate(
            [
                "NONE",
                "FIRST_QUARTILE",
                "SECOND_QUARTILE",
                "THIRD_QUARTILE",
                "FOURTH_QUARTILE",
            ]
        )
    ]

    assert [contribution_color(day, "green") for day in days] == [
        "#000000",
        "#00240f",
        "#007a2f",
        "#30d158",
        "#ffffff",
    ]
    assert [contribution_color(day, "purple") for day in days] == [
        "#000000",
        "#1a0033",
        "#6d28d9",
        "#c084fc",
        "#ffffff",
    ]
    assert [contribution_color(day, "yellow") for day in days] == [
        "#000000",
        "#2b1800",
        "#9a5b00",
        "#ffd60a",
        "#ffffff",
    ]
