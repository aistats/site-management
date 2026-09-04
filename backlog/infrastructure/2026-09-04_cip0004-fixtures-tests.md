---
id: "2026-09-04_cip0004-fixtures-tests"
title: "CIP-0004: Fixtures and sync tests (including no-clobber)"
status: "Ready"
priority: "High"
created: "2026-09-04"
last_updated: "2026-09-04"
category: "infrastructure"
related_cips: ["0004"]
owner: "Neil Lawrence"
dependencies: ["2026-09-04_cip0004-compare-report", "2026-09-04_cip0004-apply-flags"]
tags:
- backlog
- cip0004
- sync
- testing
---

# Task: Fixtures and sync tests (including no-clobber)

## Description

Add HTML fixtures under `scripts/sync_virtual/fixtures/`, golden conversion snippets, and automated tests for match / drift / missing classifications, default no-clobber behaviour, and apply-only-selected paths.

## Acceptance Criteria

- [ ] Fixtures for at least CoC, CFP fragment, and one FAQ (plus optional Invited)
- [ ] Conversion golden tests (stable candidate markdown modulo allowed normalisation)
- [ ] Default sync leaves a dirty year-site fixture byte-identical
- [ ] Drift fixture produces report entry, diff, and virtual-update-request section
- [ ] Apply-mode test changes only `--only`-listed paths
- [ ] Pandoc missing → clear skip/fail message

## Implementation Notes

May use pytest. Keep fixtures small enough for git.

## Related

- CIP: 0004

## Progress Updates

### 2026-09-04

Task created at Ready after CIP-0004 acceptance.
