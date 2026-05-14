from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from github_contrib_awtrix.grid import ContributionDay, ContributionGrid

FRAME_WIDTH = 32
FRAME_HEIGHT = 8
PNG_SCALE = 10
BLANK_COLOR = "#000000"


def render_terminal(grid: ContributionGrid) -> str:
    lines: list[str] = []
    for row in range(FRAME_HEIGHT):
        parts: list[str] = []
        for column in range(FRAME_WIDTH):
            color = _cell_color(grid.weeks[column], row)
            red, green, blue = _hex_to_rgb(color)
            parts.append(f"\033[48;2;{red};{green};{blue}m  \033[0m")
        lines.append("".join(parts))
    return "\n".join(lines)


def write_png(grid: ContributionGrid, path: Path, *, scale: int = PNG_SCALE) -> None:
    image = Image.new("RGB", (FRAME_WIDTH * scale, FRAME_HEIGHT * scale), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    for row in range(FRAME_HEIGHT):
        for column in range(FRAME_WIDTH):
            color = _hex_to_rgb(_cell_color(grid.weeks[column], row))
            x = column * scale
            y = row * scale
            draw.rectangle((x, y, x + scale - 1, y + scale - 1), fill=color)

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def _cell_color(week: list[ContributionDay], row: int) -> str:
    if row >= 7:
        return BLANK_COLOR
    return week[row].color


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    clean = color.removeprefix("#")
    if len(clean) != 6:
        raise ValueError(f"expected 6-digit hex color, got {color!r}")
    return (
        int(clean[0:2], 16),
        int(clean[2:4], 16),
        int(clean[4:6], 16),
    )
