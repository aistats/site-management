---
id: "2026-09-02_cip0002-branding-style"
title: "Phase C: Clarify or retire style: aistats branding switch"
status: "Proposed"
priority: "Medium"
created: "2026-09-02"
last_updated: "2026-09-02"
category: "infrastructure"
related_cips: ["0002"]
owner: "Neil Lawrence"
dependencies: ["2026-09-02_cip0002-fenner-install"]
tags:
- backlog
- jekyll-theme
- branding
- cip0002
---

# Task: Theme branding contract

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Replace or clarify the magic `style: aistats` contract (default when unset, rename to something like `brand:`, or document a migration). Update stub `_config.yml` / README accordingly. Ship a migration path for existing year sites.

## Acceptance Criteria

- [ ] Branding contract documented and implemented in the theme
- [ ] Stub config/docs updated; chairs know what to set (if anything)
- [ ] Existing sites with `style: aistats` still work through transition
- [ ] Past-meetings listing, CSS, favicon, and style includes still resolve for AISTATS

## Implementation Notes

Do after Fenner install so branding edits do not fight cite-stack ownership. Options: default unset → aistats; rename key; split themes — pick one when starting the task.

## Related

- CIP: 0002

## Progress Updates

### 2026-09-02

Task created (Proposed) as Phase C of consolidated CIP-0002.
