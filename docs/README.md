# Docs

Project docs for `github-contrib-awtrix`.

## Specs

- [Local scheduled refresh](local-refresh.md)
- [GitHub data](specs/local-service.md)
- [AWTRIX display](specs/awtrix-display.md)

## V1 Shape

1. Fetch a GitHub profile calendar or commit-search activity slice.
2. Convert it into a 32-week contribution grid.
3. Render JSON, terminal, PNG, and/or AWTRIX outputs.
4. Optionally refresh several AWTRIX CustomApps from a private local config.

Hosted service, OAuth, browser UI, Home Assistant, and firmware changes are out
of scope for v1.
