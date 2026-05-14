# GitHub Data Spec

## Purpose

Fetch one GitHub login's contribution calendar and turn it into 32 weeks of
grid data.

## Inputs

- `GITHUB_TOKEN`
- `GITHUB_LOGIN`
- local machine date

CLI flags may override `.env` values.

Overrides:

- `--token`
- `--login`

## Source Of Truth

Use GitHub GraphQL's contribution calendar.

Use GitHub's returned week/day structure and day fields:

- `date`
- `weekday`
- `contributionCount`
- `contributionLevel`
- `color`

Do not compute custom colors in v1.

## Window

- request the last 32 weeks ending today
- "today" means the local machine date
- use GitHub's returned week columns and day rows

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
- org aggregation
- custom intensity mapping
- GitHub webhooks
- OAuth
