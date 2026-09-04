#!/usr/bin/env python3
"""CLI for CIP-0004 sync_virtual."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

PACKAGE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = PACKAGE_DIR.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from sync_virtual.apply import apply_from_report  # noqa: E402
from sync_virtual.compare import run_compare, write_report_artefacts  # noqa: E402
from sync_virtual.config_patch import (  # noqa: E402
    apply_proposal_to_config_file,
    proposal_from_manifest,
    write_proposal_artefacts,
)
from sync_virtual.convert import PandocMissingError, convert_page  # noqa: E402
from sync_virtual.manifest import (  # noqa: E402
    load_manifest,
    load_manifest_with_optional_year_override,
    resolve_target_repo_path,
)


def default_manifest_path() -> Path:
    return PACKAGE_DIR / "manifests" / "aistats2026.yml"


def _split_only(value: Optional[str]) -> Optional[List[str]]:
    if value is None:
        return None
    return [part.strip() for part in value.split(",") if part.strip()]


def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.manifest)
    if args.with_year_override:
        manifest = load_manifest_with_optional_year_override(path)
    else:
        manifest = load_manifest(path)
    print(f"OK: {path}")
    print(f"  year={manifest.year} pages={len(manifest.pages)} base={manifest.virtual_base}")
    print(f"  target_repo={manifest.target_repo}")
    for page in manifest.pages:
        flag = "required" if page.required else "optional"
        print(f"  - {page.id}: {page.out} [{page.extract}] ({flag}, on_drift={page.on_drift})")
    return 0


def cmd_convert(args: argparse.Namespace) -> int:
    path = Path(args.manifest)
    manifest = load_manifest(path)
    page = manifest.page_by_id(args.id)
    fixture = Path(args.fixture) if args.fixture else None
    try:
        result = convert_page(manifest, page, fixture=fixture)
    except PandocMissingError as exc:
        print(exc, file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"convert failed: {exc}", file=sys.stderr)
        return 1

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(result.full_markdown, encoding="utf-8")
        print(f"Wrote candidate markdown: {out}")
    else:
        sys.stdout.write(result.full_markdown)
    return 0


def _load_for_sync(args: argparse.Namespace):
    path = Path(args.manifest)
    if args.with_year_override:
        manifest = load_manifest_with_optional_year_override(path)
        target = Path(manifest.target_repo)
    else:
        manifest = load_manifest(path)
        target = (
            Path(args.target_repo)
            if args.target_repo
            else resolve_target_repo_path(manifest, path)
        )
    if args.target_repo:
        target = Path(args.target_repo).resolve()
    return manifest, target


def cmd_sync(args: argparse.Namespace) -> int:
    manifest, target = _load_for_sync(args)
    manifest.target_repo = str(target)
    only = _split_only(args.only)
    fixtures_dir = Path(args.fixtures_dir) if args.fixtures_dir else None

    try:
        report = run_compare(
            manifest,
            target,
            only=only,
            fixtures_dir=fixtures_dir,
            include_index=args.include_index,
            offline=args.offline,
        )
    except PandocMissingError as exc:
        print(exc, file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"sync failed: {exc}", file=sys.stderr)
        return 1

    report_root = Path(args.report_dir) if args.report_dir else (target / manifest.report_dir)
    paths = write_report_artefacts(report, report_root)
    print(f"Report: {paths['summary']}")
    print(f"Virtual update request: {paths['virtual_update_request']}")
    for item in report.comparisons:
        print(f"  {item.classification:10} {item.page.id} -> {item.page.out}")

    proposal = proposal_from_manifest(
        manifest,
        fixtures_dir=fixtures_dir,
        offline=args.offline,
    )
    config_paths = write_proposal_artefacts(proposal, paths["dir"])
    print(f"Config proposal: {config_paths['markdown']}")

    if args.apply_config_patch:
        config_path = target / "_config.yml"
        if not config_path.is_file():
            print(f"error: missing {config_path}", file=sys.stderr)
            return 1
        before = config_path.read_text(encoding="utf-8")
        try:
            log = apply_proposal_to_config_file(config_path, proposal)
        except RuntimeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        after = config_path.read_text(encoding="utf-8")
        if before == after:
            print("Config patch: no textual changes (aliases may not match deadline names)")
        else:
            print(f"WROTE {config_path} (surgical config patch)")
        for line in log:
            print(f"  config: {line}")

    apply_result = apply_from_report(
        report,
        target,
        fill_missing=args.fill_missing,
        apply_from_virtual=args.apply_from_virtual,
        only=only,
    )
    for path in apply_result.written:
        print(f"WROTE {path}")
    for msg in apply_result.skipped:
        print(f"skip: {msg}")
    for msg in apply_result.errors:
        print(f"error: {msg}", file=sys.stderr)
    return 1 if apply_result.errors else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sync_virtual",
        description="Compare-first sync between virtual.aistats.org and aistats20XX (CIP-0004).",
    )
    parser.add_argument(
        "--manifest",
        default=str(default_manifest_path()),
        help="Path to manifest YAML (default: manifests/aistats2026.yml)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Load and validate a manifest")
    validate.add_argument(
        "--with-year-override",
        action="store_true",
        help="Prefer target_repo/virtual-sync.yml when present",
    )
    validate.set_defaults(func=cmd_validate)

    convert = sub.add_parser(
        "convert",
        help="Convert one page id to candidate markdown (no year-site write)",
    )
    convert.add_argument("--id", required=True, help="Page id from the manifest")
    convert.add_argument(
        "--fixture",
        help="Offline HTML file instead of fetching virtual",
    )
    convert.add_argument(
        "--out",
        help="Write candidate markdown to this path (default: stdout)",
    )
    convert.set_defaults(func=cmd_convert)

    sync = sub.add_parser(
        "sync",
        help="Compare-first sync: report + diffs + virtual update request (no write by default)",
    )
    sync.add_argument("--target-repo", help="Override manifest target_repo path")
    sync.add_argument("--report-dir", help="Directory for sync-report/YYYY-MM-DD/")
    sync.add_argument("--only", help="Comma-separated page ids")
    sync.add_argument(
        "--fixtures-dir",
        help="Prefer HTML fixtures named {id}.html when present",
    )
    sync.add_argument(
        "--offline",
        action="store_true",
        help="Do not fetch; pages without fixtures are skipped",
    )
    sync.add_argument(
        "--include-index",
        action="store_true",
        help="Include gated index page",
    )
    sync.add_argument(
        "--with-year-override",
        action="store_true",
        help="Prefer target_repo/virtual-sync.yml when present",
    )
    sync.add_argument(
        "--fill-missing",
        action="store_true",
        help="Create absent mapped pages from converted virtual (no overwrite)",
    )
    sync.add_argument(
        "--apply-from-virtual",
        action="store_true",
        help="Overwrite selected pages; requires --only",
    )
    sync.add_argument(
        "--apply-config-patch",
        action="store_true",
        help="Merge proposed deadline/venue fields into target _config.yml (chairs untouched)",
    )
    sync.set_defaults(func=cmd_sync)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
