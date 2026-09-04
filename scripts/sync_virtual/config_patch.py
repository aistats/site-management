"""Propose and surgically apply `_config.yml` patches from virtual Dates / Hotels."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .convert import fetch_html, load_html
from .manifest import Manifest, PageSpec

# Virtual Dates row label → canonical proposal key.
DEADLINE_NAME_MAP = {
    "abstract submission deadline": "Abstract submission deadline",
    "full paper submission deadline": "Paper submission deadline",
    "paper submission deadline": "Paper submission deadline",
    "author rebuttal period begins": "Author response period",
    "author reviewer discussion period begins": "Author response period",
    "author reviewer discussion period ends": "Author response period",
    "paper decision notifications": "Paper decision notifications",
    "camera ready version deadline": "Camera-ready deadline",
    "camera-ready version deadline": "Camera-ready deadline",
    "journal to conference submission deadline": "Journal-to-Conference track deadline",
    "workshop submission deadline": "Workshop submission deadline",
    "main conference begins": "Conference dates",
    "registration opens": "Registration deadline",
    "early pricing before this date.": "Registration deadline",
}

# Canonical proposal key → year-site deadline name(s) and which proposal field to write.
# Multiple targets allow stub-shaped and 2026-shaped `_config.yml` variants.
DEADLINE_APPLY_TARGETS: Dict[str, List[Dict[str, str]]] = {
    "Abstract submission deadline": [
        {"name": "Abstract submission deadline", "field": "date", "from": "date"},
    ],
    "Paper submission deadline": [
        {"name": "Paper submission deadline", "field": "date", "from": "date"},
    ],
    "Author response period": [
        {"name": "Author response period", "field": "date", "from": "date"},
        {"name": "Author response period", "field": "enddate", "from": "enddate"},
        {"name": "Author response period starts", "field": "date", "from": "date"},
        {"name": "Author response period ends", "field": "date", "from": "enddate"},
        {"name": "Author response period ends", "field": "time", "from": "enddate"},
        {"name": "Author rebuttal period", "field": "date", "from": "date"},
        {"name": "Author rebuttal period", "field": "enddate", "from": "enddate"},
        {"name": "Author-reviewer discussion period", "field": "date", "from": "date"},
        {"name": "Author-reviewer discussion period", "field": "enddate", "from": "enddate"},
        {"name": "Author-Reviewer discussion period", "field": "date", "from": "date"},
        {"name": "Author-Reviewer discussion period", "field": "enddate", "from": "enddate"},
    ],
    "Paper decision notifications": [
        {"name": "Paper decision notifications", "field": "date", "from": "date"},
    ],
    "Camera-ready deadline": [
        {"name": "Camera-ready deadline", "field": "date", "from": "date"},
        {"name": "Deadline for camera-ready papers", "field": "date", "from": "date"},
        {"name": "Deadline for camera-ready papers", "field": "time", "from": "date"},
        {"name": "Camera-Ready revision due", "field": "date", "from": "date"},
    ],
    "Journal-to-Conference track deadline": [
        {"name": "Journal-to-Conference track deadline", "field": "date", "from": "date"},
        {"name": "Journal-to-Conference Track Request due", "field": "date", "from": "date"},
    ],
    "Workshop submission deadline": [
        {"name": "Workshop submission deadline", "field": "date", "from": "date"},
    ],
    "Conference dates": [
        {"name": "Conference dates", "field": "date", "from": "date"},
        {"name": "Conference dates", "field": "enddate", "from": "enddate"},
    ],
    "Registration deadline": [
        {"name": "Registration deadline", "field": "date", "from": "date"},
    ],
}

VENUE_RE = re.compile(
    r"will take place at the\s+(.+?)\s+in\s+(.+?)\.",
    re.IGNORECASE | re.DOTALL,
)


@dataclass
class ConfigProposal:
    deadlines: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    venue: Optional[str] = None
    location: Optional[str] = None
    meeting_dates_raw: Optional[str] = None
    source_urls: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conference": {
                "venue": self.venue,
                "location": self.location,
                "dates_raw": self.meeting_dates_raw,
                "deadlines": self.deadlines,
            },
            "source_urls": self.source_urls,
            "notes": self.notes,
        }


def _soup(html: str):
    from bs4 import BeautifulSoup

    return BeautifulSoup(html, "html.parser")


def parse_dates_rows(html: str) -> List[Tuple[str, str]]:
    soup = _soup(html)
    rows: List[Tuple[str, str]] = []
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
            cells = [c for c in cells if c]
            if len(cells) < 2:
                continue
            name, date_text = cells[0], cells[1]
            if name.lower() in {
                "name",
                "attendees",
                "main conference",
                "paper submissions",
                "workshops",
                "journal-to-conference",
            }:
                continue
            if (
                "deadline" in name.lower()
                or "period" in name.lower()
                or "notification" in name.lower()
                or "begins" in name.lower()
                or "opens" in name.lower()
                or "pricing" in name.lower()
            ):
                rows.append((name, date_text))
            elif re.search(r"\d", date_text):
                rows.append((name, date_text))
    return rows


def parse_venue_from_hotels(html: str) -> Tuple[Optional[str], Optional[str]]:
    soup = _soup(html)
    text = soup.get_text(" ", strip=True)
    match = VENUE_RE.search(text)
    if not match:
        return None, None
    venue = re.sub(r"\s+", " ", match.group(1)).strip()
    location = re.sub(r"\s+", " ", match.group(2)).strip()
    return venue, location


def parse_meeting_dates_banner(html: str) -> Optional[str]:
    soup = _soup(html)
    for table in soup.find_all("table"):
        text = table.get_text(" ", strip=True)
        if "Conference Sessions" in text or "Workshops" in text:
            return re.sub(r"\s+", " ", text)
    return None


def build_config_proposal(
    *,
    dates_html: Optional[str] = None,
    hotels_html: Optional[str] = None,
    dates_url: Optional[str] = None,
    hotels_url: Optional[str] = None,
) -> ConfigProposal:
    proposal = ConfigProposal()
    if dates_url:
        proposal.source_urls.append(dates_url)
    if hotels_url:
        proposal.source_urls.append(hotels_url)

    if dates_html:
        proposal.meeting_dates_raw = parse_meeting_dates_banner(dates_html)
        for name, date_text in parse_dates_rows(dates_html):
            key = DEADLINE_NAME_MAP.get(name.strip().lower())
            if not key:
                proposal.notes.append(f"Unmapped dates row: {name} → {date_text}")
                continue
            entry = proposal.deadlines.setdefault(key, {})
            lname = name.lower()
            if key == "Author response period":
                if "ends" in lname:
                    entry["enddate"] = date_text
                    entry["source_name_end"] = name
                elif "discussion" in lname and "begins" in lname:
                    entry["date"] = date_text
                    entry["source_name"] = name
                elif "date" not in entry:
                    entry["date"] = date_text
                    entry["source_name"] = name
            elif "date" not in entry:
                entry["date"] = date_text
                entry["source_name"] = name
            else:
                entry["enddate"] = date_text
                entry["source_name_end"] = name

    if hotels_html:
        venue, location = parse_venue_from_hotels(hotels_html)
        proposal.venue = venue
        proposal.location = location
        if not venue:
            proposal.notes.append("Could not parse venue from Hotels HTML")

    return proposal


def proposal_from_manifest(
    manifest: Manifest,
    *,
    fixtures_dir: Optional[Path] = None,
    offline: bool = False,
) -> ConfigProposal:
    dates_page = None
    hotels_page = None
    for page in manifest.pages:
        if page.id in {"dates", "config-dates-venue", "registration", "schedule"}:
            dates_page = dates_page or page
        if page.id == "accommodation":
            hotels_page = page

    dates_html = _load_page_html(manifest, dates_page, fixtures_dir, offline, "dates")
    hotels_html = _load_page_html(
        manifest, hotels_page, fixtures_dir, offline, "accommodation"
    )
    return build_config_proposal(
        dates_html=dates_html,
        hotels_html=hotels_html,
        dates_url=dates_page.absolute_url(manifest.virtual_base) if dates_page else None,
        hotels_url=hotels_page.absolute_url(manifest.virtual_base) if hotels_page else None,
    )


def _load_page_html(
    manifest: Manifest,
    page: Optional[PageSpec],
    fixtures_dir: Optional[Path],
    offline: bool,
    fixture_id: str,
) -> Optional[str]:
    if page is None:
        return None
    if fixtures_dir is not None:
        path = fixtures_dir / f"{fixture_id}.html"
        if path.is_file():
            return load_html(path)
        path = fixtures_dir / f"{page.id}.html"
        if path.is_file():
            return load_html(path)
    if offline:
        return None
    url = page.absolute_url(manifest.virtual_base)
    if not url:
        return None
    return fetch_html(url)


def read_config_yaml(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config root must be a mapping: {path}")
    return data


def render_proposal_markdown(proposal: ConfigProposal) -> str:
    lines = [
        "# Proposed `_config.yml` patches",
        "",
        "Reviewable only — not applied unless `--apply-config-patch` is set.",
        "Apply uses a surgical text merge (comments preserved).",
        "",
        "## Venue",
        "",
        f"- venue: {proposal.venue or '(none)'}",
        f"- location: {proposal.location or '(none)'}",
        f"- meeting dates (raw): {proposal.meeting_dates_raw or '(none)'}",
        "",
        "## Deadlines",
        "",
    ]
    if not proposal.deadlines:
        lines.append("(none mapped)")
    else:
        for name, entry in proposal.deadlines.items():
            lines.append(f"- **{name}**: `{entry.get('date', '')}`")
            if entry.get("enddate"):
                lines.append(f"  - enddate: `{entry['enddate']}`")
    if proposal.notes:
        lines.extend(["", "## Notes", ""])
        for note in proposal.notes:
            lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def write_proposal_artefacts(proposal: ConfigProposal, out_dir: Path) -> Dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    yaml_path = out_dir / "proposed-config-patch.yaml"
    md_path = out_dir / "proposed-config-patch.md"
    yaml_path.write_text(
        yaml.safe_dump(proposal.to_dict(), sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    md_path.write_text(render_proposal_markdown(proposal), encoding="utf-8")
    return {"yaml": yaml_path, "markdown": md_path}


def _replace_conference_scalar(text: str, key: str, value: str) -> str:
    """Replace `  key:` (conference-level indent) value; preserve surrounding comments."""
    pattern = re.compile(rf"^(  {re.escape(key)}:)[ \t]*.*$", re.MULTILINE)
    if not pattern.search(text):
        return text
    return pattern.sub(rf"\1 {value}", text, count=1)


def _set_deadline_field(text: str, deadline_name: str, field: str, value: str) -> Tuple[str, bool]:
    """
    Within the first deadlines list item whose name matches, set `field:`.
    If the field line is missing, insert it after the name line.
    """
    name_re = re.compile(
        rf"(^([ \t]*)- name:[ \t]*{re.escape(deadline_name)}[ \t]*\n)"
        rf"((?:^(?![ \t]*- name:)[ \t]+.*\n)*)",
        re.MULTILINE,
    )
    match = name_re.search(text)
    if not match:
        return text, False

    prefix = match.group(1)
    indent = match.group(2) + "  "
    block = match.group(3)
    field_re = re.compile(rf"^([ \t]*{re.escape(field)}:)[ \t]*.*$", re.MULTILINE)
    if field_re.search(block):
        new_block = field_re.sub(rf"\1 {value}", block, count=1)
    else:
        new_block = f"{indent}{field}: {value}\n" + block
    start, end = match.span()
    return text[:start] + prefix + new_block + text[end:], True


def apply_proposal_to_config_text(text: str, proposal: ConfigProposal) -> Tuple[str, List[str]]:
    """
    Surgically merge venue/location/deadline fields into config text.
    Preserves comments and unrelated keys. Returns (new_text, log_lines).
    """
    log: List[str] = []
    updated = text
    if proposal.venue:
        before = updated
        updated = _replace_conference_scalar(updated, "venue", proposal.venue)
        if updated != before:
            log.append(f"venue → {proposal.venue}")
    if proposal.location:
        before = updated
        updated = _replace_conference_scalar(updated, "location", proposal.location)
        if updated != before:
            log.append(f"location → {proposal.location}")

    for canonical, entry in proposal.deadlines.items():
        targets = DEADLINE_APPLY_TARGETS.get(canonical, [])
        for target in targets:
            source_key = target.get("from", "date")
            value = entry.get(source_key)
            if not value:
                continue
            updated, ok = _set_deadline_field(
                updated, target["name"], target["field"], str(value)
            )
            if ok:
                log.append(f"{target['name']}.{target['field']} ← {canonical}.{source_key}")
    return updated, log


def apply_proposal_to_config_file(path: Path, proposal: ConfigProposal) -> List[str]:
    """Apply surgical merge in place. Returns log of fields written."""
    original = path.read_text(encoding="utf-8")
    updated, log = apply_proposal_to_config_text(original, proposal)
    if updated == original:
        return log
    path.write_text(updated, encoding="utf-8")
    return log


def apply_proposal_to_config(
    config: Dict[str, Any],
    proposal: ConfigProposal,
) -> Dict[str, Any]:
    """
    In-memory merge for tests / inspection. Prefer apply_proposal_to_config_file
    for real year-site writes (comment-preserving).
    """
    import copy

    updated = copy.deepcopy(config)
    conference = updated.setdefault("conference", {})
    if not isinstance(conference, dict):
        raise ValueError("conference must be a mapping")

    if proposal.venue:
        conference["venue"] = proposal.venue
    if proposal.location:
        conference["location"] = proposal.location

    deadlines = conference.get("deadlines")
    if isinstance(deadlines, list) and proposal.deadlines:
        by_name = {
            item.get("name"): item for item in deadlines if isinstance(item, dict)
        }
        for canonical, entry in proposal.deadlines.items():
            for target in DEADLINE_APPLY_TARGETS.get(canonical, []):
                item = by_name.get(target["name"])
                if not item:
                    continue
                value = entry.get(target.get("from", "date"))
                if value:
                    item[target["field"]] = value
    return updated
