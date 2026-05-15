# GitHub Data Spec

## Purpose

Fetch GitHub activity and turn it into 32 weeks of grid data.

## Inputs

- `GITHUB_TOKEN`
- `GITHUB_LOGIN` for profile mode
- at least one of `--author-email EMAIL`, `--org OWNER`, or `--repo OWNER/REPO` for commit-search mode
- local machine date

CLI flags may override `.env` values.

Overrides:

- `--token`
- `--login`
- `--source`
- `--org`
- `--repo`
- `--author-email`

## Source Of Truth

Profile mode uses GitHub GraphQL's contribution calendar. GitHub's GraphQL API
requires an authenticated request, even when the visible profile data is public.

Use GitHub's returned week/day structure and day fields:

- `date`
- `weekday`
- `contributionCount`
- `contributionLevel`
- `color`

Commit-search mode uses GitHub commit search. It counts commits visible to the
token using at least one filter:

- `--author-email EMAIL`: exact primary commit author email
- `--org OWNER`: all visible commits in one org
- `--repo OWNER/REPO`: all visible commits in one repo

`--author-email` can be combined with `--org` or `--repo`. `--org` and `--repo`
are mutually exclusive.

Commit-search mode computes contribution levels from the visible window so it can
reuse the same renderers as profile mode.

## Window

- request the last 32 weeks ending today
- "today" means the local machine date
- profile mode uses GitHub's returned week columns and day rows
- commit-search mode uses GitHub-style Sunday-start week columns

## JSON Output

JSON contains contribution data only:

- 32 week columns
- 7 day rows per week
- no AWTRIX-only eighth row

`--json` without a path writes to stdout. `--json <path>` writes to a file.

Shape:

```text
grid[week][day]
```

Each cell includes:

- `date`
- `weekday`
- `contributionCount`
- `contributionLevel`
- `color`

## Out Of Scope For V1

- teams
- co-author counting
- search result sets larger than GitHub's commit search cap
- GitHub webhooks
- OAuth
