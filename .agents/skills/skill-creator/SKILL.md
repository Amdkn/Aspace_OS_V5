---
name: skill-creator
description: "Create new skills, refine existing skills, and compile expertise from any source (conversation, docs, videos, books) into executable SOPs. Merges Anthropic's Skill SOP standards, Hermes Agent's continuous /learn distillation, and Matt Pocock's surgical, highly-opinionated engineering style. Make sure to use this skill whenever the user asks to create a skill, turn a workflow into a skill, optimize a skill, write SOPs, or formalize repetitive tasks."
version: 2.0.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [skills, meta, compiler, anthropic, hermes, pocock, sop]
    category: engineering
---

# Skill Creator (Triple Synthesis: Anthropic SOP × Hermes /learn × Matt Pocock Style)

Create, benchmark, and iteratively refine reusable skills for AI coding agents (`Antigravity`, `Claude Code`, `Pi`, `Codex`, `OpenCode`, `Herdr`, `Orca`).

This skill unifies three industry-standard paradigms:
1. **Anthropic SOP Architecture**: Three-level progressive disclosure (`metadata` -> `SKILL.md` -> `bundled resources`), pushy descriptions combating undertriggering, and quantitative/qualitative eval loops.
2. **Hermes Agent Continuous Learning**: `/learn` distillation from raw multi-turn history, docs, and codebases; incremental updates without duplication; advisory linting guarding against body bloat (<24k chars / <500 lines) and reference sprawl.
3. **Matt Pocock Engineering Precision**: Non-presumptive exploration first, surgical decision presentation with recommended defaults in bold, and clean separation between repeatable mechanics and domain facts.

---

## Architecture & Progressive Disclosure

```
Level 0: skills_list()          → [name + pushy description]           (~100 tokens)
Level 1: SKILL.md body          → Mental models, triggers & core rules   (<500 lines)
Level 2: Bundled Resources      → Loaded on-demand only when invoked
         ├── references/        → Deep domain guides, schemas, cheat sheets
         ├── scripts/           → Deterministic code execution (zero LLM token burn)
         └── assets/            → File templates, icons, boilerplate
```

---

## The 4-Stage Creation & Refinement Process

```
┌─────────────────┐      ┌───────────────────────────┐      ┌────────────────────────┐      ┌──────────────────┐
│ 1. EXPLORATION  │ ───► │ 2. INTENT & INTERVIEW     │ ───► │ 3. DRAFTING & AUDIT    │ ───► │ 4. EVAL & RECORD │
│ Check codebase, │      │ Ask 1 question at a time, │      │ Frontmatter, triggers, │      │ Dry-run verify,  │
│ tools, remotes  │      │ lead with recommended     │      │ progressive structure  │      │ git commit & log │
└─────────────────┘      └───────────────────────────┘      └────────────────────────┘      └──────────────────┘
```

### Stage 1: Non-Presumptive Exploration (Matt Pocock Rule)
Before asking or writing, inspect the actual environment:
- Check existing skills in `.agents/skills/`, `.claude/skills/`, and built-in paths.
- Check project signals: package managers (`pnpm`, `npm`), languages (`ts`, `py`, `go`), tool harnesses.
- Inspect the current conversation: has the user just solved a problem or executed a multi-step sequence? If yes, extract tools, commands, and corrections directly.

### Stage 2: Intent & Interview (Anthropic SOP Rule)
Ask exactly **ONE** concrete question at a time. Lead with the recommended answer:
1. **Triggering boundary**: *When should this skill run?* (Make the description specific and slightly "pushy" to ensure the model doesn't miss calling it).
2. **Deterministic vs Cognitive boundary**: *Can parts of this be automated in Python/Bash scripts rather than pure model tokens?*
3. **Acceptance criteria**: *What constitutes an undeniable proof of success?*

### Stage 3: Drafting & Structural Hygiene (Hermes Agent Rule)
Draft `SKILL.md` following the canonical anatomy:

```markdown
---
name: <kebab-case-name>
description: "<Action verb> + <scope> + <explicit contexts/keywords when to trigger>. Make sure to use this skill whenever..."
version: 1.0.0
platforms: [macos, linux, windows]
---

# <Title>

## When to Use
[Bullet points with explicit triggers and anti-triggers]

## Architecture & Mental Models
[Diagram or state table showing the mechanics]

## Decision Tree / Procedure
1. Step one (surgical command)
2. Step two (evaluation)

## Lessons Learned & Known Pitfalls
[Anti-patterns, edge cases, and post-mortem fixes]

## Verification & Deterministic Gates
[Automated validation commands, expected return codes]
```

#### Advisory Linter Rules (Hermes Guardrails):
- **Body ceiling**: Keep `SKILL.md` under 500 lines (<24 000 characters). Delegate deeper sub-topics to `references/<topic>.md`.
- **References budget**: Maximum 15 reference files to prevent sprawl.
- **Incremental update**: If the user or task reveals new lessons on an existing skill, fold them into `Lessons Learned & Known Pitfalls` rather than creating a fragmented `skill-v2`.

### Stage 4: Evaluation & Storage
1. **Write targets**:
   - Primary: `.agents/skills/<name>/SKILL.md`
   - Mirror: `.claude/skills/<name>/SKILL.md`
2. **Deterministic Gate**: Run `pwsh -NoProfile -File 02_Factory/checks.ps1` to ensure schema compliance and zero broken links.
3. **Commit & Append Log**: Add an append-only entry in `00_Memoire/bundle/log.md`.

---

## Quick Reference Templates

### Scripted Skill
When repetitive shell execution or parsing is involved, place a standalone script in `scripts/` and invoke it from `SKILL.md`:
```
skill-name/
├── SKILL.md
└── scripts/
    └── run.py
```

### Knowledge-Base Skill (Book-to-Skill / Spec-to-Skill)
When distilling a whole book, library, or complex framework:
```
skill-name/
├── SKILL.md         (Lean navigation index + trigger criteria)
├── glossary.md      (Core vocabulary & domain ontology)
├── patterns.md      (Concrete before/after examples)
├── cheatsheet.md    (Quick decision tables & rule sets)
└── chapters/        (Topic-by-topic deep dives)
```
