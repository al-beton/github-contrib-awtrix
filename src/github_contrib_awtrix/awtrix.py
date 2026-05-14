from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from github_contrib_awtrix.colors import ColorMode
from github_contrib_awtrix.defaults import DEFAULT_AWTRIX_APP_DURATION
from github_contrib_awtrix.grid import ContributionGrid
from github_contrib_awtrix.render import FRAME_HEIGHT, FRAME_WIDTH, frame_colors

DEFAULT_APP_DURATION_SECONDS = DEFAULT_AWTRIX_APP_DURATION


class AwtrixError(RuntimeError):
    pass


@dataclass(frozen=True)
class AwtrixClient:
    base_url: str

    def get_stats(self) -> dict[str, Any]:
        return self._request_json("GET", "/api/stats")

    def install_app(
        self,
        app_name: str,
        *,
        duration_seconds: int = DEFAULT_APP_DURATION_SECONDS,
    ) -> None:
        payload = {
            "text": "GitHub ready",
            "center": True,
            "noScroll": True,
            "textCase": 2,
            "duration": duration_seconds,
            "save": False,
        }
        self.update_app(app_name, payload)

    def push_grid(
        self,
        app_name: str,
        grid: ContributionGrid,
        *,
        duration_seconds: int = DEFAULT_APP_DURATION_SECONDS,
        color_mode: ColorMode = "github",
        velocity: bool = False,
    ) -> None:
        self.update_app(
            app_name,
            grid_payload(
                grid,
                duration_seconds=duration_seconds,
                color_mode=color_mode,
                velocity=velocity,
            ),
        )

    def update_app(self, app_name: str, payload: dict[str, Any]) -> None:
        path = f"/api/custom?{urlencode({'name': app_name})}"
        self._request_json("POST", path, payload)

    def uninstall_app(self, app_name: str) -> None:
        path = f"/api/custom?{urlencode({'name': app_name})}"
        self._request_json("POST", path, None)

    def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}{path}"
        body = None if payload is None else json.dumps(payload).encode()
        headers = {"Content-Type": "application/json"} if payload is not None else {}
        request = Request(url, data=body, headers=headers, method=method)

        try:
            with urlopen(request, timeout=10) as response:
                raw = response.read().decode()
        except HTTPError as exc:
            detail = _read_error_detail(exc)
            message = f"AWTRIX request failed: {method} {path} HTTP {exc.code}"
            if detail:
                message = f"{message}: {detail}"
            raise AwtrixError(message) from exc
        except URLError as exc:
            raise AwtrixError(
                f"AWTRIX request failed: {method} {path}: {exc.reason}"
            ) from exc

        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {"response": raw}
        if isinstance(parsed, dict):
            return parsed
        return {"response": parsed}


def grid_payload(
    grid: ContributionGrid,
    *,
    duration_seconds: int = DEFAULT_APP_DURATION_SECONDS,
    color_mode: ColorMode = "github",
    velocity: bool = False,
) -> dict[str, Any]:
    return {
        "draw": [
            {
                "db": [
                    0,
                    0,
                    FRAME_WIDTH,
                    FRAME_HEIGHT,
                    [
                        _hex_to_rgb888(color)
                        for row in frame_colors(
                            grid,
                            color_mode=color_mode,
                            velocity=velocity,
                        )
                        for color in row
                    ],
                ]
            }
        ],
        "duration": duration_seconds,
        "noScroll": True,
        "save": False,
    }


def _read_error_detail(exc: HTTPError) -> str:
    if exc.fp is None:
        return ""
    return exc.fp.read().decode(errors="replace").strip()


def _hex_to_rgb888(color: str) -> int:
    clean = color.removeprefix("#")
    if len(clean) != 6:
        raise ValueError(f"expected 6-digit hex color, got {color!r}")
    return int(clean, 16)
