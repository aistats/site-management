"""Propose reviewable _config.yml patches from virtual Dates / Hotels HTML."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from .convert import fetch_html, load_html
from .manifest import Manifest, PageSpec

# Map virtual Dates row names → stub deadline `name` values (and optional type hints).
DEADLINE_NAME_MAP = {
    "abstract submission deadline": "Abstract submission deadline",
    "full paper submission deadline": "Paper submission deadline",
    "paper submission deadline": "Paper submission deadline",
    "author reviewer discussion period begins": "Author response period",
    "author reviewer discussion period ends": "Author response period",
    "paper decision notifications": "Paper decision notifications",
    "camera ready version deadline": "Camera-ready deadline",
    "camera-ready version deadline": "Camera-ready deadline",
    "journal to conference submission deadline": "Journal-to-Conference track deadline",
    "workshop submission deadline": "Workshop submission deadline",
    "main conference begins": "Conference dates",
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
            # Typical: Name, Date, Countdown…
            name, date_text = cells[0], cells[1]
            if name.lower() in {"name", "attendees", "main conference", "paper submissions", "workshops"}:
                continue
            if "deadline" in name.lower() or "period" in name.lower() or "notification" in name.lower() or "begins" in name.lower() or "opens" in name.lower():
                rows.append((name, date_text))
            elif len(cells) >= 2 and re.search(r"\d", date_text):
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
            # First mapped start date wins; ends fill enddate when same key seen again.
            if "date" not in entry:
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


def apply_proposal_to_config(
    config: Dict[str, Any],
    proposal: ConfigProposal,
) -> Dict[str, Any]:
    """
    Return a shallow-copied config with only known conference keys merged.
    Chairs and unrelated keys are left untouched.
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
        for item in deadlines:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            if name not in proposal.deadlines:
                continue
            mapped = proposal.deadlines[name]
            if mapped.get("date"):
                item["date"] = mapped["date"]
            if mapped.get("enddate"):
                item["enddate"] = mapped["enddate"]
    return updated


def dump_config_yaml(data: Dict[str, Any]) -> str:
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
