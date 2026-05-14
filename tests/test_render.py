from __future__ import annotations

from pathlib import Path

from PIL import Image

from github_contrib_awtrix.grid import ContributionGrid
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


def test_dark_color_mode_uses_black_empty_cells(sample_grid: ContributionGrid) -> None:
    colors = frame_colors(sample_grid, color_mode="dark")

    assert colors[0][0] == "#000000"
    assert colors[0][1] == "#0e4429"
    assert colors[-1] == ["#000000"] * 32
