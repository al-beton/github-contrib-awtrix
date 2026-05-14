from __future__ import annotations

import argparse
from collections.abc import Sequence


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

    parser.error("outputs are specified in the spec but not implemented yet")


if __name__ == "__main__":
    raise SystemExit(main())
