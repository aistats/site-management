"""Load and validate sync_virtual YAML manifests (CIP-0004)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
from urllib.parse import urljoin

import yaml

EXTRACT_STRATEGIES = frozenset(
    {
        "main_after_nav",
        "event_bios",
        "dates_tables",
        "hotels_venue",
        "registration_blocks",
        "schedule_summary",
        "home_announcements",
        "config_merge",
        "none",
    }
)

ON_DRIFT_VALUES = frozenset({"report", "prefer_year", "prefer_virtual"})


@dataclass
class PageSpec:
    id: str
    out: str
    extract: str
    url: Optional[str] = None
    required: bool = False
    on_drift: str = "report"
    front_matter: Dict[str, Any] = field(default_factory=dict)
    assets: Optional[str] = None
    include: Optional[str] = None

    def absolute_url(self, virtual_base: str) -> Optional[str]:
        if not self.url:
            return None
        if self.url.startswith("http://") or self.url.startswith("https://"):
            return self.url
        return urljoin(virtual_base.rstrip("/") + "/", self.url.lstrip("/"))


@dataclass
class Manifest:
    year: int
    virtual_base: str
    target_repo: str
    pages: List[PageSpec]
    report_dir: str = "sync-report"
    link_only: List[Dict[str, Any]] = field(default_factory=list)
    path: Optional[Path] = None

    def page_by_id(self, page_id: str) -> PageSpec:
        for page in self.pages:
            if page.id == page_id:
                return page
        known = ", ".join(p.id for p in self.pages)
        raise KeyError(f"Unknown page id {page_id!r}. Known: {known}")

    def resolve_target_repo(self, relative_to: Optional[Path] = None) -> Path:
        root = relative_to or (self.path.parent if self.path else Path.cwd())
        path = Path(self.target_repo)
        if path.is_absolute():
            return path
        # Manifests live under manifests/; year repo is usually sibling of site-management.
        return (root / path).resolve()


def _require(mapping: Mapping[str, Any], key: str, where: str) -> Any:
    if key not in mapping:
        raise ValueError(f"Missing required field {key!r} in {where}")
    return mapping[key]


def _parse_page(raw: Mapping[str, Any], index: int) -> PageSpec:
    where = f"pages[{index}]"
    page_id = str(_require(raw, "id", where))
    out = str(_require(raw, "out", where))
    extract = str(_require(raw, "extract", where))
    if extract not in EXTRACT_STRATEGIES:
        raise ValueError(
            f"Unknown extract {extract!r} for {page_id}. "
            f"Allowed: {sorted(EXTRACT_STRATEGIES)}"
        )
    on_drift = str(raw.get("on_drift", "report"))
    if on_drift not in ON_DRIFT_VALUES:
        raise ValueError(
            f"Unknown on_drift {on_drift!r} for {page_id}. "
            f"Allowed: {sorted(ON_DRIFT_VALUES)}"
        )
    url = raw.get("url")
    if url is not None:
        url = str(url)
    if extract != "none" and not url and extract != "config_merge":
        # config_merge and dates often have urls; year-only uses none
        pass
    if extract != "none" and url is None:
        raise ValueError(f"Page {page_id} with extract {extract!r} requires url")

    front_matter = raw.get("front_matter") or {}
    if not isinstance(front_matter, dict):
        raise ValueError(f"front_matter for {page_id} must be a mapping")

    return PageSpec(
        id=page_id,
        out=out,
        extract=extract,
        url=url,
        required=bool(raw.get("required", False)),
        on_drift=on_drift,
        front_matter=dict(front_matter),
        assets=str(raw["assets"]) if raw.get("assets") is not None else None,
        include=str(raw["include"]) if raw.get("include") is not None else None,
    )


def load_manifest(path: Path) -> Manifest:
    path = path.resolve()
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Manifest root must be a mapping: {path}")

    year = int(_require(data, "year", "manifest"))
    virtual_base = str(_require(data, "virtual_base", "manifest"))
    target_repo = str(_require(data, "target_repo", "manifest"))
    pages_raw = _require(data, "pages", "manifest")
    if not isinstance(pages_raw, list) or not pages_raw:
        raise ValueError("manifest.pages must be a non-empty list")

    pages = [_parse_page(item, i) for i, item in enumerate(pages_raw)]
    ids = [p.id for p in pages]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate page ids in manifest: {ids}")

    link_only = data.get("link_only") or []
    if not isinstance(link_only, list):
        raise ValueError("link_only must be a list")

    return Manifest(
        year=year,
        virtual_base=virtual_base,
        target_repo=target_repo,
        pages=pages,
        report_dir=str(data.get("report_dir", "sync-report")),
        link_only=list(link_only),
        path=path,
    )


def year_override_path(target_repo: Path) -> Path:
    """Optional per-year override: aistats20XX/virtual-sync.yml."""
    return target_repo / "virtual-sync.yml"


def site_management_root(manifest_path: Path) -> Path:
    """.../site-management/scripts/sync_virtual/manifests/file.yml → site-management."""
    return manifest_path.resolve().parents[3]


def resolve_target_repo_path(manifest: Manifest, manifest_path: Path) -> Path:
    path = Path(manifest.target_repo)
    if path.is_absolute():
        return path
    return (site_management_root(manifest_path) / path).resolve()


def load_manifest_with_optional_year_override(
    default_manifest: Path,
    target_repo: Optional[Path] = None,
) -> Manifest:
    """
    Load the shared default manifest. If the year repo contains virtual-sync.yml,
    load that file instead (full replacement for clarity).
    """
    default_manifest = default_manifest.resolve()
    manifest = load_manifest(default_manifest)
    repo = target_repo or resolve_target_repo_path(manifest, default_manifest)

    override = year_override_path(repo)
    if override.is_file():
        return load_manifest(override)

    manifest.path = default_manifest
    manifest.target_repo = str(repo)
    return manifest
