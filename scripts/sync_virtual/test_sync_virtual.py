"""Tests for CIP-0004 sync_virtual (no year-site clobber by default)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SCRIPTS = PACKAGE.parent
import sys

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from sync_virtual.apply import apply_from_report
from sync_virtual.compare import run_compare, write_report_artefacts
from sync_virtual.config_patch import (
    apply_proposal_to_config,
    build_config_proposal,
)
from sync_virtual.convert import convert_page
from sync_virtual.manifest import load_manifest

MANIFEST = PACKAGE / "manifests" / "aistats2026.yml"
FIXTURES = PACKAGE / "fixtures"


class SyncVirtualTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = load_manifest(MANIFEST)

    def test_manifest_loads_inventory(self) -> None:
        self.assertEqual(self.manifest.year, 2026)
        ids = {p.id for p in self.manifest.pages}
        self.assertIn("call-for-papers", ids)
        self.assertIn("invited", ids)
        self.assertIn("config-dates-venue", ids)

    def test_convert_fixture_preserves_sentence(self) -> None:
        page = self.manifest.page_by_id("call-for-papers")
        result = convert_page(
            self.manifest,
            page,
            fixture=FIXTURES / "call-for-papers.html",
        )
        self.assertIn(
            "Authors must not paraphrase this fixture sentence during sync tests.",
            result.body_markdown,
        )
        self.assertIn("title: Call for Papers", result.full_markdown)

    def test_default_sync_does_not_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            year_file = target / "call-for-papers.md"
            year_file.write_text("# Call for Papers\n\nKeep me.\n", encoding="utf-8")
            before = year_file.read_text(encoding="utf-8")
            report = run_compare(
                self.manifest,
                target,
                only=["call-for-papers"],
                fixtures_dir=FIXTURES,
                offline=True,
            )
            apply_from_report(report, target)  # no flags
            self.assertEqual(year_file.read_text(encoding="utf-8"), before)
            self.assertEqual(report.comparisons[0].classification, "drift")

    def test_fill_missing_and_apply_requires_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            report = run_compare(
                self.manifest,
                target,
                only=["call-for-papers"],
                fixtures_dir=FIXTURES,
                offline=True,
            )
            refused = apply_from_report(
                report, target, apply_from_virtual=True, only=None
            )
            self.assertTrue(refused.errors)
            filled = apply_from_report(report, target, fill_missing=True)
            self.assertTrue((target / "call-for-papers.md").is_file())
            self.assertTrue(filled.written)

    def test_report_artefacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "call-for-papers.md").write_text(
                "# Call for Papers\n\nOld.\n", encoding="utf-8"
            )
            report = run_compare(
                self.manifest,
                target,
                only=["call-for-papers"],
                fixtures_dir=FIXTURES,
                offline=True,
            )
            paths = write_report_artefacts(report, Path(tmp) / "report")
            self.assertTrue(paths["summary"].is_file())
            self.assertTrue(paths["virtual_update_request"].is_file())
            self.assertIn("call-for-papers", paths["virtual_update_request"].read_text())

    def test_config_proposal_from_fixtures(self) -> None:
        dates = (FIXTURES / "dates.html").read_text(encoding="utf-8")
        hotels = (FIXTURES / "accommodation.html").read_text(encoding="utf-8")
        proposal = build_config_proposal(dates_html=dates, hotels_html=hotels)
        self.assertIn("Abstract submission deadline", proposal.deadlines)
        self.assertIn("Hilton Tangier", proposal.venue or "")
        self.assertIn("Tangier", proposal.location or "")

        config = {
            "conference": {
                "venue": "Old",
                "location": "Old",
                "chairs": [{"type": "General Chairs", "people": [{"family": "X"}]}],
                "deadlines": [
                    {"name": "Abstract submission deadline", "date": ""},
                    {"name": "Paper submission deadline", "date": ""},
                ],
            }
        }
        updated = apply_proposal_to_config(config, proposal)
        self.assertEqual(
            updated["conference"]["chairs"],
            config["conference"]["chairs"],
        )
        self.assertTrue(updated["conference"]["deadlines"][0]["date"])


if __name__ == "__main__":
    unittest.main()
