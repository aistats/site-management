# CIP-0003 evidence notes

Synthesised 2026-09-02 from `git log --format='%ad|%s' --date=short` on `aistats2023`–`aistats2025`, with week offsets from conference start, plus deadline blocks in each year’s `_config.yml`.

## Conference starts

| Year | Start | Source |
|------|-------|--------|
| 2023 | 2023-04-25 | `index.md` (“April 25 - April 27, 2023”) |
| 2024 | 2024-05-02 | `_config.yml` `conference.dates` |
| 2025 | 2025-05-03 | `_config.yml` `conference.dates` |

First Valencia year in this window: **2023**. AISTATS 2026 was incomplete at analysis time (meeting dates in config still showed May 2025 placeholders).

## Repo birth (weeks before start)

| Year | First commit | Weeks before |
|------|--------------|--------------|
| 2023 | 2022-08-03 | 37 |
| 2024 | 2023-07-14 | 41 |
| 2025 | 2024-07-29 | 39 |

## Keyword-bucket earliest / latest pre-conference hits

Buckets are commit-subject regexes (noisy; treat as qualitative).

### 2023

| Theme | Earliest | Latest (pre) |
|-------|----------|--------------|
| CFP / deadlines | 37w | 5w |
| Committee | 37w | 6w |
| Review / rebuttal / guidelines | 37w | 11w |
| Registration | 14w | 9w |
| Invited | 10w | 10w |
| Schedule / programme | 37w (noise) / real schedule ~4–9w | 4w |
| Camera / paper pack | 37w | 10w |
| Awards | 9w | 9w |

### 2024

| Theme | Earliest | Latest (pre) |
|-------|----------|--------------|
| CFP / deadlines | 35w | 12w |
| Committee | 40w | 1w |
| Review / rebuttal | 33w | 20w |
| Registration | 40w | 20w |
| Invited | 1w | 1w |
| Schedule / programme | 3w | 1w |
| Camera | 12w | 9w |
| Awards | post-conf only in log sample | — |

### 2025

| Theme | Earliest | Latest (pre) |
|-------|----------|--------------|
| CFP / deadlines | 37w | 21w |
| Committee | 38w | 26w |
| Review / rebuttal / guidelines | 34w | 1w |
| Registration | 17w | 4w |
| Invited | 6w | 2w |
| Schedule / programme | 4w | 2w |
| Camera / paper pack | 34w | 0w |
| Awards | 4w | 1w |

Monthly commit mass for 2025 peaked in **April 2025** (46 commits) immediately before a 3 May start — evidence for schedule/programme lateness.

## Deadline fields with dates (snapshot at analysis)

### 2023 (`_config.yml`)

- Abstract submission: 21 November 2022  
- Paper submission: 19 January 2023  
- Supplementary materials: 17 March 2023  
- Reviews released: 30 March 2023  
- Author rebuttal / decisions: 11 April 2023  
- Early registration: 17 March 2023  

### 2024

- Abstract: 6 October 2023  
- Paper submission: 16 October 2023  
- Appendix: 23 October 2023  
- Reviews released: 27 November 2023  
- Author rebuttals: 5 December 2023  
- Decision notifications: 19 January 2024  
- Early registration: 25 March 2024  

### 2025 (richer chain)

- Submission server open: 3 October 2024  
- Abstract: 8 October 2024  
- Paper submission: 17 October 2024  
- Appendix: 22 October 2024  
- Reviews released: 27 November 2024  
- Author rebuttals: 5 December 2024  
- AC meta reviews due: 7 January 2025  
- SAC decisions: 21 January 2025  
- Paper decision notifications: 10 March 2025  
- Camera-ready revision: 15 March 2025  
- Journal-to-Conference track request: 3 May 2025  

## Implications for recommended bands

- **T−40+ / T−26–39**: match observed repo birth, CFP, chairs, guideline seeding.  
- **T−12–15**: push registration earlier than “when early-bird is about to close.”  
- **T−8–11**: recommend invited speakers here; observed 2024/25 lag to T−1–6 is the main anti-pattern.  
- **T−4–7 / T−1–3**: schedule draft then freeze; counteract final-month commit burst.  
- **Post**: expect proceedings; do not block closing the meeting site on PMLR URL day-of.
