from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from github_contrib_awtrix.config import resolve_config
from github_contrib_awtrix.github import GitHubError, fetch_contribution_grid
from github_contrib_awtrix.render import render_terminal, write_png


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="github-contrib-awtrix",
        description="Show a GitHub contribution graph on an AWTRIX/Ulanzi display.",
    )
    parser.add_argument(
        "--json",
        nargs="?",
        const="-",
        metavar="PATH",
        help="Write 32 x 7 contribution data. Without PATH, write to stdout.",
    )
    parser.add_argument(
        "--terminal",
        action="store_true",
        help="Print a 32 x 8 ANSI color preview.",
    )
    parser.add_argument(
        "--png",
        metavar="PATH",
        help="Write a 32 x 8 PNG preview at 10x scale.",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Send the 32 x 8 frame to AWTRIX over local HTTP.",
    )
    parser.add_argument("--token", help="Override GITHUB_TOKEN.")
    parser.add_argument("--login", help="Override GITHUB_LOGIN.")
    parser.add_argument("--awtrix-url", help="Override AWTRIX_URL.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not any((args.json, args.terminal, args.png, args.push)):
        parser.print_help()
        return 0

    if args.push and not any((args.json, args.terminal, args.png)):
        parser.error("--push is specified in the spec but not implemented yet")

    try:
        config = resolve_config(
            token=args.token,
            login=args.login,
            awtrix_url=args.awtrix_url,
        )
        grid = fetch_contribution_grid(token=config.token, login=config.login)

        if args.json:
            json_output = json.dumps(grid.to_json(), indent=2)
            if args.json == "-":
                print(json_output)
            else:
                json_path = Path(args.json)
                json_path.parent.mkdir(parents=True, exist_ok=True)
                json_path.write_text(f"{json_output}\n")

        if args.terminal:
            print(render_terminal(grid))

        if args.png:
            write_png(grid, Path(args.png))

        if args.push:
            parser.error("--push is specified in the spec but not implemented yet")

    except (GitHubError, OSError, ValueError) as exc:
        parser.exit(1, f"{parser.prog}: error: {exc}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
