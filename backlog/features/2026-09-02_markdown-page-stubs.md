---
id: "2026-09-02_markdown-page-stubs"
title: "Add markdown page stubs and updated committee.html"
status: "Completed"
priority: "High"
created: "2026-09-02"
last_updated: "2026-09-02"
category: "features"
related_cips: ["0001"]
owner: "Neil Lawrence"
dependencies: ["2026-09-02_modernise-config-readme"]
tags:
- backlog
- jekyll
- cip0001
---

# Task: Add markdown page stubs

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Add the standard conference markdown pages with front matter and short TODO bodies, and replace `committee.html` with the 2025/2026 `layout: default` chairs loop. Add `index.md` to replace the old home HTML once obsolete pages are removed.

## Acceptance Criteria

- [x] Present: `index.md`, `call-for-papers.md`, `code-of-conduct.md`, `dates.md`, `faqs.md`, `reviewer_guidelines.md`, `ac_guidelines.md`, `invited.md`, `schedule.md`, `awards.md`, `camera.md`, `poster.md`, `registration.md`, `other.md`
- [x] `dates.md` includes `{% include listdates.html %}`
- [x] `other.md` uses `layout: other` and `hide: true`
- [x] `committee.html` matches the 2025/2026 chairs-rendering pattern
- [x] Page weights roughly match recent nav practice

## Implementation Notes

Bodies should be placeholders (headings + TODO), not copied 2025 prose. Front matter titles/layouts/weights from CIP-0001.

## Related

- CIP: 0001

## Progress Updates

### 2026-09-02

Task created at Ready status after CIP-0001 acceptance.

### 2026-09-02

Implemented on branch `cip0001-refresh-stub`.
