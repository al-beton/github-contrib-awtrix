# AWTRIX Display Spec

## Purpose

Render the GitHub contribution grid as a 32 x 8 frame.

## Frame

- columns `x = 0..31` are weeks
- rows `y = 0..6` are GitHub contribution days
- row `y = 7` is blank/off
- older weeks appear on the left
- the current week appears on the right
- colors come from GitHub's returned `color`

## App Naming

- AWTRIX app id/name: `github_contribution_graph`
- human title: `GitHub Contribution Graph`

## Outputs

### Terminal

`--terminal` prints a 32 x 8 ANSI color preview.

### PNG

`--png <path>` writes a 32 x 8 preview image.

- default scale: 10x
- logical frame: 32 x 8
- default output size: 320 x 80

### AWTRIX

`--push` sends the 32 x 8 frame to AWTRIX over the local HTTP API.

`AWTRIX_URL` is required for `--push`.

`--awtrix-url` may override `AWTRIX_URL`.

Push happens after JSON, terminal, and PNG outputs. If AWTRIX is unreachable,
the command exits non-zero and prior outputs remain.

## Out Of Scope For V1

- MQTT requirement
- Home Assistant
- firmware changes
- public port forwarding
