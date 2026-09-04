---
id: "2026-09-04_cip0004-convert-pipeline"
title: "CIP-0004: Fetch, extract, pandoc, and post-process pipeline"
status: "Ready"
priority: "High"
created: "2026-09-04"
last_updated: "2026-09-04"
category: "infrastructure"
related_cips: ["0004"]
owner: "Neil Lawrence"
dependencies: ["2026-09-04_cip0004-manifest"]
tags:
- backlog
- cip0004
- sync
- pandoc
---

# Task: Fetch, extract, pandoc, and post-process pipeline

## Description

Implement the conversion half of `sync-virtual`: fetch virtual HTML (or load fixtures), extract the main body per strategy, convert with pandoc, and post-process (front matter injection, link rewrite hooks, optional asset download stubs). Output is a **candidate** markdown body—no year-site writes yet.

## Acceptance Criteria

- [ ] CLI or library entrypoint can convert a mapped page id to candidate markdown
- [ ] Chrome (nav/footer/cookies) stripped via configured extract strategy
- [ ] Pandoc used for HTML→markdown; clear error if pandoc missing
- [ ] Front matter from manifest applied without altering converted body prose
- [ ] Offline fixture replay supported for at least one page

## Implementation Notes

Preserve wording; no paraphrase. Image fetch for invited speakers can be stubbed if needed and completed with apply/validation tasks.

## Related

- CIP: 0004

## Progress Updates

### 2026-09-04

Task created at Ready after CIP-0004 acceptance.
