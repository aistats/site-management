---
id: "2026-09-02_society-site-template-notes"
title: "Align aistats.github.io create-from-template notes with refreshed stub"
status: "Ready"
priority: "Low"
created: "2026-09-02"
last_updated: "2026-09-02"
category: "documentation"
related_cips: ["0001"]
owner: "Neil Lawrence"
dependencies: ["2026-09-02_stub-smoke-check"]
tags:
- backlog
- documentation
- cip0001
---

# Task: Update society-site template instructions

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

After the stub refresh lands, update `aistats.github.io` README create-from-template steps if they still assume old paths (`doc/`, HTML submission pages, or outdated first edits). Keep instructions aligned with `_config.yml` placeholders and `_doc/` organiser guides.

## Acceptance Criteria

- [ ] Society-site README steps match the refreshed stub workflow
- [ ] Mentions of obsolete stub paths removed or corrected

## Implementation Notes

Work happens in the `aistats.github.io` repo, not in `stub`. Depends on smoke-check so instructions describe the final shape.

## Related

- CIP: 0001
- Repo: aistats.github.io

## Progress Updates

### 2026-09-02

Task created at Ready status after CIP-0001 acceptance.
