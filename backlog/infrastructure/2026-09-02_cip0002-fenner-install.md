---
id: "2026-09-02_cip0002-fenner-install"
title: "Phase B: Install jekyll-fenner CiteProc stack into aistats/jekyll-theme"
status: "Proposed"
priority: "High"
created: "2026-09-02"
last_updated: "2026-09-02"
category: "infrastructure"
related_cips: ["0002"]
owner: "Neil Lawrence"
dependencies: ["2026-09-02_cip0002-theme-tidy-jekyll"]
tags:
- backlog
- jekyll-theme
- fenner
- citeproc
- cip0002
---

# Task: Fenner CiteProc install

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

Install Fenner-owned publication/cite/SEO templates into `aistats/jekyll-theme` from `~/lawrennd/jekyll-fenner` (copy mode). Preserve AISTATS chrome; use path-2 adapter strategy where needed; smoke-build theme and a consumer site.

## Acceptance Criteria

- [ ] Fenner install applied using ownership manifest
- [ ] Chrome paths not overwritten by install
- [ ] Paper/cite pages render authors, venue, abstract, cite/export, SEO metas
- [ ] `citeproc.yaml` (or equivalent) remains coherent
- [ ] Theme + at least one consumer smoke build OK

## Implementation Notes

```
FENNER_ROOT=~/lawrennd/jekyll-fenner ./script/install /path/to/aistats/jekyll-theme
```

(Use current Fenner install entrypoint if the path differs.) Resolve conflicts by hand; prefer thin `paper_abstract` adapter over a risky full path-1 cutover.

## Related

- CIP: 0002
- Fenner: ~/lawrennd/jekyll-fenner

## Progress Updates

### 2026-09-02

Task created (Proposed) as Phase B of consolidated CIP-0002.
