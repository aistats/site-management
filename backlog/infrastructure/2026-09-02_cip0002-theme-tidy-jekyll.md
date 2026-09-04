---
id: "2026-09-02_cip0002-theme-tidy-jekyll"
title: "Phase A: Tidy aistats/jekyll-theme and confirm Jekyll/Pages compatibility"
status: "Proposed"
priority: "High"
created: "2026-09-02"
last_updated: "2026-09-02"
category: "infrastructure"
related_cips: ["0002"]
owner: "Neil Lawrence"
dependencies: []
tags:
- backlog
- jekyll-theme
- cip0002
---

# Task: Theme tidy and Jekyll compatibility

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

On `aistats/jekyll-theme`, inventory and remove or quarantine unused Minima sample content, align gemspec/Gemfile identity with the real theme, and confirm local/Pages builds against current Jekyll. Document the supported Jekyll range. Do not change Fenner-owned cite paths yet.

## Acceptance Criteria

- [ ] Branch exists on `aistats/jekyll-theme` for CIP-0002 work
- [ ] Gemspec/identity no longer presents as stock Minima in a misleading way (without breaking `remote_theme`)
- [ ] Unused sample content removed or clearly quarantined
- [ ] `bundle exec jekyll build` (or documented Pages-equivalent) succeeds; deprecations that block builds are fixed
- [ ] Supported Jekyll/Pages range noted in theme README or short docs

## Implementation Notes

Keep chrome (`_includes/aistats/`, Sass/CSS skins, headers/footers) intact for later phases.

## Related

- CIP: 0002

## Progress Updates

### 2026-09-02

Task created (Proposed) as Phase A of consolidated CIP-0002.
