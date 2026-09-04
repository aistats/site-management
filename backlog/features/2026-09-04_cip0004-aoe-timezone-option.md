---
id: "2026-09-04_cip0004-aoe-timezone-option"
title: "CIP-0004: Optional AoE timezone rendering in listdates"
status: "Ready"
priority: "Low"
created: "2026-09-04"
last_updated: "2026-09-04"
category: "features"
related_cips: ["0004"]
owner: "Neil Lawrence"
dependencies:
- "2026-09-04_cip0004-dates-include-config"
tags:
- backlog
- cip0004
- jekyll
- theme
- dates
---

# Task: Optional AoE timezone rendering in listdates

## Description

Today `listdates.html` assumes all deadlines are Anywhere on Earth and says so in a single blurb. Some deadlines need a clock time in UTC (or venue local time). Prefer a theme/include option such as site `timezone: AOE` and/or per-deadline `tz: AOE|UTC|…` so config stores real dates/times and the include chooses the label — rather than stuffing “Anywhere on Earth” into YAML values.

## Acceptance Criteria

- [ ] Documented config shape for site-level and optional per-deadline timezone
- [ ] `listdates.html` (stub and/or `jekyll-theme`) renders AoE vs timed zones without free-text date strings
- [ ] Existing year sites that rely on the global AoE blurb keep working with defaults
- [ ] Sync config apply continues to write parseable dates only

## Implementation Notes

Likely lands in `aistats/jekyll-theme` and/or stub `_includes/listdates.html`. Keep CIP-0004 sync out of the theme change except for not writing AOE into values.

## Related

- CIP: 0004
- Depends on content/config cleanup: `2026-09-04_cip0004-dates-include-config`

## Progress Updates

### 2026-09-04

Task created at Ready; deferred until PR content uses parseable dates.
