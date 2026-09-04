---
id: "2026-09-04_cip0004-site-contract-ci"
title: "CIP-0004: Stub year-site contract checks and PR CI"
status: "Ready"
priority: "Medium"
created: "2026-09-04"
last_updated: "2026-09-04"
category: "infrastructure"
related_cips: ["0004", "0001"]
owner: "Neil Lawrence"
dependencies:
- "2026-09-04_cip0004-extract-chrome"
tags:
- backlog
- cip0004
- cip0001
- stub
- ci
- testing
---

# Task: Stub year-site contract checks and PR CI

## Description

Add a **Tier A** automated site-contract checker that year repos (starting with `aistats2026`) and `aistats/stub` can run on PRs—no network, no pandoc. Goal: catch incomplete sync PRs, virtual layout chrome leaking into markdown, and basic `_config.yml` year consistency before merge (including updates to [aistats2026#1](https://github.com/aistats/aistats2026/pull/1)).

Canonical script and workflow live in **stub**; year sites copy or vendor the same check. Deeper sync faithfulness (fixture/live convert) stays in `site-management` (`sync_virtual` unit tests), not in this task.

Extends the spirit of the completed CIP-0001 stub smoke checklist (`2026-09-02_stub-smoke-check`) into something reusable and CI-runnable.

## Acceptance Criteria

- [ ] `stub/scripts/check_year_site.py` (or equivalent) implements at least:
  - Required archival page paths present (aligned with stub / CIP-0004 manifest inventory)
  - Forbidden chrome markers absent in `*.md` (`child-menu`, `Select Year:`, and similar)
  - `_config.yml`: `conference.year` consistent with dated `conference.dates` entries when both present
  - Exit non-zero on failure with clear messages
- [ ] Stub mode: placeholder/year-city pollution checks retained or ported from CIP-0001 smoke intent
- [ ] GitHub Action workflow in `stub` runs the contract script on PRs (optional `jekyll build` as a separate job or flag)
- [ ] Same checker runnable in `aistats2026` (copied script and/or workflow) so PR #1 / sync branches get a red/green signal
- [ ] Short note in stub `_doc/` pointing at how year sites enable the check
- [ ] Document that Tier C faithfulness remains in `site-management` (link to `scripts/sync_virtual/`)

## Implementation Notes

Keep Tier A cheap and deterministic. Do not require live virtual.aistats.org in year-site CI.

Suggested follow-ups (out of scope here unless trivial): optional Jekyll build job; length/fingerprint paraphrase heuristics in site-management only.

## Related

- CIP: 0004, 0001
- PR: [aistats2026#1](https://github.com/aistats/aistats2026/pull/1)
- Related backlog: `2026-09-02_stub-smoke-check` (manual predecessor), `2026-09-04_cip0004-validate-2026`

## Progress Updates

### 2026-09-04

Task created at Ready after dual-base sync probes and extract-chrome fix; Tier A CI agreed before PR update.
