---
id: "2026-09-04_cip0004-compare-report"
title: "CIP-0004: Compare-first report, diffs, and virtual update request"
status: "Ready"
priority: "High"
created: "2026-09-04"
last_updated: "2026-09-04"
category: "features"
related_cips: ["0004"]
owner: "Neil Lawrence"
dependencies: ["2026-09-04_cip0004-convert-pipeline"]
tags:
- backlog
- cip0004
- sync
- report
---

# Task: Compare-first report, diffs, and virtual update request

## Description

Default sync mode: compare candidate (from virtual) to existing `aistats20XX` pages, classify each mapped page (missing / match / drift / year-only), emit unified diffs, and write a **virtual update request** artefact for drift where the year site should remain authoritative. Must not modify year-site files.

## Acceptance Criteria

- [ ] Default CLI run writes a sync report without changing year-site content
- [ ] Classifications implemented per CIP-0004 table
- [ ] Drift pages produce a non-empty unified diff (body compare; front matter ignorable)
- [ ] `virtual-update-request.md` (or equivalent) lists drifted pages with year URL, virtual URL, and excerpts suitable to send to the virtual operator
- [ ] Match / missing / year-only appear clearly in the summary

## Implementation Notes

Normalise whitespace/links as needed for stable compare, but do not rewrite prose for “sameness.”

## Related

- CIP: 0004

## Progress Updates

### 2026-09-04

Task created at Ready after CIP-0004 acceptance.
