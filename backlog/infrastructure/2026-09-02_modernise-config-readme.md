---
id: "2026-09-02_modernise-config-readme"
title: "Modernise stub _config.yml and README for aistats/jekyll-theme"
status: "Completed"
priority: "High"
created: "2026-09-02"
last_updated: "2026-09-02"
category: "infrastructure"
related_cips: ["0001"]
owner: "Neil Lawrence"
dependencies: ["2026-09-02_cip0001-branch"]
tags:
- backlog
- jekyll
- cip0001
---

# Task: Modernise config and README

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Rewrite `_config.yml` to the 2023–2025 contract: `remote_theme: aistats/jekyll-theme`, `banner_title`, `repository`, `20XX` placeholders, modern chair roles, and richer deadline field examples. Update `README.md` so it describes this repo as the conference template and points at the correct theme and `_doc/` workflow.

## Acceptance Criteria

- [x] No reference to `lawrennd/proceedings` in `_config.yml` or `README.md`
- [x] `_config.yml` includes `banner_title`, `repository`, and `20XX` placeholders only (no real venue year copy)
- [x] Chair stubs include General, Program, Workflow, Local, Publication, Sponsorship, D&I/Inclusivity, Journal-to-Conference
- [x] README states template purpose and links organiser docs under `_doc/` (or notes the pending migrate task)

## Implementation Notes

Use aistats2025 `_config.yml` as the shape reference; strip real people, dates, and Thailand-specific content.

## Related

- CIP: 0001

## Progress Updates

### 2026-09-02

Task created at Ready status after CIP-0001 acceptance.

### 2026-09-02

Implemented on branch `cip0001-refresh-stub`.
