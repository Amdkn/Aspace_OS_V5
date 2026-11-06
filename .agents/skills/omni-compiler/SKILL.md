---
name: omni-compiler
description: "Compile any media (YouTube videos, courses, books, PDF papers) into executable Super-Skills (.agents/skills/) and persistent context (00_Memoire/bundle/ and shared_brain/). Merges Brad Bonanno's multimodal video understanding, book-to-skill layout distillation (Docling/pdftotext), epistemic triage (How vs What), and conflict-resolving decision trees. Make sure to use this skill whenever the user wants to ingest a video, extract insights from a book/PDF, create a Super-Skill from multi-source research, or build structured SOPs from unstructured material."
version: 2.0.0
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [knowledge, compiler, video, book-to-skill, sop, multimodal, gemini, whisperx]
    category: research
---

# Omni-Knowledge Compiler (Knowledge-to-Execution Engine)

A multimodal ingestion, distillation, and synthesis engine that converts any unstructured media (videos, online courses, technical books, PDF manuals) into **executable agent Super-Skills** and **dynamic LLM Wiki context**.

---

## Architecture & Epistemic Separation

```
                                  UNSTRUCTURED RAW SOURCES
                       (YouTube / MP4 / PDF Books / Course Transcripts)
                                              │
                                              ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ COUCHE 1 · DUAL-ENGINE MULTIMODAL INGESTION                                            │
│                                                                                        │
│  ├─ Video Stream:                                                                      │
│  │   ├─ Engine A (Cloud Gemini API): Zero download, -87% tokens, instant timestamps.   │
│  │   └─ Engine B (Local WhisperX + Keyframes): I-Frame extraction (40x speed),         │
│  │       deictic frame capture ("look here"), thumbnail deduplication.                 │
│  │                                                                                     │
│  └─ Book & PDF Stream:                                                                 │
│      ├─ Text-centric: pdftotext CLI extraction.                                        │
│      ├─ Complex layouts / tables: IBM Docling parser.                                  │
│      └─ Book unavailable: Cross-aggregation of 5 deep chapter summaries + 3 reviews.   │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ COUCHE 2 · EPISTEMIC TRIAGE: THE "HOW" vs THE "WHAT"                                   │
│ Discriminative Rule: "Does the process repeat, or does the information change?"       │
│                                                                                        │
│         ┌─────────────────────────────────┴─────────────────────────────────┐          │
│         ▼ (Process Repeats = THE HOW)       (Data Changes = THE WHAT) ▼          │
│   [ SUPER-SKILL COMPILER ]                     [ LLM WIKI & SECOND BRAIN ]             │
│   SOPs, decision trees, heuristics             Metrics, client status, research data   │
└─────────┬───────────────────────────────────────────────────┬──────────────────────────┘
          │                                                   │
          ▼                                                   ▼
┌─────────────────────────────────────────┐       ┌──────────────────────────────────────┐
│ COUCHE 3A · THE SKILL BOOKSHELF         │       │ COUCHE 3B · THE SECOND BRAIN WIKI    │
│ (.agents/skills/<name>/)                │       │ (00_Memoire/bundle/ & shared_brain/) │
│                                         │       │                                      │
│ ├─ SKILL.md      (Lean index & trigger) │       │ ├─ concepts/*.md (OKF v0.2 wiki)     │
│ ├─ glossary.md   (Domain taxonomy)      │       │ ├─ shared_brain/memory.jsonl         │
│ ├─ patterns.md   (Before/after concrete)│       │ └─ log.md        (Strict append-only)│
│ └─ cheatsheet.md (Decision matrices)    │       └──────────────────────────────────────┘
└────────────────────┬────────────────────┘
                     │ Progressive Disclosure: Only load on explicit task match
                     ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ COUCHE 4 · CONTINUOUS SELF-IMPROVEMENT EXECUTION LOOP                                   │
│ 1. Load skill metadata into prompt index (~100 tokens).                                │
│ 2. When triggered, load SKILL.md + consult active Second Brain Wiki facts.             │
│ 3. Execute with deterministic checks (02_Factory/checks.ps1).                          │
│ 4. Fold human steering & edge cases back into the Skill without duplicating.           │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## The 5 Core Principles

### Principle 1: Hybrid Video Perception & Token Economy
- **Gemini Video Understanding (`.agents/skills/watch/`)**: Use for rapid scanning of long YouTube videos, identifying timestamped topics, and evaluating audience retention drop-offs without burning local bandwidth.
- **Local Keyframes + WhisperX**: Use when exact pixels, code snippets, or UI workflows must be replicated. Detect deictic expressions (*"as you see here"*, *"look at this line"*) to pin the exact video frame.

### Principle 2: The Bookshelf Progressive Disclosure
Never dump a whole book or transcript into context. Structure the skill as a virtual book:
- `SKILL.md` represents the **spine**: trigger keywords, summary, and navigational index.
- `glossary.md` holds author-specific terms.
- `patterns.md` contains executable implementations.
- `cheatsheet.md` provides fast lookup decision tables.

### Principle 3: Multi-Source Super-Skills & Conflict Arbitrage
Do not create one fragmented skill per video. Synthesize one authoritative **Super-Skill** per discipline:
- Source A provides preparation rules.
- Source B provides tactical execution.
- Source C provides QA inspection standards.
- **Conflict Arbitrage**: If two experts contradict each other, do not overwrite; document the contextual boundary: *"Apply Method A when constraint X holds; switch to Method B under constraint Y."*

### Principle 4: The 5 Founding Business SOP Archetypes
Translate foundational business wisdom into actionable execution trees:
1. **Eugene Schwartz (*Breakthrough Advertising*)**: Assess market awareness (Unaware -> Problem Aware -> Solution Aware -> Product Aware -> Most Aware) before drafting copy.
2. **Alex Hormozi (*$100M Offers & Playbooks*)**: Optimize the Value Equation ($\text{Value} = \frac{\text{Dream Outcome} \times \text{Perceived Likelihood}}{\text{Time Delay} \times \text{Effort \& Sacrifice}}$), stack bonuses, and design risk-reversal guarantees.
3. **Adamson & Dixon (*The Challenger Sale*)**: Structure commercial pitches through 6 steps (The Warmer -> The Reframe -> Rational Drowning -> Emotional Impact -> A New Way -> Your Solution).
4. **Blair Enns (*Pricing Creativity*)**: Anchor pricing to perceived outcome value rather than hours spent.
5. **Chip & Dan Heath (*Decisive*)**: Neutralize AI complacency via the WRAP framework (**W**iden options, **R**eality-test assumptions, **A**ttain distance, **P**repare to be wrong).

### Principle 5: Invariant Separation of Skill (How) vs Wiki (What)
- **The How (Skill)**: How to write a proposal, analyze a video, backtest an algorithm. Encoded once in `.agents/skills/<name>/`.
- **The What (Wiki)**: Client rosters, Q4 numbers, market intelligence. Encoded in `00_Memoire/bundle/` and indexed in `00_Memoire/shared_brain/memory.jsonl`.

---

## Step-by-Step Compilation Procedure

### Step 1: Input Detection & Extraction
```powershell
# For video sources
python .agents/skills/watch/scripts/watch.py "<URL_OR_PATH>" --question "Extract core procedural steps, decision rules, and keyframes"

# For PDF / Book sources (Docling layout extraction or pdftotext)
pdftotext -layout input_book.pdf extracted_raw.txt
```

### Step 2: Epistemic Routing
Separate the extracted content into:
1. **Procedural Rules** -> Route to Step 3.
2. **Factual Entities / Knowledge Notes** -> Append to `00_Memoire/bundle/concepts/<topic>.md` and register in `shared_brain/memory.jsonl`.

### Step 3: Scaffold the Super-Skill
Create directory `.agents/skills/<skill-name>/` with:
- `SKILL.md` (metadata, triggers, high-level procedure)
- `glossary.md` (domain taxonomy)
- `patterns.md` (concrete examples)
- `cheatsheet.md` (decision logic)

### Step 4: Verification & Scellement
1. Run `pwsh -NoProfile -File 02_Factory/checks.ps1` (verify 7/7 PASS).
2. Append entry to `00_Memoire/bundle/log.md`.
3. Commit and push changes.
