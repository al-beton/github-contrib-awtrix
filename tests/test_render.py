from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from PIL import Image

from github_contrib_awtrix.colors import contribution_color
from github_contrib_awtrix.grid import ContributionDay, ContributionGrid
from github_contrib_awtrix.render import (
    _ADVANCE,
    _FONT,
    frame_colors,
    render_terminal,
    write_png,
)
from github_contrib_awtrix.velocity import VELOCITY_COLOR, format_commits_per_day


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


def test_velocity_overlay_draws_over_bottom_left(sample_grid: ContributionGrid) -> None:
    colors = frame_colors(sample_grid, color_mode="green", velocity=True)

    assert colors[3][0] == VELOCITY_COLOR
    assert colors[7][2] == VELOCITY_COLOR
    assert colors[-1] != ["#000000"] * 32


def test_velocity_decimal_point_is_tight() -> None:
    grid = _grid_with_counts([1, 1, 1, 1, 1, 1, 1, 1, 1, 0])

    colors = frame_colors(grid, color_mode="green", velocity=True)

    assert colors[7][4] == VELOCITY_COLOR
    assert colors[7][6] == VELOCITY_COLOR


def test_velocity_labels_fit_32_pixel_frame() -> None:
    values = [
        0,
        0.04,
        0.9,
        12,
        999,
        999.5,
        1_200,
        112_000,
        999_499,
        999_500,
        1_200_000,
        999_500_000,
        1_200_000_000,
        999_500_000_000,
        1_200_000_000_000,
        999_500_000_000_000,
        999_500_000_000_000_000,
    ]

    for value in values:
        assert _text_width(format_commits_per_day(value)) <= 32


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


def _grid_with_counts(counts: list[int]) -> ContributionGrid:
    start = date(2026, 5, 1)
    count_by_index = dict(enumerate(counts))
    days = [
        ContributionDay(
            date=(start + timedelta(days=index)).isoformat(),
            weekday=index % 7,
            contribution_count=count_by_index.get(index, 0),
            contribution_level="NONE",
            color="#000000",
        )
        for index in range(32 * 7)
    ]
    return ContributionGrid(
        login="al-beton",
        generated_at=(start + timedelta(days=len(counts) - 1)).isoformat(),
        weeks=[days[index : index + 7] for index in range(0, len(days), 7)],
    )


def _text_width(text: str) -> int:
    width = 0
    for char in text:
        glyph = _FONT.get(char)
        width += _ADVANCE.get(char, len(glyph[0]) + 1) if glyph else 4
    return max(width - 1, 0)
