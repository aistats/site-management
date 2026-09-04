---
id: "2026-09-04_cip0004-apply-flags"
title: "CIP-0004: Opt-in fill-missing and apply-from-virtual"
status: "Ready"
priority: "High"
created: "2026-09-04"
last_updated: "2026-09-04"
category: "features"
related_cips: ["0004"]
owner: "Neil Lawrence"
dependencies: ["2026-09-04_cip0004-compare-report"]
tags:
- backlog
- cip0004
- sync
- apply
---

# Task: Opt-in fill-missing and apply-from-virtual

## Description

Add explicit write paths: `--fill-missing` creates absent mapped pages from converted virtual content; `--apply-from-virtual [--only id…]` overwrites selected existing pages. Log every path that will be written. Default remains no write.

## Acceptance Criteria

- [ ] Without apply flags, year-site tree unchanged (regression covered with fixtures)
- [ ] `--fill-missing` only creates pages that do not already exist
- [ ] `--apply-from-virtual` requires explicit selection (global or `--only`) before overwriting
- [ ] Console/report lists files written
- [ ] Rejects or no-ops clearly when pandoc/candidate missing for a selected id

## Implementation Notes

Year site stays primary: make overwrite hard to do accidentally (confirm flag naming matches CIP CLI sketch).

## Related

- CIP: 0004

## Progress Updates

### 2026-09-04

Task created at Ready after CIP-0004 acceptance.
