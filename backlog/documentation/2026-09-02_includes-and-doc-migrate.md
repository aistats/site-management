---
id: "2026-09-02_includes-and-doc-migrate"
title: "Add _includes and migrate doc/ to _doc/"
status: "Completed"
priority: "High"
created: "2026-09-02"
last_updated: "2026-09-02"
category: "documentation"
related_cips: ["0001"]
owner: "Neil Lawrence"
dependencies: ["2026-09-02_modernise-config-readme"]
tags:
- backlog
- documentation
- cip0001
---

# Task: Add includes and migrate organiser docs

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Copy sanitised `_includes/banner.html`, `listdates.html`, and `tabledates.html` from aistats2025. Move organiser guides from `doc/` to `_doc/` so they are not published as site pages, and fix internal links for the new markdown page names.

## Acceptance Criteria

- [x] `_includes/banner.html`, `_includes/listdates.html`, `_includes/tabledates.html` exist
- [x] Organiser docs live under `_doc/` (not `doc/`)
- [x] Internal `_doc` links updated for new page filenames where they mention old HTML names
- [x] No published `doc/` directory remains (or it is empty and removed)

## Implementation Notes

Can proceed in parallel with markdown page stubs once config/README is done. Keep includes generic (no 2025 venue hardcoding beyond theme expectations).

## Related

- CIP: 0001

## Progress Updates

### 2026-09-02

Task created at Ready status after CIP-0001 acceptance.

### 2026-09-02

Implemented on branch `cip0001-refresh-stub`.
