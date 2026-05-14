# github-contrib-awtrix

Show a GitHub contribution graph on an AWTRIX/Ulanzi display.

V1 is a Python CLI that runs once and exits. It can be run manually or scheduled
with cron/launchd later.

## V1

- one GitHub login, or one exact commit author email
- last 32 weeks ending today, using the local machine date
- GitHub GraphQL contribution calendar as the data source
- GitHub commit search as the bot/agent commit data source
- 32 x 8 visual frame for terminal, PNG, and AWTRIX output
- blank/off eighth row

## Config

`.env` provides defaults. CLI flags override `.env`.

```env
GITHUB_TOKEN=...
GITHUB_LOGIN=al-beton
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
uninstall: --awtrix-url, --awtrix-app-name
```

## Command Shape

No command prints help and does nothing.

```bash
github-contrib-awtrix doctor
github-contrib-awtrix install
github-contrib-awtrix push \
  --color-mode green \
  --velocity \
  --json out/grid.json \
  --terminal \
  --png out/preview.png
github-contrib-awtrix push \
  --source commit-search \
  --author-email bot@example.com \
  --color-mode purple
github-contrib-awtrix push \
  --source commit-search \
  --org OWNER \
  --author-email bot@example.com \
  --color-mode purple
github-contrib-awtrix uninstall
```

AWTRIX CustomApps are named pages in the device rotation. There is no on-device
code to install. `install` creates the named page with a placeholder; `push`
updates that page with the current contribution grid.

`push` fetches once, then renders each requested output from the same data.

Sources:

- `profile`: the default; uses `GITHUB_LOGIN` and GitHub's profile contribution calendar
- `commit-search`: uses `--author-email EMAIL` to count matching primary commit authors across commits visible to the token

`commit-search` can be narrowed with `--org OWNER` or `--repo OWNER/REPO`, but
both are optional. `--org` and `--repo` cannot be used together.

`commit-search` is a commit activity calendar. It is not GitHub's profile
contribution calendar and does not include co-authors, PR authorship, other
branches, or team rollups.

Color modes:

- `github`: GitHub's returned colors
- `matrix`: black empty cells with brighter matrix greens
- `green`: black empty cells with a green-to-white scale
- `purple`: black empty cells with a purple-to-white scale
- `yellow`: black empty cells with an amber/yellow-to-white scale

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
- [GitHub data spec](docs/specs/local-service.md)
- [AWTRIX display spec](docs/specs/awtrix-display.md)
