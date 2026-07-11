"""Command-line entrypoint for inspecting Gyeol Mono build plans."""

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from gyeol_mono.builder import BuildPlan
from gyeol_mono.japanese import JapaneseSource
from gyeol_mono.upstream import fetch_source, load_manifest


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="gyeol-mono")
    commands = root.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="print the preview or release build matrix")
    plan.add_argument(
        "--release-source",
        choices=[source.value for source in JapaneseSource],
        help="emit an 8-target release plan instead of the 16-target preview plan",
    )
    plan.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    fetch = commands.add_parser("fetch", help="download and verify pinned upstream archives")
    fetch.add_argument("--manifest", type=Path, default=Path("sources.toml"))
    fetch.add_argument("--output", type=Path, default=Path("upstream"))
    fetch.add_argument(
        "--source",
        action="append",
        default=[],
        help="source id to fetch; may be repeated, defaults to all sources",
    )
    fetch.add_argument("--force", action="store_true", help="replace an existing archive")
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "fetch":
        manifest = load_manifest(args.manifest)
        sources = manifest.select(tuple(args.source))
        for source in sources:
            result = fetch_source(source, args.output, force=args.force)
            action = "downloaded" if result.downloaded else "verified"
            print(f"{source.id}: {action} {result.archive} ({len(result.files)} files)")
        return 0

    if args.command != "plan":  # pragma: no cover - argparse enforces the subcommand
        raise AssertionError(f"unhandled command: {args.command}")

    build_plan = (
        BuildPlan.release(JapaneseSource(args.release_source))
        if args.release_source
        else BuildPlan.preview()
    )
    if args.json:
        print(json.dumps(build_plan.as_dict(), ensure_ascii=False, indent=2))
    else:
        _print_table(build_plan)
    return 0


def _print_table(plan: BuildPlan) -> None:
    print(f"targets: {len(plan.targets)}")
    for target in plan.targets:
        powerline = "PL" if target.powerline else "base"
        print(
            f"{target.japanese_source.value:18} {powerline:4} "
            f"{target.face.style.value:11} -> {target.names.file_name}"
        )


if __name__ == "__main__":
    raise SystemExit(main())
