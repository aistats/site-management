"""Fetch virtual HTML, extract body, pandoc to markdown, inject front matter."""

from __future__ import annotations

import copy
import re
import shutil
import subprocess
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional

from .manifest import Manifest, PageSpec

USER_AGENT = "aistats-sync-virtual/0.1 (+https://github.com/aistats/site-management)"

EMPTY_HTML_LINE = re.compile(
    r"^\s*</?(?:div|span|section|header|footer|nav|button)[^>]*>\s*$",
    re.IGNORECASE,
)
CALENDAR_NOTE = (
    "Full interactive calendar: "
    "https://virtual.aistats.org/virtual/{year}/calendar"
)
REGISTRATION_NOTE = (
    "Registration and payment are handled on the virtual conference site; "
    "use the conference registration portal linked from virtual.aistats.org."
)


class PandocMissingError(RuntimeError):
    pass


@dataclass
class ConvertResult:
    page_id: str
    source_url: Optional[str]
    html_path: Optional[Path]
    fragment_html: str
    body_markdown: str
    full_markdown: str


def require_pandoc() -> str:
    path = shutil.which("pandoc")
    if not path:
        raise PandocMissingError(
            "pandoc not found on PATH. Install pandoc "
            "(https://pandoc.org/) before running sync_virtual convert."
        )
    return path


def fetch_html(url: str, timeout: int = 60) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def load_html(source: Path) -> str:
    return source.read_text(encoding="utf-8")


def _soup(html: str):
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise ImportError(
            "BeautifulSoup (bs4) is required for HTML extract. "
            "Install with: .venv-vibesafe/bin/pip install beautifulsoup4"
        ) from exc
    return BeautifulSoup(html, "html.parser")


def _strip_chrome(soup) -> None:
    for selector in (
        "nav",
        "header",
        "footer",
        "script",
        "style",
        "noscript",
        "[role=navigation]",
        ".cookie",
        "#cookie",
        ".cookies-banner",
        ".navbar",
        ".navbar-collapse",
        ".site-header",
        ".site-footer",
        "#child-menu",
        ".dropdown-menu",
        "table.gdpr-statement",
        ".gdpr-statement",
        ".sticky-header-wrapper",
        ".card-bookmark",
        ".events-count-badge",
        ".btn-close",
        "[data-bs-dismiss]",
    ):
        for node in soup.select(selector):
            node.decompose()

    # Year switcher / leftover dropdown chrome often sits in main.
    for node in list(soup.find_all(id=re.compile(r"navbar", re.I))):
        node.decompose()
    for node in list(soup.find_all(string=re.compile(r"^\s*Select Year:", re.I))):
        parent = node.parent
        if parent is not None:
            # Drop the nearest small wrapper that only holds the switcher.
            target = parent
            for _ in range(3):
                if target.parent and target.parent.name in {"div", "li", "ul"}:
                    if "Select Year" in target.parent.get_text(" ", strip=True)[:80]:
                        target = target.parent
                else:
                    break
            target.decompose()


def _prune_empty_wrappers(root) -> None:
    """Remove empty layout shells left after chrome strip."""
    if root is None:
        return
    changed = True
    while changed:
        changed = False
        for node in list(root.find_all(["div", "span", "section", "ul", "li"])):
            if node.decomposed:
                continue
            text = node.get_text(strip=True)
            has_media = bool(node.find(["img", "table", "a", "p", "h1", "h2", "h3", "h4"]))
            if text or has_media:
                continue
            node.decompose()
            changed = True


def _unwrap_redundant_containers(root) -> None:
    """Flatten Bootstrap container wrappers that only delay the article body."""
    if root is None:
        return
    for _ in range(6):
        progressed = False
        for node in list(
            root.select(
                "div.container-fluid, div.container, div.row, div.col, "
                "div.col-12, div.my-5, div.my-3, div.g-4"
            )
        ):
            if node.decomposed or node.parent is None:
                continue
            kids = [c for c in node.children if getattr(c, "name", None) or str(c).strip()]
            # Unwrap if single element child, or if this wrapper has no own text.
            own_text = "".join(
                str(t) for t in node.find_all(string=True, recursive=False)
            ).strip()
            if own_text:
                continue
            if len(kids) == 1 and getattr(kids[0], "name", None):
                node.replace_with(kids[0])
                progressed = True
            elif not kids:
                node.decompose()
                progressed = True
        if not progressed:
            break


def _main_candidate(soup):
    for selector in (
        "main",
        "article",
        "#content",
        ".content",
        ".main-content",
        "#MainContent",
        ".page-content",
        "[role=main]",
    ):
        node = soup.select_one(selector)
        if node and node.get_text(strip=True):
            return node
    body = soup.body
    return body if body else soup


def _inner_html(node) -> str:
    """Prefer children so pandoc does not wrap a leftover main/div shell."""
    if node is None:
        return ""
    if getattr(node, "name", None) in {"main", "article", "body", "div"} or (
        hasattr(node, "get") and node.get("role") == "main"
    ):
        return "".join(str(child) for child in node.children).strip()
    return str(node)


def _prepare_root(html: str):
    soup = _soup(html)
    _strip_chrome(soup)
    root = _main_candidate(soup)
    _prune_empty_wrappers(root)
    _unwrap_redundant_containers(root)
    _prune_empty_wrappers(root)
    return soup, root


def _card_by_header(root, needle: str):
    needle_l = needle.lower().strip()
    exact = None
    partial = None
    for header in root.select(".card-header"):
        text = header.get_text(" ", strip=True).lower()
        card = header.find_parent(class_="card")
        if not card:
            continue
        if text == needle_l:
            exact = card
            break
        if needle_l in text and partial is None:
            partial = card
    if exact is not None:
        return exact
    if partial is not None:
        return partial
    for heading in root.find_all(re.compile(r"^h[1-4]$")):
        text = heading.get_text(" ", strip=True).lower()
        if text == needle_l or needle_l in text:
            card = heading.find_parent(class_="card")
            if card:
                return card
            return heading.parent
    return None


def _table_section_rows(table, start_labels: Iterable[str], stop_labels: Iterable[str]):
    """Yield <tr> elements from a labeled section until the next section header."""
    start = {s.lower() for s in start_labels}
    stop = {s.lower() for s in stop_labels}
    capturing = False
    for tr in table.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
        nonempty = [c for c in cells if c]
        label = nonempty[0].lower() if nonempty else ""
        if not capturing and label in start:
            capturing = True
            continue
        if capturing and label in stop:
            break
        if capturing:
            yield tr


def _extract_dates_tables(soup, root) -> str:
    wrapper = soup.new_tag("div")
    # Prefer the full deadlines card (not the financial-aid "Important Dates" card).
    card = _card_by_header(root, "Dates and Deadlines")
    if card is None:
        card = _card_by_header(root, "Important Dates and Deadlines")
    source = card or root
    heading = None
    if card:
        heading = card.select_one(".card-header, h1, h2, h3")
    if heading:
        h = soup.new_tag("h2")
        h.string = heading.get_text(" ", strip=True)
        wrapper.append(h)
    keep_sections = {
        "paper submissions",
        "workshops",
        "journal-to-conference",
        "main conference",
    }
    for table in source.find_all("table"):
        section_table = soup.new_tag("table")
        captured = False
        current_ok = False
        for tr in table.find_all("tr"):
            cells = [c.get_text(" ", strip=True) for c in tr.find_all(["th", "td"])]
            nonempty = [c for c in cells if c]
            if len(nonempty) == 1 and nonempty[0].lower() in keep_sections:
                current_ok = True
                section_table.append(copy.copy(tr))
                captured = True
                continue
            if len(nonempty) == 1:
                current_ok = False
                continue
            if current_ok and nonempty:
                section_table.append(copy.copy(tr))
                captured = True
        if captured:
            wrapper.append(section_table)
    if not wrapper.find("table"):
        meeting = _card_by_header(root, "AISTATS 2026 Meeting Dates") or _card_by_header(
            root, "Meeting Dates"
        )
        if meeting:
            return _inner_html(meeting)
        return _inner_html(root)
    return str(wrapper)


def _extract_registration_blocks(soup, root, year: Optional[int] = None) -> str:
    wrapper = soup.new_tag("div")
    title = soup.new_tag("h1")
    title.string = "Registration"
    wrapper.append(title)
    note = soup.new_tag("p")
    note.string = REGISTRATION_NOTE
    wrapper.append(note)

    meeting = _card_by_header(root, "Meeting Dates")
    if meeting:
        wrapper.append(copy.copy(meeting))

    card = _card_by_header(root, "Dates and Deadlines") or root
    for table in card.find_all("table"):
        section = soup.new_tag("table")
        rows = list(
            _table_section_rows(
                table,
                start_labels=["attendees"],
                stop_labels=["main conference", "paper submissions", "workshops"],
            )
        )
        if not rows:
            continue
        head = soup.new_tag("tr")
        th = soup.new_tag("th")
        th.string = "Attendees"
        head.append(th)
        section.append(head)
        for tr in rows:
            section.append(copy.copy(tr))
        wrapper.append(section)
    return str(wrapper)


def _extract_schedule_summary(soup, root, year: Optional[int] = None) -> str:
    wrapper = soup.new_tag("div")
    title = soup.new_tag("h1")
    title.string = "Schedule"
    wrapper.append(title)
    meeting = _card_by_header(root, "Meeting Dates")
    if meeting:
        wrapper.append(copy.copy(meeting))
    card = _card_by_header(root, "Dates and Deadlines") or root
    for table in card.find_all("table"):
        section = soup.new_tag("table")
        rows = list(
            _table_section_rows(
                table,
                start_labels=["main conference"],
                stop_labels=["paper submissions", "workshops", "journal-to-conference", "attendees"],
            )
        )
        for tr in rows:
            section.append(copy.copy(tr))
        if section.find("tr"):
            wrapper.append(section)
    note = soup.new_tag("p")
    y = year or 2026
    note.string = CALENDAR_NOTE.format(year=y)
    wrapper.append(note)
    return str(wrapper)


def _extract_event_bios(soup, root) -> str:
    wrapper = soup.new_tag("div")
    for heading in root.find_all(re.compile(r"^h[1-3]$"), limit=4):
        text = heading.get_text(" ", strip=True)
        if text and "Navigation" not in text and "Select Year" not in text:
            clean = soup.new_tag(heading.name)
            clean.string = text
            wrapper.append(clean)
            break

    cards = root.select(".event-card, .bio, .speaker, .event-item, .person")
    if not cards:
        return _inner_html(root)

    for card in cards:
        cleaned = copy.copy(card)
        for sel in (
            ".card-bookmark",
            ".events-count-badge",
            ".event-type-badge",
            ".meta-pill",
            ".view-details-link",
            ".btn",
            "button",
            ".dropdown",
        ):
            for node in cleaned.select(sel):
                node.decompose()
        # Drop attribute noise used only by the virtual UI.
        for attr in list(cleaned.attrs):
            if attr.startswith("event-") or attr in {"touchup", "onclick"}:
                del cleaned.attrs[attr]
        if cleaned.get_text(strip=True):
            wrapper.append(cleaned)
    return str(wrapper) if wrapper.get_text(strip=True) else _inner_html(root)


def extract_fragment(html: str, strategy: str, *, year: Optional[int] = None) -> str:
    """Return an HTML fragment string for pandoc."""
    if strategy == "none":
        return ""
    if strategy == "config_merge":
        strategy = "dates_tables"

    soup, root = _prepare_root(html)

    if strategy == "event_bios":
        return _extract_event_bios(soup, root)
    if strategy == "dates_tables":
        return _extract_dates_tables(soup, root)
    if strategy == "registration_blocks":
        return _extract_registration_blocks(soup, root, year=year)
    if strategy == "schedule_summary":
        return _extract_schedule_summary(soup, root, year=year)
    if strategy == "hotels_venue":
        # Same chrome strip; prefer hotel heading region if present.
        hotel = None
        for heading in root.find_all(re.compile(r"^h[1-3]$")):
            if "hotel" in heading.get_text(" ", strip=True).lower():
                hotel = heading.find_parent("div") or heading.parent
                break
        target = hotel or root
        _prune_empty_wrappers(target)
        return _inner_html(target)

    # main_after_nav, home_announcements
    return _inner_html(root)


def html_to_markdown(fragment_html: str, pandoc_bin: Optional[str] = None) -> str:
    pandoc = pandoc_bin or require_pandoc()
    if not fragment_html.strip():
        return ""
    proc = subprocess.run(
        [
            pandoc,
            "-f",
            "html",
            "-t",
            "gfm",
            "--wrap=none",
        ],
        input=fragment_html,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"pandoc failed: {proc.stderr.strip() or proc.stdout}")
    return _clean_pandoc_markdown(proc.stdout)


def _clean_pandoc_markdown(text: str) -> str:
    """Drop empty HTML shell lines; do not rewrite prose words."""
    lines = text.replace("\r\n", "\n").split("\n")
    cleaned: List[str] = []
    blank = False
    for line in lines:
        if EMPTY_HTML_LINE.match(line):
            continue
        # Drop attribute-only opening tags left on their own line.
        if re.match(r"^\s*<div\b[^>]*>\s*$", line, re.I):
            continue
        if line.strip() == "":
            if blank or not cleaned:
                continue
            cleaned.append("")
            blank = True
            continue
        cleaned.append(line.rstrip())
        blank = False
    body = "\n".join(cleaned).strip()
    return body + ("\n" if body else "")


def inject_front_matter(body_markdown: str, front_matter: dict) -> str:
    if not front_matter:
        return body_markdown
    dumped = yaml_front_matter(front_matter)
    body = body_markdown if body_markdown.endswith("\n") else body_markdown + "\n"
    return f"---\n{dumped}---\n\n{body}"


def yaml_front_matter(data: dict) -> str:
    import yaml

    return yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )


def convert_page(
    manifest: Manifest,
    page: PageSpec,
    *,
    fixture: Optional[Path] = None,
    html_cache_dir: Optional[Path] = None,
) -> ConvertResult:
    if page.extract == "none":
        return ConvertResult(
            page_id=page.id,
            source_url=None,
            html_path=None,
            fragment_html="",
            body_markdown="",
            full_markdown=inject_front_matter("", page.front_matter),
        )

    source_url = page.absolute_url(manifest.virtual_base)
    html_path = None
    if fixture is not None:
        html = load_html(fixture)
        html_path = fixture
    else:
        if not source_url:
            raise ValueError(f"Page {page.id} has no URL to fetch")
        html = fetch_html(source_url)
        if html_cache_dir is not None:
            html_cache_dir.mkdir(parents=True, exist_ok=True)
            html_path = html_cache_dir / f"{page.id}.html"
            html_path.write_text(html, encoding="utf-8")

    fragment = extract_fragment(html, page.extract, year=manifest.year)
    body = html_to_markdown(fragment)
    full = inject_front_matter(body, page.front_matter)
    return ConvertResult(
        page_id=page.id,
        source_url=source_url,
        html_path=html_path,
        fragment_html=fragment,
        body_markdown=body,
        full_markdown=full,
    )
