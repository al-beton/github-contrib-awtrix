from __future__ import annotations

from typing import Literal

from github_contrib_awtrix.grid import ContributionDay

ColorMode = Literal["github", "dark", "matrix", "intense", "purple", "yellow"]

COLOR_MODES: tuple[ColorMode, ...] = (
    "github",
    "dark",
    "matrix",
    "intense",
    "purple",
    "yellow",
)

_DARK_PALETTE = {
    "NONE": "#000000",
    "FIRST_QUARTILE": "#002b12",
    "SECOND_QUARTILE": "#005f2a",
    "THIRD_QUARTILE": "#1f9d45",
    "FOURTH_QUARTILE": "#39d353",
}

_MATRIX_PALETTE = {
    "NONE": "#000000",
    "FIRST_QUARTILE": "#003b18",
    "SECOND_QUARTILE": "#007f32",
    "THIRD_QUARTILE": "#00c853",
    "FOURTH_QUARTILE": "#7cff6b",
}

_INTENSE_PALETTE = {
    "NONE": "#000000",
    "FIRST_QUARTILE": "#001f0c",
    "SECOND_QUARTILE": "#00a83b",
    "THIRD_QUARTILE": "#39ff14",
    "FOURTH_QUARTILE": "#b6ff00",
}

_PURPLE_PALETTE = {
    "NONE": "#000000",
    "FIRST_QUARTILE": "#1a0033",
    "SECOND_QUARTILE": "#4c148c",
    "THIRD_QUARTILE": "#9b4dff",
    "FOURTH_QUARTILE": "#e0b3ff",
}

_YELLOW_PALETTE = {
    "NONE": "#000000",
    "FIRST_QUARTILE": "#2b1800",
    "SECOND_QUARTILE": "#7a4300",
    "THIRD_QUARTILE": "#ffb000",
    "FOURTH_QUARTILE": "#fff36a",
}

_PALETTES = {
    "dark": _DARK_PALETTE,
    "matrix": _MATRIX_PALETTE,
    "intense": _INTENSE_PALETTE,
    "purple": _PURPLE_PALETTE,
    "yellow": _YELLOW_PALETTE,
}


def normalize_color_mode(value: str) -> ColorMode:
    if value == "github":
        return "github"
    if value == "dark":
        return "dark"
    if value == "matrix":
        return "matrix"
    if value == "intense":
        return "intense"
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
