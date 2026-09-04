"""CIP-0004 sync_virtual package."""

from .manifest import Manifest, PageSpec, load_manifest, load_manifest_with_optional_year_override

__all__ = [
    "Manifest",
    "PageSpec",
    "load_manifest",
    "load_manifest_with_optional_year_override",
]
