from __future__ import annotations

from typing import Literal

from github_contrib_awtrix.grid import ContributionDay

ColorMode = Literal["github", "dark", "matrix"]

COLOR_MODES: tuple[ColorMode, ...] = ("github", "dark", "matrix")

_DARK_PALETTE = {
    "NONE": "#000000",
    "FIRST_QUARTILE": "#0e4429",
    "SECOND_QUARTILE": "#006d32",
    "THIRD_QUARTILE": "#26a641",
    "FOURTH_QUARTILE": "#39d353",
}

_MATRIX_PALETTE = {
    "NONE": "#000000",
    "FIRST_QUARTILE": "#003b18",
    "SECOND_QUARTILE": "#007f32",
    "THIRD_QUARTILE": "#00c853",
    "FOURTH_QUARTILE": "#7cff6b",
}

_PALETTES = {
    "dark": _DARK_PALETTE,
    "matrix": _MATRIX_PALETTE,
}


def normalize_color_mode(value: str) -> ColorMode:
    if value == "github":
        return "github"
    if value == "dark":
        return "dark"
    if value == "matrix":
        return "matrix"
    expected = ", ".join(COLOR_MODES)
    raise ValueError(f"unknown color mode {value!r}; expected one of: {expected}")


def contribution_color(day: ContributionDay, color_mode: ColorMode) -> str:
    if color_mode == "github":
        return day.color
    return _PALETTES[color_mode].get(day.contribution_level, day.color)
