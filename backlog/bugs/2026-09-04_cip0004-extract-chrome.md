---
id: "2026-09-04_cip0004-extract-chrome"
title: "CIP-0004: Strip virtual chrome and specialise extract strategies"
status: "Completed"
priority: "High"
created: "2026-09-04"
last_updated: "2026-09-04"
category: "bugs"
related_cips: ["0004"]
owner: "Neil Lawrence"
dependencies: ["2026-09-04_cip0004-convert-pipeline"]
tags:
- backlog
- cip0004
- sync
- extract
- pandoc
---

# Task: Strip virtual chrome and specialise extract strategies

## Description

Probe runs on `gh-pages` (`cip0004-apply-probe`) and `sync-from-virtual` (`cip0004-apply-probe-sfv`) showed that converted pages keep virtual Bootstrap chrome and that several named extract strategies still share one “main” path.

Fix extract so archival markdown is mostly prose (plus necessary structure), not layout shells. Specialise Dates-derived and event-list strategies so registration / schedule / dates / invited / awards stop looking like clones of the wrong page.

Evidence: empty `#child-menu` / `container-fluid` wrappers on Call for Papers; `registration.md` ≈ `schedule.md` ≈ `dates.md`; invited/awards retain event-card chrome. Pre-apply diffs under `aistats2026/sync-report-sfv/2026-09-04/diffs/` show paraphrase vs chrome mixed together.

## Acceptance Criteria

- [x] `main_after_nav` (and shared helpers) remove nav/header/footer, cookie banners, empty dropdown shells, and redundant Bootstrap wrappers before pandoc
- [x] Converted Call for Papers fixture or live snapshot has no `child-menu` / nested empty `container-fluid` lead-in; key virtual sentences still present
- [x] `registration_blocks`, `schedule_summary`, and `dates_tables` produce clearly different bodies (or registration/schedule stay link-heavy summaries rather than full Dates dumps)
- [x] `event_bios` keeps speaker/award names and bio text; drops bookmark/badge/card chrome where practical
- [x] Unit/fixture tests cover chrome strip and at least one Dates-strategy divergence
- [x] Re-convert spot-check: CFP and invited candidates reviewed against virtual wording (faithful, not paraphrased)

## Implementation Notes

Prefer tightening BeautifulSoup selectors and post-pandoc cleanup of empty HTML leftovers over regex on prose. Do not rewrite virtual sentences. Image download for speakers can remain stubbed.

After this lands, re-run dual-base validation (`2026-09-04_cip0004-validate-2026`).

## Related

- CIP: 0004
- PR: [aistats2026#1](https://github.com/aistats/aistats2026/pull/1) (destination once converts are clean)
- Local probes: `cip0004-apply-probe`, `cip0004-apply-probe-sfv`

## Progress Updates

### 2026-09-04

Task created from dual-base apply probe findings (Ready for review before implementation).

### 2026-09-04 (later)

Completed in `convert.py`: chrome strip + unwrap, specialised Dates/registration/schedule/event_bios extracts, fixtures and unit tests; live CFP/invited spot-check clean of year-switcher chrome with bios preserved.
