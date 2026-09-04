---
id: "2026-09-04_cip0004-config-surgical"
title: "CIP-0004: Surgical _config.yml merge and deadline name aliases"
status: "Completed"
priority: "High"
created: "2026-09-04"
last_updated: "2026-09-04"
category: "bugs"
related_cips: ["0004"]
owner: "Neil Lawrence"
dependencies: ["2026-09-04_cip0004-config-yaml-patch"]
tags:
- backlog
- cip0004
- sync
- config
---

# Task: Surgical `_config.yml` merge and deadline name aliases

## Description

`--apply-config-patch` currently round-trips the whole year-site `_config.yml` through `yaml.safe_dump`, which strips comments and reformats unrelated keys. The 2026 year site also uses deadline `name` strings that differ from the stub schema, so most proposed Dates rows never merge.

Replace full dump with an in-place surgical merge (venue, location, matched deadline fields only). Add alias maps (manifest or code) from virtual Dates labels → year-site deadline names, including stub-shaped and 2026-shaped variants.

## Acceptance Criteria

- [x] Applying a config patch leaves comments and unrelated keys byte-stable aside from intentional field updates
- [x] Chairs (and other non-target keys) remain unchanged (regression test)
- [x] Alias map covers at least: abstract/paper submission, author response start/end, decisions, camera-ready, journal-track, workshops, conference dates
- [x] 2026 `_config.yml` labels such as `Deadline for camera-ready papers` and split author-response rows can receive dates
- [x] Default remains proposal-only; `--apply-config-patch` still required to write
- [x] Unit test: round-trip fixture config with comments survives apply

## Implementation Notes

Prefer line/structured edit or ruamel-style comment preservation if we add a dependency; otherwise targeted replacements on known keys after parse-for-values + rewrite-only-those-blocks. Document aliases in `scripts/sync_virtual/README.md`.

Do not auto-fix `conference.dates` year typos unless mapped from virtual meeting dates with an explicit rule.

## Related

- CIP: 0004
- Probe note: full dump on `aistats2026` was reverted; surgical venue/location/two deadlines applied by hand on `cip0004-apply-probe`

## Progress Updates

### 2026-09-04

Task created from config-apply probe failure (Ready for review before implementation).

### 2026-09-04 (later)

Completed: `apply_proposal_to_config_text` / `_file`, `DEADLINE_APPLY_TARGETS` aliases, unit test for comment preservation.
