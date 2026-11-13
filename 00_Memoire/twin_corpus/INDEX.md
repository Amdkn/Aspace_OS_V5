---
type: corpus_index
okf_version: "0.2"
corpus_id: aspace-v5-source-a-twin-corpus
subject: "Amadou Kone (human:amdkn) -> A0 Amadeus (aspace:a0:amadeus)"
audit_status: PASS
---

# Source A Twin Corpus Index — Amadou Kone (`human:amdkn`)

Consolidated, verified Source A corpus across **Muse AI**, **ChatGPT / Antigravity V2 / Claude Code**, and **Gemini / YouTube (`LD04 Cognition`)**. Machine-readable manifest: [twin_corpus_manifest.json](twin_corpus_manifest.json).

## 1. Consolidated Verified Totals

| Metric | Verified Count | Notes |
|---|---:|---|
| **Direct human Source A turns / prompts** | **3,754** | `635` Muse + `299` ChatGPT (dedup.) + `526` Antigravity + `89` Claude Code + `2,205` Gemini (`2,188` direct + `17` live) |
| **JSONL Source A records written** | **3,906** | `3,902` deduplicated (`4` ChatGPT PDF/Drive #24 overlaps flagged via `overlaps_drive: true`); includes `148` tagged relay/automation records |
| **Excluded scheduled / proactive / PII / noise items** | **3,349** | `150` Muse proactive + `95` Claude daemon files + `1,623` `tool_result` + `62` wrappers + `23` empty AG + `693` Gemini civil PII + `522` Gemini scheduled + `274` UI/canvas *(items + files)* |
| **YouTube `LD04 Cognition` watch entries** | **45,700** | `31,096` named-channel views (`28,888` unique videos, `9,773` channels), `14,251` ad/unattributed, `353` unavailable (`2025-06-06` -> `2026-10-12`) |
| **Muse Workspace media & docs inventoried** | **366** | `329` `.mp3`, `6` `.mp4`, `20` non-proactive `.md`, `9` workspace `.txt`, `2` `.ogg` (`150` proactive excluded) |
| **Slice output files** | **20** | **9,496,835 bytes** total; every `.json`/`.jsonl` parses with `0` errors; all `.md` `< 400 KB` |
| **Security & privacy hygiene** | **PASS** | `14` secrets redacted (`[REDACTED_SECRET]`: `5` Muse, `9` GPT/CLI, `0` Gemini); **0** unredacted secrets, **0** civil PII leaks |

## 2. Breakdown by Source & Slice

| Slice | Platform / Source | Direct Human | Relay / Auto / Scheduled | Total JSONL Lines | Exclusions Applied | Summary JSON |
|---|---|---:|---:|---:|---|---|
| `muse/` | Muse AI (`EYI Package_11-11-2026`) | **635** | `20` (`is_relay`) | **655** | `5,054` Muse AI turns, `150` `proactive_messages/*` | [muse/SUMMARY.json](muse/SUMMARY.json) |
| `gpt_cli/` | ChatGPT (Drive 39 `.md` + local 375p PDF) | **299** *(dedup.)* | `5` (`scheduled_button`) | **308** *(304 dedup.)* | ChatGPT `Source B/C` responses; `4` PDF/Drive #24 overlaps tagged | [gpt_cli/SUMMARY.json](gpt_cli/SUMMARY.json) |
| `gpt_cli/` | Antigravity V2 (54 JSON files) | **526** | `70` (`automated_wake`) | **596** | Assistant turns + `23` empty entries | [gpt_cli/SUMMARY.json](gpt_cli/SUMMARY.json) |
| `gpt_cli/` | Claude Code (`~/.claude/projects`, 74/169 scanned) | **89** | `53` (`automated_dispatch`) | **142** | `95` `cubefarm-machines` files, `1,623` `tool_result`, `62` wrappers | [gpt_cli/SUMMARY.json](gpt_cli/SUMMARY.json) |
| `gemini/` | Gemini Takeout (`2025-04`..`2026-10`, 19 files) | **2,205** *(2,188 + 17 live)* | `522` *(11 templates)* | **2,205** | `693` civil/PII (`68` sessions + turns), `522` scheduled, `274` UI/canvas, `Source B/C` | [gemini/SUMMARY.json](gemini/SUMMARY.json) |
| `gemini/` | YouTube Takeout (`youtube_watch_history.csv`) | — | — | — | `14,251` ad/unattributed + `353` deleted separated from `31,096` named | [gemini/youtube_ld04_interests.json](gemini/youtube_ld04_interests.json) |

## 3. Verified File Catalog

### `muse/` (`extract-muse`, 6 files)
- [muse/muse_source_a_turns.jsonl](muse/muse_source_a_turns.jsonl) (`792,417` B, `655` lines: `635` `direct_human` + `20` `relay_or_dispatch`)
- [muse/muse_source_a_digest.md](muse/muse_source_a_digest.md) (`300,077` B; non-proactive docs summary + `2026-10` Part 1, `282` turns)
- [muse/muse_source_a_digest_2026-10_part2.md](muse/muse_source_a_digest_2026-10_part2.md) (`152,060` B; `2026-10` Part 2, `232` turns)
- [muse/muse_source_a_digest_2026-11.md](muse/muse_source_a_digest_2026-11.md) (`180,450` B; `2026-11`, `121` turns)
- [muse/muse_media_and_docs_inventory.json](muse/muse_media_and_docs_inventory.json) (`150,841` B; `329` `.mp3`, `6` `.mp4`, `20` `.md`, `9` `.txt`, `2` `.ogg`)
- [muse/SUMMARY.json](muse/SUMMARY.json) (`3,287` B)

### `gpt_cli/` (`extract-gpt`, 5 files)
- [gpt_cli/chatgpt_drive_source_a.jsonl](gpt_cli/chatgpt_drive_source_a.jsonl) (`496,231` B, `308` lines / `304` deduplicated)
- [gpt_cli/chatgpt_drive_source_a.md](gpt_cli/chatgpt_drive_source_a.md) (`265,525` B)
- [gpt_cli/antigravity_claude_source_a.jsonl](gpt_cli/antigravity_claude_source_a.jsonl) (`2,362,060` B, `738` lines: `596` Antigravity + `142` Claude)
- [gpt_cli/antigravity_claude_source_a.md](gpt_cli/antigravity_claude_source_a.md) (`349,028` B)
- [gpt_cli/SUMMARY.json](gpt_cli/SUMMARY.json) (`3,040` B)

### `gemini/` (`extract-gemini`, 9 files)
- [gemini/gemini_source_a_prompts.jsonl](gemini/gemini_source_a_prompts.jsonl) (`3,253,732` B, `2,205` lines)
- [gemini/gemini_source_a_chronology.md](gemini/gemini_source_a_chronology.md) (`29,789` B; synthesis aligned with `04 — Chronologie des intentions`)
- [gemini/gemini_source_a_chronology_2025_p1.md](gemini/gemini_source_a_chronology_2025_p1.md) (`248,980` B)
- [gemini/gemini_source_a_chronology_2026_p1.md](gemini/gemini_source_a_chronology_2026_p1.md) (`334,616` B)
- [gemini/gemini_source_a_chronology_2026_p2.md](gemini/gemini_source_a_chronology_2026_p2.md) (`335,553` B)
- [gemini/gemini_source_a_chronology_2026_p3.md](gemini/gemini_source_a_chronology_2026_p3.md) (`199,343` B)
- [gemini/youtube_ld04_interests.json](gemini/youtube_ld04_interests.json) (`26,607` B)
- [gemini/youtube_ld04_interests.md](gemini/youtube_ld04_interests.md) (`5,149` B)
- [gemini/SUMMARY.json](gemini/SUMMARY.json) (`8,050` B)

## 4. Verification Summary

- **JSON / JSONL parsing**: All 5 `.json` and 4 `.jsonl` slice files plus `twin_corpus_manifest.json` validated cleanly with zero parse errors.
- **Source A & privacy separation**:
  - `muse/`: `proactive_messages/*` (`150`) excluded from Source A; `20` relay turns excluded from digest Markdown; `5,054` Muse AI turns excluded.
  - `gpt_cli/`: ChatGPT `Source B/C` excluded; `95` `cubefarm-machines` files, `1,623` `tool_result` blocks, and `62` harness wrappers excluded; automated wakes/dispatches tagged separately from `direct_human`.
  - `gemini/`: `693` civil/legal/identity PII entries excluded (0 PII leaks across all 9 files); Gemini `Source B/C` responses excluded; `522` scheduled automations deduplicated into 11 template summaries; raw Takeout dumps purged outside repo.
- **Secret scanning**: Full-byte regex scan across all files in `00_Memoire/twin_corpus/` found `0` unredacted secret tokens.
