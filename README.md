# github-contrib-awtrix

Show a GitHub contribution graph on an AWTRIX/Ulanzi display.

V1 is a Python CLI that runs once and exits. It can be run manually or scheduled
with cron/launchd later.

## V1

- one GitHub login
- last 32 weeks ending today, using the local machine date
- GitHub GraphQL contribution calendar as the data source
- GitHub's returned colors
- 32 x 8 visual frame for terminal, PNG, and AWTRIX output
- blank/off eighth row

## Config

`.env` provides defaults. CLI flags override `.env`.

```env
GITHUB_TOKEN=...
GITHUB_LOGIN=al-beton
AWTRIX_URL=http://awtrix_4c7100.local
```

Overrides:

```text
--token
--login
--awtrix-url
```

## Command Shape

No flags prints help and does nothing.

```bash
github-contrib-awtrix \
  --json out/grid.json \
  --terminal \
  --png out/preview.png \
  --push
```

Outputs can be combined in one run. The command fetches once, then renders each
requested output from the same data.

## Outputs

- `--json` writes 32 x 7 contribution data to stdout
- `--json <path>` writes 32 x 7 contribution data to a file
- `--terminal` prints a 32 x 8 ANSI color preview
- `--png <path>` writes a 32 x 8 PNG preview at 10x scale; path is required
- `--push` sends the 32 x 8 frame to AWTRIX over local HTTP

Output order is:

```text
json -> terminal -> png -> push
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
