---
id: "2026-09-04_cip0004-fixtures-tests"
title: "CIP-0004: Fixtures and no-clobber tests"
status: "Completed"
priority: "Medium"
created: "2026-09-04"
last_updated: "2026-09-04"
category: "infrastructure"
related_cips: ["0004"]
owner: "Neil Lawrence"
dependencies: ["2026-09-04_cip0004-convert-pipeline", "2026-09-04_cip0004-compare-report", "2026-09-04_cip0004-apply-flags"]
tags:
- backlog
- cip0004
- sync
- tests
---

# Task: Fixtures and no-clobber tests

## Description

Store HTML fixtures under `scripts/sync_virtual/fixtures/` and add tests covering conversion faithfulness, classification (match/drift/missing), default no-write behaviour, and apply-flag gating.

## Acceptance Criteria

- [x] At least one prose fixture and Dates/Hotels fixtures for config path
- [x] Tests assert fixture wording survives convert
- [x] Default sync leaves year-site bytes unchanged
- [x] `--apply-from-virtual` without `--only` refuses overwrite

## Implementation Notes

Run with: `.venv-vibesafe/bin/python -m unittest scripts.sync_virtual.test_sync_virtual -v`

## Related

- CIP: 0004

## Progress Updates

### 2026-09-04

Completed with `test_sync_virtual.py` and fixtures `call-for-papers.html`, `dates.html`, `accommodation.html`.
