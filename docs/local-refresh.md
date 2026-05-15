# Local Refresh

`refresh` updates several AWTRIX CustomApps from one TOML config. It is intended
for a private machine-local setup where secrets stay in `.env` or environment
variables.

## Config

Create a private config outside the repo:

```bash
mkdir -p ~/.config/github-contrib-awtrix
cp examples/rotation.toml ~/.config/github-contrib-awtrix/rotation.toml
```

Edit the app entries for your own rotation:

```toml
[[apps]]
app_name = "github_green"
source = "profile"
login = "octocat"
color_mode = "green"
velocity = true

[[apps]]
app_name = "github_purple"
source = "commit-search"
org = "example-org"
color_mode = "purple"
velocity = true
```

Supported fields:

- `app_name`: AWTRIX CustomApp name
- `source`: `profile` or `commit-search`; defaults to `profile`
- `login`: GitHub login for `profile`
- `org`: GitHub org for `commit-search`
- `repo`: `OWNER/REPO` for `commit-search`
- `author_email`: exact commit author email for `commit-search`
- `color_mode`: one of the supported display palettes
- `velocity`: `true` or `false`
- `awtrix_app_duration`: optional per-app duration in seconds

`profile` requires `login`. `commit-search` requires at least one of
`author_email`, `org`, or `repo`. `org` and `repo` cannot be combined.

Secrets and device config still come from `.env` or environment variables:

```env
GITHUB_TOKEN=...
AWTRIX_URL=http://awtrix_xxxxxx.local
AWTRIX_APP_DURATION=7
```

## Manual Run

From the repo:

```bash
uv run github-contrib-awtrix refresh \
  --config ~/.config/github-contrib-awtrix/rotation.toml
```

The command refreshes each app in order and exits. If one app fails, the command
exits non-zero so scheduled logs show the problem.

## LaunchD

The example plist runs hourly:

```text
examples/launchd/com.example.github-contrib-awtrix.refresh.plist
```

Copy it into your LaunchAgents folder and edit the placeholder paths:

```bash
cp examples/launchd/com.example.github-contrib-awtrix.refresh.plist \
  ~/Library/LaunchAgents/com.example.github-contrib-awtrix.refresh.plist
```

Update:

- `WorkingDirectory`
- `--config` path
- log paths
- label, if desired

Load it:

```bash
launchctl load ~/Library/LaunchAgents/com.example.github-contrib-awtrix.refresh.plist
```

Run once immediately:

```bash
launchctl start com.example.github-contrib-awtrix.refresh
```

Logs go to the `StandardOutPath` / `StandardErrorPath` set in the plist.

To change frequency, edit `StartInterval`. The repo example uses `3600`
seconds, which is hourly.
