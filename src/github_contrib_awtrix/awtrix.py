from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from github_contrib_awtrix.grid import ContributionGrid
from github_contrib_awtrix.render import FRAME_HEIGHT, FRAME_WIDTH, frame_colors


class AwtrixError(RuntimeError):
    pass


@dataclass(frozen=True)
class AwtrixClient:
    base_url: str

    def get_stats(self) -> dict[str, Any]:
        return self._request_json("GET", "/api/stats")

    def install_app(self, app_name: str) -> None:
        payload = {
            "text": "GitHub ready",
            "center": True,
            "noScroll": True,
            "textCase": 2,
            "save": False,
        }
        self.update_app(app_name, payload)

    def push_grid(self, app_name: str, grid: ContributionGrid) -> None:
        self.update_app(app_name, grid_payload(grid))

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
            raise AwtrixError(f"AWTRIX request failed: HTTP {exc.code}") from exc
        except URLError as exc:
            raise AwtrixError(f"AWTRIX request failed: {exc.reason}") from exc

        if not raw:
            return {}
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {"response": raw}
        if isinstance(parsed, dict):
            return parsed
        return {"response": parsed}


def grid_payload(grid: ContributionGrid) -> dict[str, Any]:
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
                        for row in frame_colors(grid)
                        for color in row
                    ],
                ]
            }
        ],
        "duration": 7,
        "noScroll": True,
        "save": False,
    }


def _hex_to_rgb888(color: str) -> int:
    clean = color.removeprefix("#")
    if len(clean) != 6:
        raise ValueError(f"expected 6-digit hex color, got {color!r}")
    return int(clean, 16)
