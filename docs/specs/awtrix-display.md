# AWTRIX Display Spec

## Purpose

Render the GitHub contribution grid as a 32 x 8 frame.

## Frame

- columns `x = 0..31` are weeks
- rows `y = 0..6` are GitHub contribution days
- row `y = 7` is blank/off
- older weeks appear on the left
- the current week appears on the right
- JSON keeps GitHub's returned `color`
- terminal, PNG, and AWTRIX output use the selected color mode

## Color Modes

- `github`: GitHub's returned colors
- `matrix`: black empty cells with brighter matrix greens
- `green`: black empty cells with a green-to-white scale
- `purple`: black empty cells with a purple-to-white scale
- `yellow`: black empty cells with an amber/yellow-to-white scale

`GITHUB_CONTRIB_COLOR_MODE` sets the default.

`--color-mode` overrides it for `push`.

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

AWTRIX CustomApps are named pages in the app rotation. They do not run code on
the device.

`install` creates the page by posting a placeholder payload to:

```text
/api/custom?name=github_contribution_graph
```

`push` updates the same page with drawing instructions for the current 32 x 8
frame.

`uninstall` removes the page by sending an empty payload to the same endpoint.

`AWTRIX_URL` is required for `doctor`, `install`, `push`, and `uninstall`.

`--awtrix-url` may override `AWTRIX_URL`.

`--awtrix-app-name` may override `AWTRIX_APP_NAME`.

`AWTRIX_APP_DURATION` controls the app duration in seconds. It defaults to `7`.

`--awtrix-app-duration` may override `AWTRIX_APP_DURATION`.

The CLI does not save the app to flash by default. A scheduled `push` recreates
or refreshes the page when needed.

Push happens after JSON, terminal, and PNG outputs. If AWTRIX is unreachable, the
command exits non-zero and prior outputs remain.

## Out Of Scope For V1

- MQTT requirement
- Home Assistant
- firmware changes
- public port forwarding
