---
id: "2026-09-04_cip0004-dates-include-config"
title: "CIP-0004: Prefer listdates include and parseable config deadlines"
status: "Completed"
priority: "High"
created: "2026-09-04"
last_updated: "2026-09-04"
category: "bugs"
related_cips: ["0004"]
owner: "Neil Lawrence"
dependencies:
- "2026-09-04_cip0004-validate-2026"
tags:
- backlog
- cip0004
- sync
- dates
- jekyll
---

# Task: Prefer `listdates` include and parseable config deadlines

## Description

The CIP-0004 live apply dumped virtual Dates tables and AOE display strings into year-site markdown and `_config.yml`. Year sites (stub / 2024 / 2025) instead:

1. Render deadlines with `{% include listdates.html %}` (optional `types=` filter).
2. Store parseable `date` / `enddate` / `time` values in `conference.deadlines` (e.g. `2 October 2025`), not `Oct 02 '25 (Anywhere on Earth)`.
3. Pull venue, location, and meeting days from `conference.*` via Liquid where the page is archival chrome (home, CFP lead-in, registration/schedule summaries).

AoE is already stated once in `listdates.html`. Do not embed “Anywhere on Earth” inside config date fields.

## Acceptance Criteria

- [x] `dates.md` uses the include (stub shape), not a virtual HTML/markdown table
- [x] Call for Papers / AC / Reviewer “Key dates” / “Important Dates” sections use the include
- [x] Registration and schedule pages do not paste virtual meeting-date tables; they summarise from config and link out for interactive detail
- [x] `_config.yml` deadlines are parseable by Jekyll `date` filters; no AOE suffix in values
- [x] Home / CFP lead-in use `site.conference.location` (and dates/venue) rather than hard-coded “Morocco” only
- [x] Sync tooling backlog note: `dates` / key-dates extracts stay `prefer_year` or post-process to include (follow-up in sync_virtual)
- [x] PR #1 content updated

## Implementation Notes

Content fix lands on `aistats2026` `sync-from-virtual`. Sync pipeline: `dates` (and `awards`, `index`) use `on_drift: prefer_year`; `--apply-from-virtual` refuses those pages. Optional AoE timezone option in listdates is `2026-09-04_cip0004-aoe-timezone-option`.

## Related

- CIP: 0004
- PR: [aistats2026#1](https://github.com/aistats/aistats2026/pull/1)
- Examples: `aistats2025/dates.md`, `aistats2025/call-for-papers.md`, `stub/_includes/listdates.html`

## Progress Updates

### 2026-09-04

Task created after PR review of faithful sync dump.

### 2026-09-04 (later)

Patched PR content on `sync-from-virtual`. Sync_virtual normalise/prefer_year follow-up left open.

### 2026-09-04 (evening)

Closed prefer_year follow-up: dates/awards/index marked prefer_year; apply refuses overwrite.
