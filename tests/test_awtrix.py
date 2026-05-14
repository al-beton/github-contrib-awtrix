from __future__ import annotations

from github_contrib_awtrix.awtrix import grid_payload
from github_contrib_awtrix.grid import ContributionGrid


def test_grid_payload_draws_32_by_8_frame(sample_grid: ContributionGrid) -> None:
    payload = grid_payload(sample_grid)

    assert payload["save"] is False
    assert payload["noScroll"] is True
    command = payload["draw"][0]["db"]
    assert command[:4] == [0, 0, 32, 8]
    assert command[4][0] == 0xEBEDF0
    assert len(command[4]) == 256
    assert command[4][-32:] == [0] * 32
