from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path

from github_contrib_awtrix.awtrix import AwtrixClient, AwtrixError
from github_contrib_awtrix.colors import COLOR_MODES, ColorMode
from github_contrib_awtrix.commit_search import fetch_commit_search_grid
from github_contrib_awtrix.config import resolve_config
from github_contrib_awtrix.github import GitHubError, fetch_contribution_grid
from github_contrib_awtrix.grid import ContributionGrid
from github_contrib_awtrix.render import render_terminal, write_png


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="github-contrib-awtrix",
        description="Show a GitHub contribution graph on an AWTRIX/Ulanzi display.",
    )

    subparsers = parser.add_subparsers(dest="command")

    doctor = subparsers.add_parser("doctor", help="Check GitHub and AWTRIX config.")
    _add_common_config_args(doctor)

    install = subparsers.add_parser("install", help="Create the AWTRIX CustomApp page.")
    _add_awtrix_args(install)

    push = subparsers.add_parser("push", help="Fetch GitHub data and update AWTRIX.")
    _add_output_args(push)
    _add_source_args(push)
    _add_common_config_args(push)

    uninstall = subparsers.add_parser(
        "uninstall",
        help="Remove the AWTRIX CustomApp page.",
    )
    _add_awtrix_identity_args(uninstall)

    return parser


def _add_output_args(parser: argparse.ArgumentParser) -> None:
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
        "--color-mode",
        choices=COLOR_MODES,
        help="Palette for terminal, PNG, and AWTRIX output.",
    )
    parser.add_argument(
        "--velocity",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Overlay average commits per day on terminal, PNG, and AWTRIX output.",
    )


def _add_github_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--token", help="Override GITHUB_TOKEN.")
    parser.add_argument("--login", help="Override GITHUB_LOGIN.")


def _add_source_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--source",
        choices=("profile", "commit-search"),
        default="profile",
        help="Data source. Defaults to GitHub profile contribution calendar.",
    )
    parser.add_argument(
        "--org",
        help="Optional organization narrowing filter for --source commit-search.",
    )
    parser.add_argument(
        "--repo",
        help="Optional OWNER/REPO narrowing filter for --source commit-search.",
    )
    parser.add_argument(
        "--author-email",
        help="Exact primary commit author email for --source commit-search.",
    )


def _add_awtrix_args(parser: argparse.ArgumentParser) -> None:
    _add_awtrix_identity_args(parser)
    parser.add_argument(
        "--awtrix-app-duration",
        help="Override AWTRIX_APP_DURATION in seconds.",
    )


def _add_awtrix_identity_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--awtrix-url", help="Override AWTRIX_URL.")
    parser.add_argument("--awtrix-app-name", help="Override AWTRIX_APP_NAME.")


def _add_common_config_args(parser: argparse.ArgumentParser) -> None:
    _add_github_args(parser)
    _add_awtrix_args(parser)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    try:
        if args.command == "doctor":
            _doctor(args)
        elif args.command == "install":
            _install(args)
        elif args.command == "push":
            _push(args)
        elif args.command == "uninstall":
            _uninstall(args)
        else:
            parser.error(f"unknown command: {args.command}")

    except (AwtrixError, GitHubError, OSError, ValueError) as exc:
        parser.exit(1, f"{parser.prog}: error: {exc}\n")

    return 0


def _doctor(args: argparse.Namespace) -> None:
    config = resolve_config(
        token=args.token,
        login=args.login,
        awtrix_url=args.awtrix_url,
        awtrix_app_name=args.awtrix_app_name,
        awtrix_app_duration=args.awtrix_app_duration,
        require_awtrix=True,
    )
    if config.token is None or config.login is None or config.awtrix_url is None:
        raise ValueError("missing required config")

    fetch_contribution_grid(token=config.token, login=config.login)
    stats = AwtrixClient(config.awtrix_url).get_stats()
    app = stats.get("app", "unknown")
    print(f"GitHub OK for {config.login}")
    print(f"AWTRIX OK at {config.awtrix_url} (current app: {app})")


def _install(args: argparse.Namespace) -> None:
    config = resolve_config(
        awtrix_url=args.awtrix_url,
        awtrix_app_name=args.awtrix_app_name,
        awtrix_app_duration=args.awtrix_app_duration,
        require_github=False,
        require_awtrix=True,
    )
    if config.awtrix_url is None:
        raise ValueError("missing required config: AWTRIX_URL")

    AwtrixClient(config.awtrix_url).install_app(
        config.awtrix_app_name,
        duration_seconds=config.awtrix_app_duration,
    )
    print(f"Installed AWTRIX CustomApp {config.awtrix_app_name}", file=sys.stderr)


def _push(args: argparse.Namespace) -> None:
    config = resolve_config(
        token=args.token,
        login=args.login,
        awtrix_url=args.awtrix_url,
        awtrix_app_name=args.awtrix_app_name,
        awtrix_app_duration=args.awtrix_app_duration,
        color_mode=args.color_mode,
        velocity=args.velocity,
        require_github=False,
        require_awtrix=True,
    )
    if config.token is None:
        raise ValueError("missing required config: GITHUB_TOKEN")
    if config.awtrix_url is None:
        raise ValueError("missing required config: AWTRIX_URL")

    grid = _fetch_grid_for_source(args, token=config.token, login=config.login)
    _write_outputs(args, grid, color_mode=config.color_mode, velocity=config.velocity)
    AwtrixClient(config.awtrix_url).push_grid(
        config.awtrix_app_name,
        grid,
        duration_seconds=config.awtrix_app_duration,
        color_mode=config.color_mode,
        velocity=config.velocity,
    )
    print(f"Pushed AWTRIX CustomApp {config.awtrix_app_name}", file=sys.stderr)


def _fetch_grid_for_source(
    args: argparse.Namespace,
    *,
    token: str,
    login: str | None,
) -> ContributionGrid:
    if args.source == "profile":
        if login is None:
            raise ValueError("missing required config: GITHUB_LOGIN")
        return fetch_contribution_grid(token=token, login=login)

    if args.source == "commit-search":
        if not args.author_email and not args.org and not args.repo:
            raise ValueError(
                "--source commit-search requires --author-email, --org, or --repo"
            )
        if args.org and args.repo:
            raise ValueError("--org and --repo cannot be used together")
        return fetch_commit_search_grid(
            token=token,
            author_email=args.author_email,
            org=args.org,
            repo=args.repo,
        )

    raise ValueError(f"unknown source: {args.source}")


def _uninstall(args: argparse.Namespace) -> None:
    config = resolve_config(
        awtrix_url=args.awtrix_url,
        awtrix_app_name=args.awtrix_app_name,
        require_github=False,
        require_awtrix=True,
    )
    if config.awtrix_url is None:
        raise ValueError("missing required config: AWTRIX_URL")

    AwtrixClient(config.awtrix_url).uninstall_app(config.awtrix_app_name)
    print(f"Removed AWTRIX CustomApp {config.awtrix_app_name}", file=sys.stderr)


def _write_outputs(
    args: argparse.Namespace,
    grid: ContributionGrid,
    *,
    color_mode: ColorMode,
    velocity: bool,
) -> None:
    if args.json:
        json_output = json.dumps(grid.to_json(), indent=2)
        if args.json == "-":
            print(json_output)
        else:
            json_path = Path(args.json)
            json_path.parent.mkdir(parents=True, exist_ok=True)
            json_path.write_text(f"{json_output}\n")

    if args.terminal:
        print(render_terminal(grid, color_mode=color_mode, velocity=velocity))

    if args.png:
        write_png(grid, Path(args.png), color_mode=color_mode, velocity=velocity)


if __name__ == "__main__":
    raise SystemExit(main())
