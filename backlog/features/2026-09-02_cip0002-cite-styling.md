---
id: "2026-09-02_cip0002-cite-styling"
title: "Phase D: Refresh cite presentation styling"
status: "Proposed"
priority: "Medium"
created: "2026-09-02"
last_updated: "2026-09-02"
category: "features"
related_cips: ["0002"]
owner: "Neil Lawrence"
dependencies: ["2026-09-02_cip0002-branding-style"]
tags:
- backlog
- jekyll-theme
- fenner
- citeproc
- styling
- cip0002
---

# Task: Cite presentation styling

> **Note**: Backlog tasks are DOING the work defined in CIPs (HOW).  
> Use `related_cips` to link to CIPs. Don't link directly to requirements (bottom-up pattern).

## Description

After Fenner is installed and branding is settled, refresh the visual and interaction design of cite affordances (Cite this paper block, copy buttons, export panels) in theme CSS and, where shared, Fenner templates.

## Acceptance Criteria

- [ ] Cite UI reviewed on a Fenner-installed AISTATS build
- [ ] Theme and/or Fenner upstream presentation updates landed
- [ ] BibTeX/APA/RIS/EndNote export content unchanged (unless a Fenner CIP expands behaviour)
- [ ] Smoke-test cite/copy UI on stub or consumer site

## Implementation Notes

Prefer theme Sass for AISTATS-only chrome; push shared markup/CSS to Fenner when other orgs benefit. Depends on branding so cite chrome matches the new brand contract.

## Related

- CIP: 0002
- Fenner: ~/lawrennd/jekyll-fenner/_includes/cite-as.html and copy_* includes

## Progress Updates

### 2026-09-02

Task created (Proposed) as Phase D of consolidated CIP-0002.
