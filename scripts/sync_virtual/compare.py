"""Compare candidate markdown to year-site pages; emit report artefacts."""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from .convert import ConvertResult, convert_page
from .manifest import Manifest, PageSpec

FRONT_MATTER_RE = re.compile(r"^---\s*\n.*?\n---\s*\n?", re.DOTALL)


@dataclass
class PageComparison:
    page: PageSpec
    classification: str  # missing | match | drift | year-only | virtual-only | skipped
    year_path: Path
    candidate: Optional[ConvertResult] = None
    year_body: Optional[str] = None
    candidate_body: Optional[str] = None
    diff: str = ""
    note: str = ""


@dataclass
class SyncReport:
    manifest: Manifest
    comparisons: List[PageComparison] = field(default_factory=list)
    report_dir: Optional[Path] = None

    def by_class(self, classification: str) -> List[PageComparison]:
        return [c for c in self.comparisons if c.classification == classification]


def strip_front_matter(text: str) -> str:
    if not text:
        return ""
    return FRONT_MATTER_RE.sub("", text, count=1)


def normalise_body(text: str) -> str:
    """Whitespace normalisation for compare only — does not rewrite prose words."""
    body = strip_front_matter(text)
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in body.split("\n")]
    # Collapse runs of blank lines
    out: List[str] = []
    blank = False
    for line in lines:
        if line.strip() == "":
            if not blank:
                out.append("")
            blank = True
        else:
            out.append(line)
            blank = False
    return "\n".join(out).strip() + ("\n" if out else "")


def unified_diff(a: str, b: str, fromfile: str, tofile: str) -> str:
    return "".join(
        difflib.unified_diff(
            a.splitlines(keepends=True),
            b.splitlines(keepends=True),
            fromfile=fromfile,
            tofile=tofile,
        )
    )


def compare_page(
    manifest: Manifest,
    page: PageSpec,
    target_repo: Path,
    *,
    fixture: Optional[Path] = None,
    skip_fetch: bool = False,
    include_index: bool = False,
) -> PageComparison:
    year_path = target_repo / page.out
    exists = year_path.is_file()

    if page.extract == "none":
        return PageComparison(
            page=page,
            classification="year-only" if exists else "missing",
            year_path=year_path,
            year_body=normalise_body(year_path.read_text(encoding="utf-8")) if exists else None,
            note="No virtual source in manifest",
        )

    if page.include == "index" and not include_index:
        return PageComparison(
            page=page,
            classification="skipped",
            year_path=year_path,
            note="index gated; pass --include-index to convert/compare",
        )

    if page.out.endswith(".yml") or page.out.endswith(".yaml") or page.extract == "config_merge":
        # Config patch path is a separate task; report presence only for now.
        return PageComparison(
            page=page,
            classification="year-only" if exists else "missing",
            year_path=year_path,
            note="Structured config_merge handled by YAML patch path (not body compare yet)",
        )

    if skip_fetch and fixture is None:
        return PageComparison(
            page=page,
            classification="skipped",
            year_path=year_path,
            note="skip_fetch set and no fixture",
        )

    candidate = convert_page(manifest, page, fixture=fixture)
    cand_body = normalise_body(candidate.body_markdown)

    if not exists:
        return PageComparison(
            page=page,
            classification="missing",
            year_path=year_path,
            candidate=candidate,
            candidate_body=cand_body,
            note="Mapped page absent on year site",
        )

    year_raw = year_path.read_text(encoding="utf-8")
    year_body = normalise_body(year_raw)
    if year_body == cand_body:
        return PageComparison(
            page=page,
            classification="match",
            year_path=year_path,
            candidate=candidate,
            year_body=year_body,
            candidate_body=cand_body,
        )

    diff = unified_diff(
        year_body,
        cand_body,
        fromfile=f"a/{page.out}",
        tofile=f"b/virtual:{page.id}",
    )
    return PageComparison(
        page=page,
        classification="drift",
        year_path=year_path,
        candidate=candidate,
        year_body=year_body,
        candidate_body=cand_body,
        diff=diff,
        note="Bodies differ after normalisation",
    )


def run_compare(
    manifest: Manifest,
    target_repo: Path,
    *,
    only: Optional[Sequence[str]] = None,
    fixtures_dir: Optional[Path] = None,
    include_index: bool = False,
    offline: bool = False,
) -> SyncReport:
    report = SyncReport(manifest=manifest)
    wanted = set(only) if only else None
    for page in manifest.pages:
        if wanted is not None and page.id not in wanted:
            continue
        fixture = None
        if fixtures_dir is not None:
            candidate = fixtures_dir / f"{page.id}.html"
            if candidate.is_file():
                fixture = candidate
        report.comparisons.append(
            compare_page(
                manifest,
                page,
                target_repo,
                fixture=fixture,
                skip_fetch=offline and fixture is None,
                include_index=include_index,
            )
        )
    return report


def _excerpt(text: Optional[str], limit: int = 400) -> str:
    if not text:
        return "(empty)"
    stripped = text.strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[: limit - 3] + "..."


def write_report_artefacts(report: SyncReport, report_root: Path) -> Dict[str, Path]:
    day = date.today().isoformat()
    out_dir = report_root / day
    diffs_dir = out_dir / "diffs"
    out_dir.mkdir(parents=True, exist_ok=True)
    diffs_dir.mkdir(parents=True, exist_ok=True)

    summary_lines = [
        f"# Sync report — AISTATS {report.manifest.year}",
        "",
        f"Virtual base: {report.manifest.virtual_base}",
        f"Target repo: `{report.manifest.target_repo}`",
        "",
        "## Summary",
        "",
    ]
    counts: Dict[str, int] = {}
    for item in report.comparisons:
        counts[item.classification] = counts.get(item.classification, 0) + 1
    for key in ("match", "drift", "missing", "year-only", "skipped", "virtual-only"):
        if key in counts:
            summary_lines.append(f"- **{key}**: {counts[key]}")
    summary_lines.extend(["", "## Pages", ""])

    request_lines = [
        f"# Virtual update request — AISTATS {report.manifest.year}",
        "",
        "The year site (`aistats20XX`) is the authoritative long-term record for the",
        "pages below. Please update virtual.aistats.org to match.",
        "",
    ]

    for item in report.comparisons:
        page = item.page
        summary_lines.append(
            f"- `{page.id}` → `{page.out}`: **{item.classification}**"
            + (f" — {item.note}" if item.note else "")
        )
        if item.classification == "drift" and item.diff:
            diff_path = diffs_dir / f"{page.id}.diff"
            diff_path.write_text(item.diff, encoding="utf-8")
            summary_lines.append(f"  - diff: `diffs/{page.id}.diff`")

            # Prefer year when on_drift is prefer_year or report (default request).
            if page.on_drift in {"report", "prefer_year"}:
                vurl = page.absolute_url(report.manifest.virtual_base) or "(no url)"
                request_lines.extend(
                    [
                        f"## {page.id}",
                        "",
                        f"- Year-site path: `{page.out}`",
                        f"- Virtual URL: {vurl}",
                        f"- Policy: on_drift={page.on_drift}",
                        "",
                        "### Year-site excerpt",
                        "",
                        "```markdown",
                        _excerpt(item.year_body),
                        "```",
                        "",
                        "### Virtual (converted) excerpt",
                        "",
                        "```markdown",
                        _excerpt(item.candidate_body),
                        "```",
                        "",
                        f"Full diff: `diffs/{page.id}.diff`",
                        "",
                    ]
                )

    summary_path = out_dir / "summary.md"
    request_path = out_dir / "virtual-update-request.md"
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    request_path.write_text("\n".join(request_lines) + "\n", encoding="utf-8")
    report.report_dir = out_dir
    return {"summary": summary_path, "virtual_update_request": request_path, "dir": out_dir}
