# sync_virtual

Compare-first sync between [virtual.aistats.org](https://virtual.aistats.org/) and yearly `aistats20XX` GitHub Pages sites (CIP-0004).

The year site is **primary**. Default mode reports drift; it does not overwrite existing pages.

## Layout

```text
scripts/sync_virtual/
  README.md                 # this file (schema + usage)
  manifests/
    aistats2026.yml         # default 2026 inventory
  fixtures/                 # offline HTML snapshots (tests)
  manifest.py               # load + validate YAML
  convert.py                # fetch → extract → pandoc → post-process
  sync_virtual.py           # CLI entrypoint
```

Year repos may ship an optional override at the repo root:

```text
aistats20XX/virtual-sync.yml
```

When present, that file is merged over (or replaces) the default year manifest for that run. Prefer declaring page URLs and policy there when a year diverges from the shared inventory.

## Manifest schema

Top-level fields:

| Field | Required | Meaning |
|-------|----------|---------|
| `year` | yes | Conference year (integer), e.g. `2026` |
| `virtual_base` | yes | Origin for relative `url` values, usually `https://virtual.aistats.org` |
| `target_repo` | yes | Path to the year-site checkout (relative to this package or absolute) |
| `pages` | yes | List of page entries (see below) |
| `report_dir` | no | Default report output under the year repo or cwd (`sync-report/`) |
| `link_only` | no | Paths that stay links-only (calendar, papers, checkout); never body-imported |

Each `pages[]` entry:

| Field | Required | Meaning |
|-------|----------|---------|
| `id` | yes | Stable short name (`call-for-papers`, `invited`, …) |
| `url` | yes* | Path or absolute URL on virtual (`*` omit only for `year-only` / config-only rows) |
| `out` | yes | Relative path in the year repo (`call-for-papers.md`, `_config.yml`, …) |
| `extract` | yes | Named extract strategy (see below) |
| `required` | no | If true (default false), always appear in the sync report |
| `on_drift` | no | `report` (default) \| `prefer_year` \| `prefer_virtual` — classification preference only; apply still needs CLI flags |
| `front_matter` | no | Jekyll front matter map injected on convert / apply |
| `assets` | no | Asset policy name (`speaker_images`, …) or omit |
| `include` | no | Extra flags (`index` needs `--include-index` to convert) |

`on_drift` never implies overwrite. `prefer_virtual` only steers the virtual update request / apply suggestions; writing still requires `--apply-from-virtual` (or `--fill-missing` for absent files).

## Extract strategies

| Name | Intent |
|------|--------|
| `main_after_nav` | Keep the primary article body after stripping nav, year switcher, empty Bootstrap shells |
| `event_bios` | Invited Talk event cards: titles, bios, images; drop badges/bookmarks. **Not** for awards announcement prose — the Award event list is paper abstracts; keep `awards.md` as `prefer_year` |
| `dates_tables` | Paper/workshop/journal (+ main conference) deadline tables from Dates |
| `hotels_venue` | Hotels / venue prose after chrome strip |
| `registration_blocks` | Registration note + meeting dates + Attendees deadline rows (not full Dates dump) |
| `schedule_summary` | Meeting dates + main conference start + calendar link |
| `home_announcements` | Selective home/index announcement blocks; high clobber risk — gated (`prefer_year`; apply refused) |
| `config_merge` | Structured fields only (deadlines, venue); no pandoc body ownership |
| `none` | No fetch/convert (year-only placeholder row for reporting) |

`on_drift: prefer_year` pages are never overwritten by `--apply-from-virtual` (apply skips them). Use report/drift diffs and virtual-update-request instead.

## Default inventories

- [`manifests/aistats2026.yml`](manifests/aistats2026.yml) — main-site inventory from CIP-0004 / stub / `sync-from-virtual`

## CLI

Use the VibeSafe venv (PyYAML + BeautifulSoup):

```bash
.venv-vibesafe/bin/pip install -r scripts/sync_virtual/requirements.txt

.venv-vibesafe/bin/python scripts/sync_virtual/__main__.py validate

.venv-vibesafe/bin/python scripts/sync_virtual/__main__.py convert \
  --id call-for-papers \
  --fixture scripts/sync_virtual/fixtures/call-for-papers.html

# Default: compare + report only (no year-site writes)
.venv-vibesafe/bin/python scripts/sync_virtual/__main__.py sync \
  --only call-for-papers \
  --fixtures-dir scripts/sync_virtual/fixtures \
  --offline \
  --report-dir /tmp/sync-report-test

# Opt-in writes
... sync --fill-missing --only call-for-papers ...
... sync --apply-from-virtual --only call-for-papers ...
```

Year override: `aistats20XX/virtual-sync.yml` (full replacement when `--with-year-override`).

## Config patches

`--apply-config-patch` uses a **surgical text merge**: only `venue`, `location`, and matched deadline `date`/`enddate`/`time` lines change. Comments and chairs are preserved. Deadline name aliases cover stub-shaped and 2026-shaped labels (see `DEADLINE_APPLY_TARGETS` in `config_patch.py`).
