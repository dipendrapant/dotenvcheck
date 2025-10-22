import argparse
import json
import pathlib
import sys
from .scanner import scan_project
from .report import to_console, to_json


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envguard",
        description="Cross-check environment variables used in Python code against declarations in .env and docker-compose.",
    )
    p.add_argument(
        "path", nargs="?", default=".", help="Path to project root (defaults to current directory)."
    )
    p.add_argument(
        "--dotenv",
        default=None,
        help="Path to .env file (default: <path>/.env if present).",
    )
    p.add_argument(
        "--compose",
        default=None,
        help="Path to docker-compose.yml (optional).",
    )
    p.add_argument(
        "--include",
        default="*.py",
        help="Glob for code files to scan under <path> (default: *.py).",
    )
    p.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Relative path/glob to exclude (can be used multiple times).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON report to stdout instead of human-readable text.",
    )
    p.add_argument(
        "--fail-on",
        default="missing,typos",
        help="Comma-separated categories that cause nonzero exit. "
             "Options: missing, typos, unused, bad_values. Default: missing,typos",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Equivalent to --fail-on missing,typos,unused,bad_values",
    )
    p.add_argument(
        "--version",
        action="store_true",
        help="Print version and exit.",
    )
    return p


def main(argv=None):
    from . import __version__

    argv = argv or sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.version:
        print(__version__)
        return 0

    root = pathlib.Path(args.path).resolve()
    dotenv_path = pathlib.Path(args.dotenv).resolve() if args.dotenv else (root / ".env")
    compose_path = pathlib.Path(args.compose).resolve() if args.compose else None

    fail_on = {"missing", "typos"} if not args.strict else {"missing", "typos", "unused", "bad_values"}
    if not args.strict and args.fail_on:
        fail_on = set([s.strip() for s in args.fail_on.split(",") if s.strip()])

    findings = scan_project(
        root=root,
        dotenv_path=dotenv_path if dotenv_path.exists() else None,
        compose_path=compose_path if compose_path and compose_path.exists() else None,
        include_glob=args.include,
        exclude_globs=args.exclude,
    )

    if args.json:
        print(json.dumps(to_json(findings), indent=2))
    else:
        to_console(findings, base_dir=root)

    # exit code logic
    category_map = {
        "missing": findings.missing,
        "typos": findings.typos,
        "unused": findings.unused,
        "bad_values": findings.bad_values,
    }
    should_fail = any(bool(category_map.get(name, [])) for name in fail_on)
    return 1 if should_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
