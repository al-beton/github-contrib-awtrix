from __future__ import annotations

import io
import json
from email.message import Message
from urllib.error import HTTPError

import pytest

from github_contrib_awtrix import awtrix
from github_contrib_awtrix.awtrix import AwtrixClient, AwtrixError, grid_payload
from github_contrib_awtrix.grid import ContributionGrid


def test_grid_payload_draws_32_by_8_frame(sample_grid: ContributionGrid) -> None:
    payload = grid_payload(sample_grid, duration_seconds=11)

    assert payload["save"] is False
    assert payload["noScroll"] is True
    assert payload["duration"] == 11
    command = payload["draw"][0]["db"]
    assert command[:4] == [0, 0, 32, 8]
    assert command[4][0] == 0xEBEDF0
    assert len(command[4]) == 256
    assert command[4][-32:] == [0] * 32


def test_install_app_posts_placeholder_payload(monkeypatch) -> None:
    payloads = []

    monkeypatch.setattr(
        AwtrixClient,
        "update_app",
        lambda _, app_name, payload: payloads.append((app_name, payload)),
    )

    AwtrixClient("http://awtrix.local").install_app("github", duration_seconds=13)

    assert payloads == [
        (
            "github",
            {
                "text": "GitHub ready",
                "center": True,
                "noScroll": True,
                "textCase": 2,
                "duration": 13,
                "save": False,
            },
        )
    ]


def test_update_app_posts_json_to_encoded_custom_app_name(monkeypatch) -> None:
    requests = []

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

        def read(self) -> bytes:
            return b'{"ok":true}'

    def fake_urlopen(request, timeout):
        requests.append((request, timeout))
        return FakeResponse()

    monkeypatch.setattr(awtrix, "urlopen", fake_urlopen)

    AwtrixClient("http://awtrix.local/").update_app("github graph", {"text": "ok"})

    request, timeout = requests[0]
    assert timeout == 10
    assert request.get_method() == "POST"
    assert request.full_url == "http://awtrix.local/api/custom?name=github+graph"
    assert json.loads(request.data.decode()) == {"text": "ok"}
    assert request.headers["Content-type"] == "application/json"


def test_uninstall_app_posts_empty_body(monkeypatch) -> None:
    requests = []

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

        def read(self) -> bytes:
            return b"OK"

    def fake_urlopen(request, timeout):
        requests.append(request)
        return FakeResponse()

    monkeypatch.setattr(awtrix, "urlopen", fake_urlopen)

    AwtrixClient("http://awtrix.local").uninstall_app("github_contribution_graph")

    request = requests[0]
    assert request.get_method() == "POST"
    assert request.full_url.endswith("/api/custom?name=github_contribution_graph")
    assert request.data is None


def test_http_error_includes_path_and_response_body(monkeypatch) -> None:
    def fake_urlopen(request, timeout):
        raise HTTPError(
            request.full_url,
            400,
            "Bad Request",
            Message(),
            io.BytesIO(b"bad payload"),
        )

    monkeypatch.setattr(awtrix, "urlopen", fake_urlopen)

    with pytest.raises(AwtrixError) as exc_info:
        AwtrixClient("http://awtrix.local").update_app("github", {"bad": True})

    message = str(exc_info.value)
    assert "POST /api/custom?name=github HTTP 400" in message
    assert "bad payload" in message
