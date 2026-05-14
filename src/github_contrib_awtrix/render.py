from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from github_contrib_awtrix.colors import ColorMode, contribution_color
from github_contrib_awtrix.grid import ContributionDay, ContributionGrid
from github_contrib_awtrix.velocity import VELOCITY_COLOR, velocity_label

FRAME_WIDTH = 32
FRAME_HEIGHT = 8
PNG_SCALE = 10
BLANK_COLOR = "#000000"


def render_terminal(
    grid: ContributionGrid,
    *,
    color_mode: ColorMode = "github",
    velocity: bool = False,
) -> str:
    lines: list[str] = []
    for row in frame_colors(grid, color_mode=color_mode, velocity=velocity):
        parts: list[str] = []
        for color in row:
            red, green, blue = _hex_to_rgb(color)
            parts.append(f"\033[48;2;{red};{green};{blue}m  \033[0m")
        lines.append("".join(parts))
    return "\n".join(lines)


def write_png(
    grid: ContributionGrid,
    path: Path,
    *,
    scale: int = PNG_SCALE,
    color_mode: ColorMode = "github",
    velocity: bool = False,
) -> None:
    image = Image.new("RGB", (FRAME_WIDTH * scale, FRAME_HEIGHT * scale), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    for row, colors in enumerate(
        frame_colors(grid, color_mode=color_mode, velocity=velocity)
    ):
        for column, color_hex in enumerate(colors):
            color = _hex_to_rgb(color_hex)
            x = column * scale
            y = row * scale
            draw.rectangle((x, y, x + scale - 1, y + scale - 1), fill=color)

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def frame_colors(
    grid: ContributionGrid,
    *,
    color_mode: ColorMode = "github",
    velocity: bool = False,
) -> list[list[str]]:
    frame = [
        [
            _cell_color(grid.weeks[column], row, color_mode=color_mode)
            for column in range(FRAME_WIDTH)
        ]
        for row in range(FRAME_HEIGHT)
    ]
    if velocity:
        _draw_text(frame, 0, FRAME_HEIGHT - FONT_HEIGHT, velocity_label(grid))
    return frame


def _cell_color(
    week: list[ContributionDay],
    row: int,
    *,
    color_mode: ColorMode,
) -> str:
    if row >= 7:
        return BLANK_COLOR
    return contribution_color(week[row], color_mode)


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    clean = color.removeprefix("#")
    if len(clean) != 6:
        raise ValueError(f"expected 6-digit hex color, got {color!r}")
    return (
        int(clean[0:2], 16),
        int(clean[2:4], 16),
        int(clean[4:6], 16),
    )


FONT_HEIGHT = 5

_FONT: dict[str, tuple[str, ...]] = {
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("111", "001", "111", "100", "111"),
    "3": ("111", "001", "111", "001", "111"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "111", "001", "111"),
    "6": ("111", "100", "111", "101", "111"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("111", "101", "111", "101", "111"),
    "9": ("111", "101", "111", "001", "111"),
    ".": ("0", "0", "0", "0", "1"),
    "/": ("001", "001", "010", "100", "100"),
    "d": ("001", "001", "111", "101", "111"),
    "k": ("101", "101", "110", "101", "101"),
    "M": ("101", "111", "111", "101", "101"),
}

_ADVANCE = {
    ".": 2,
}


def _draw_text(
    frame: list[list[str]],
    start_column: int,
    start_row: int,
    text: str,
) -> None:
    column = start_column
    for char in text:
        glyph = _FONT.get(char)
        if glyph is None:
            column += 4
            continue
        for y, glyph_row in enumerate(glyph):
            for x, pixel in enumerate(glyph_row):
                target_column = column + x
                target_row = start_row + y
                if (
                    pixel == "1"
                    and 0 <= target_row < FRAME_HEIGHT
                    and 0 <= target_column < FRAME_WIDTH
                ):
                    frame[target_row][target_column] = VELOCITY_COLOR
        column += _ADVANCE.get(char, len(glyph[0]) + 1)
