"""Opt-in writes from converted virtual content onto the year site."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Set

from .compare import PageComparison, SyncReport, normalise_body
from .convert import convert_page
from .manifest import Manifest, PageSpec


@dataclass
class ApplyResult:
    written: List[Path] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def _parse_only(only: Optional[Sequence[str]]) -> Optional[Set[str]]:
    if only is None:
        return None
    return {item.strip() for item in only if item.strip()}


def apply_from_report(
    report: SyncReport,
    target_repo: Path,
    *,
    fill_missing: bool = False,
    apply_from_virtual: bool = False,
    only: Optional[Sequence[str]] = None,
) -> ApplyResult:
    """
    Write candidates into the year repo.

    - Default (both flags false): no writes.
    - --fill-missing: create files that are classification == missing.
    - --apply-from-virtual: overwrite existing pages; requires --only
      (or only=all via explicit sentinel handled by CLI).
    """
    result = ApplyResult()
    only_ids = _parse_only(only)

    if not fill_missing and not apply_from_virtual:
        result.skipped.append("No write flags set; year site unchanged")
        return result

    if apply_from_virtual and only_ids is None:
        result.errors.append(
            "--apply-from-virtual requires --only id1,id2 (refusing broad overwrite)"
        )
        return result

    for item in report.comparisons:
        page = item.page
        if only_ids is not None and page.id not in only_ids:
            continue

        if item.classification == "skipped":
            result.skipped.append(f"{page.id}: {item.note or 'skipped'}")
            continue

        if page.extract == "config_merge" or page.out.endswith((".yml", ".yaml")):
            result.skipped.append(f"{page.id}: config_merge uses YAML patch path, not apply")
            continue

        dest = target_repo / page.out

        if item.classification == "missing" and fill_missing:
            candidate = item.candidate
            if candidate is None or not candidate.full_markdown.strip():
                result.errors.append(f"{page.id}: no candidate markdown to fill")
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(candidate.full_markdown, encoding="utf-8")
            result.written.append(dest)
            continue

        if apply_from_virtual and only_ids is not None and page.id in only_ids:
            if item.classification == "missing":
                # Allow apply to create as well when explicitly listed.
                candidate = item.candidate
                if candidate is None:
                    result.errors.append(f"{page.id}: no candidate for apply")
                    continue
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(candidate.full_markdown, encoding="utf-8")
                result.written.append(dest)
                continue
            if item.candidate is None or not item.candidate.full_markdown.strip():
                result.errors.append(f"{page.id}: no candidate markdown for apply")
                continue
            if not dest.is_file() and not fill_missing:
                result.errors.append(f"{page.id}: target missing; use --fill-missing or apply create")
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(item.candidate.full_markdown, encoding="utf-8")
            result.written.append(dest)
            continue

        if fill_missing and item.classification != "missing":
            result.skipped.append(f"{page.id}: exists ({item.classification}); fill-missing no-op")

    return result


def ensure_candidates(
    manifest: Manifest,
    comparisons: List[PageComparison],
    *,
    fixtures_dir: Optional[Path] = None,
) -> None:
    """Fetch/convert any comparison still lacking a candidate (e.g. live run)."""
    for item in comparisons:
        if item.candidate is not None:
            continue
        if item.page.extract in {"none", "config_merge"}:
            continue
        fixture = None
        if fixtures_dir is not None:
            path = fixtures_dir / f"{item.page.id}.html"
            if path.is_file():
                fixture = path
        try:
            item.candidate = convert_page(manifest, item.page, fixture=fixture)
            item.candidate_body = normalise_body(item.candidate.body_markdown)
        except Exception as exc:  # noqa: BLE001
            item.note = f"convert failed: {exc}"
