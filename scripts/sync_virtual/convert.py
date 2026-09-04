"""Fetch virtual HTML, extract body, pandoc to markdown, inject front matter."""

from __future__ import annotations

import re
import shutil
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .manifest import Manifest, PageSpec

USER_AGENT = "aistats-sync-virtual/0.1 (+https://github.com/aistats/site-management)"


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
        ".site-header",
        ".site-footer",
    ):
        for node in soup.select(selector):
            node.decompose()


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


def extract_fragment(html: str, strategy: str) -> str:
    """Return an HTML fragment string for pandoc."""
    import copy

    if strategy == "none":
        return ""
    if strategy == "config_merge":
        # Structured path uses tables later; still return dates-ish main for inspection.
        strategy = "dates_tables"

    soup = _soup(html)
    _strip_chrome(soup)
    root = _main_candidate(soup)

    if strategy == "event_bios":
        # Prefer lists of bios / cards if present; else main.
        candidates = root.select(".bio, .speaker, .event-item, .person, article")
        if len(candidates) >= 1:
            wrapper = soup.new_tag("div")
            for heading in root.find_all(re.compile(r"^h[1-3]$"), limit=3):
                wrapper.append(copy.copy(heading))
            for item in candidates:
                text = item.get_text(" ", strip=True)
                if len(text) < 40:
                    continue
                wrapper.append(copy.copy(item))
            if wrapper.get_text(strip=True):
                return _inner_html(wrapper) or str(wrapper)

    # main_after_nav, hotels_venue, registration_blocks, schedule_summary,
    # home_announcements, dates_tables: share chrome-stripped main for now.
    # Finer selectors can narrow later without changing strategy names.
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
    # Drop common empty artefacts; do not rewrite prose.
    lines = text.replace("\r\n", "\n").split("\n")
    cleaned = []
    for line in lines:
        if line.strip() in {":::", "---"} and not cleaned:
            continue
        cleaned.append(line)
    body = "\n".join(cleaned).strip() + ("\n" if cleaned else "")
    return body


def inject_front_matter(body_markdown: str, front_matter: dict) -> str:
    if not front_matter:
        return body_markdown
    # Preserve body prose byte-for-byte after the closing fence.
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

    fragment = extract_fragment(html, page.extract)
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
