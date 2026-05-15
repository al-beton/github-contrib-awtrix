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
- `blue`: black empty cells with a blue-to-white scale
- `orange`: black empty cells with an orange-to-white scale

`GITHUB_CONTRIB_COLOR_MODE` sets the default.

`--color-mode` overrides it for `push`.

## Velocity Overlay

Velocity is an optional same-page overlay. It does not create a second AWTRIX
CustomApp page.

`GITHUB_CONTRIB_VELOCITY=true` enables it by default.

`push --velocity` enables it for one run.

`push --no-velocity` disables it for one run.

The metric is average commits per day over the visible real-day period:

```text
velocity_per_day = total_visible_commits / visible_real_days
```

Future padding cells in the current week do not count as visible real days.

The overlay uses compact `/d` formatting:

```text
0/d
0.4/d
12/d
999/d
1.2k/d
10k/d
1.2M/d
1B/d
1.2T/d
```

The value is drawn with a tiny fixed pixel font over the bottom-left of the
32 x 8 frame.

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
frame. When velocity is enabled, the overlay is drawn into the same frame before
the payload is sent.

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

## Out Of Scope

- MQTT requirement
- Home Assistant
- firmware changes
- public port forwarding
