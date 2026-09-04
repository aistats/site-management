---
id: "2026-09-04_cip0004-config-yaml-patch"
title: "CIP-0004: Reviewable deadline and venue YAML patches"
status: "Ready"
priority: "Medium"
created: "2026-09-04"
last_updated: "2026-09-04"
category: "features"
related_cips: ["0004"]
owner: "Neil Lawrence"
dependencies: ["2026-09-04_cip0004-convert-pipeline"]
tags:
- backlog
- cip0004
- sync
- config
---

# Task: Reviewable deadline and venue YAML patches

## Description

Parse virtual Dates (and Hotels where useful) into proposed patches for `conference.dates`, `deadlines`, and venue fields in `_config.yml`. Emit a reviewable diff/patch; do not silently overwrite chairs or unrelated config. Same primary-site rules: report by default, apply only with an explicit flag.

## Acceptance Criteria

- [ ] Dates tables → structured deadline candidates aligned with stub `_config.yml` deadline fields
- [ ] Venue/location fields proposed from Hotels / conference header where available
- [ ] Default output is a patch or side-by-side proposal, not an in-place overwrite
- [ ] Chairs and unrelated keys left untouched
- [ ] Explicit apply path documented (flag or separate subcommand)

## Implementation Notes

Separate from pandoc prose path. Prefer merging known keys only.

## Related

- CIP: 0004

## Progress Updates

### 2026-09-04

Task created at Ready after CIP-0004 acceptance.
