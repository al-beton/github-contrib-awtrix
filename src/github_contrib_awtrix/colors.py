from __future__ import annotations

from typing import Literal

from github_contrib_awtrix.grid import ContributionDay

ColorMode = Literal["github", "matrix", "green", "purple", "yellow"]

COLOR_MODES: tuple[ColorMode, ...] = (
    "github",
    "matrix",
    "green",
    "purple",
    "yellow",
)

_GREEN_PALETTE = {
    "NONE": "#000000",
    "FIRST_QUARTILE": "#00240f",
    "SECOND_QUARTILE": "#007a2f",
    "THIRD_QUARTILE": "#30d158",
    "FOURTH_QUARTILE": "#ffffff",
}

_MATRIX_PALETTE = {
    "NONE": "#000000",
    "FIRST_QUARTILE": "#003b18",
    "SECOND_QUARTILE": "#007f32",
    "THIRD_QUARTILE": "#00c853",
    "FOURTH_QUARTILE": "#7cff6b",
}

_PURPLE_PALETTE = {
    "NONE": "#000000",
    "FIRST_QUARTILE": "#1a0033",
    "SECOND_QUARTILE": "#6d28d9",
    "THIRD_QUARTILE": "#c084fc",
    "FOURTH_QUARTILE": "#ffffff",
}

_YELLOW_PALETTE = {
    "NONE": "#000000",
    "FIRST_QUARTILE": "#2b1800",
    "SECOND_QUARTILE": "#9a5b00",
    "THIRD_QUARTILE": "#ffd60a",
    "FOURTH_QUARTILE": "#ffffff",
}

_PALETTES = {
    "green": _GREEN_PALETTE,
    "matrix": _MATRIX_PALETTE,
    "purple": _PURPLE_PALETTE,
    "yellow": _YELLOW_PALETTE,
}


def normalize_color_mode(value: str) -> ColorMode:
    if value == "github":
        return "github"
    if value == "matrix":
        return "matrix"
    if value == "green":
        return "green"
    if value == "purple":
        return "purple"
    if value == "yellow":
        return "yellow"
    expected = ", ".join(COLOR_MODES)
    raise ValueError(f"unknown color mode {value!r}; expected one of: {expected}")


def contribution_color(day: ContributionDay, color_mode: ColorMode) -> str:
    if color_mode == "github":
        return day.color
    return _PALETTES[color_mode].get(day.contribution_level, day.color)
