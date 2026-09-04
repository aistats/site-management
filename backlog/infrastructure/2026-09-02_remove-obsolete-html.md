---
id: "2026-09-02_remove-obsolete-html"
title: "Remove or underscore obsolete stub HTML pages"
status: "Completed"
priority: "High"
created: "2026-09-02"
last_updated: "2026-09-02"
category: "infrastructure"
related_cips: ["0001"]
owner: "Neil Lawrence"
dependencies: ["2026-09-02_markdown-page-stubs"]
tags:
- backlog
- cleanup
- cip0001
---

# Task: Remove obsolete HTML pages

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Stop shipping the 2020 live HTML pages that recent conferences no longer use. Delete `index.html` once `index.md` exists. Underscore venue helpers (`_accommodation.html`, `_local.html`) if kept as starting points; otherwise delete `accommodation.html`, `local.html`, `registration.html`, `submission.html`, and `submit.html`.

## Acceptance Criteria

- [x] `index.html` removed (home is `index.md`)
- [x] No live `accommodation.html`, `local.html`, `submission.html`, or `submit.html` in the nav surface
- [x] Registration is markdown (`registration.md`) rather than the old HTML page
- [x] Any retained venue helpers are underscored and not linked from default nav

## Implementation Notes

Prefer underscore over delete for accommodation/local if `_doc` still references them as optional starting points.

## Related

- CIP: 0001

## Progress Updates

### 2026-09-02

Task created at Ready status after CIP-0001 acceptance.

### 2026-09-02

Implemented on branch `cip0001-refresh-stub`.
