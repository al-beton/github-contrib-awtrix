# github-contrib-awtrix

Show a GitHub contribution graph on an AWTRIX/Ulanzi display.

`github-contrib-awtrix` is a small Python CLI for rendering GitHub contribution
and commit activity grids onto an AWTRIX/Ulanzi display. It can push one graph on
demand, write terminal/PNG previews, or refresh a local rotation of AWTRIX
CustomApps from a TOML config.

![AWTRIX display showing GitHub contribution activity on a desk](docs/assets/awtrix-desk-demo.jpg)

![PNG preview of a GitHub contribution grid rendered for AWTRIX](docs/assets/github-contrib-awtrix-preview.png)

## What It Supports

- GitHub profile contribution calendars
- commit-search activity for one author email, org, repo, or author within an org/repo
- multi-app local refresh from a private TOML config
- last 32 weeks ending today, using the local machine date
- 32 x 8 visual frame for terminal, PNG, and AWTRIX output
- GitHub-like and custom color palettes
- optional velocity overlay

Profile mode uses GitHub's contribution calendar. Commit-search mode is
commit-only; it is useful for bots, agents, repos, and org-wide activity, but it
is not the same data product as a GitHub profile graph.

## Install

From the repo:

```bash
uv sync
uv run github-contrib-awtrix --help
```

## Config

`.env` provides defaults. CLI flags override `.env`.

```env
GITHUB_TOKEN=...
GITHUB_LOGIN=octocat
AWTRIX_URL=http://awtrix_xxxxxx.local
AWTRIX_APP_NAME=github_contribution_graph
AWTRIX_APP_DURATION=7
GITHUB_CONTRIB_COLOR_MODE=github
GITHUB_CONTRIB_VELOCITY=false
```

Overrides are command-specific and must appear after the subcommand:

```text
doctor: --token, --login, --awtrix-url, --awtrix-app-name, --awtrix-app-duration
install: --awtrix-url, --awtrix-app-name, --awtrix-app-duration
push: --source, --org, --repo, --author-email, --token, --login, --awtrix-url, --awtrix-app-name, --awtrix-app-duration, --color-mode, --velocity, --no-velocity
refresh: --config, --token, --awtrix-url, --awtrix-app-duration
uninstall: --awtrix-url, --awtrix-app-name
```

## Command Shape

No command prints help and does nothing.

```bash
uv run github-contrib-awtrix doctor
uv run github-contrib-awtrix install
uv run github-contrib-awtrix push \
  --color-mode green \
  --velocity \
  --json out/grid.json \
  --terminal \
  --png out/preview.png
uv run github-contrib-awtrix push \
  --source commit-search \
  --author-email bot@example.com \
  --color-mode purple
uv run github-contrib-awtrix push \
  --source commit-search \
  --org OWNER \
  --color-mode purple
uv run github-contrib-awtrix refresh \
  --config ~/.config/github-contrib-awtrix/rotation.toml
uv run github-contrib-awtrix uninstall
```

AWTRIX CustomApps are named pages in the device rotation. There is no on-device
code to install. `install` creates the named page with a placeholder; `push`
updates that page with the current contribution grid.

`push` fetches once, then renders each requested output from the same data.

`refresh` reads a TOML config and updates multiple AWTRIX CustomApps in order.
It is useful for local scheduled refresh via LaunchD. See
[local refresh docs](docs/local-refresh.md).

Sources:

- `profile`: the default; uses `GITHUB_LOGIN` and GitHub's profile contribution calendar
- `commit-search`: counts commits visible to the token using at least one of `--author-email`, `--org`, or `--repo`

`commit-search` can count a whole visible org with `--org OWNER`, one repo with
`--repo OWNER/REPO`, one author with `--author-email EMAIL`, or an author inside
an org/repo by combining `--author-email` with one scope. `--org` and `--repo`
cannot be used together.

`commit-search` is a commit activity calendar. It does not include GitHub
profile-only activity such as issue/PR authorship, reviews, discussions,
co-authors, or team rollups.

Color modes:

- `github`: GitHub's returned colors
- `matrix`: black empty cells with brighter matrix greens
- `green`: black empty cells with a green-to-white scale
- `purple`: black empty cells with a purple-to-white scale
- `yellow`: black empty cells with an amber/yellow-to-white scale
- `blue`: black empty cells with a blue-to-white scale
- `orange`: black empty cells with an orange-to-white scale

Velocity overlay:

- off by default
- enabled with `GITHUB_CONTRIB_VELOCITY=true` or `push --velocity`
- disabled for a command with `push --no-velocity`
- displays average commits per day over the visible real days
- draws the compact value, such as `0.4/d`, `12/d`, `1.2k/d`, or `1.2M/d`, over the bottom-left of the grid
- promotes cleanly across large suffixes: `999/d`, `1k/d`, `999k/d`, `1M/d`, `1B/d`
- applies to terminal, PNG, and AWTRIX output

## Outputs

- `push --json` writes 32 x 7 contribution data to stdout
- `push --json <path>` writes 32 x 7 contribution data to a file
- `push --terminal` prints a 32 x 8 ANSI color preview
- `push --png <path>` writes a 32 x 8 PNG preview at 10x scale; path is required
- `push` sends the 32 x 8 frame to AWTRIX over local HTTP

The preview flags currently belong to `push`, so the command still requires
`AWTRIX_URL` and updates the AWTRIX CustomApp after writing previews.

Output order is:

```text
json -> terminal -> png -> AWTRIX
```

If one output fails, the command exits non-zero. Already-written outputs are not
rolled back.

## Implementation

- Python
- typed code
- `uv`
- `ruff`
- `ty`
- `pytest`
- small dependency set

## Docs

- [Docs index](docs/README.md)
- [Local scheduled refresh](docs/local-refresh.md)
- [GitHub data spec](docs/specs/local-service.md)
- [AWTRIX display spec](docs/specs/awtrix-display.md)
