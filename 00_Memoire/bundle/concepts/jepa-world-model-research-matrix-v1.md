---
type: Research Matrix
id: jepa-world-model-research-matrix-v1
title: "A0 JEPA / World-Model Research Matrix"
status: Research
created: "2026-11-20"
updated: "2026-11-20"
parent_adr: "a0-cognitive-architecture-jepa-v1"
tags: [jepa, world-model, v-jepa, leworldmodel, agentic-jepa, benchmark]
---

# A0 JEPA / World-Model Research Matrix — V1

## 0. Mission

Select research candidates for A'Space V5 by **capability fit and reproducible evidence**, not by hype, parameter count or a demo.

This matrix is a research-screening artifact. It does not authorize downloading weights, installing dependencies, training, fine-tuning, runtime integration or production use.

**Decision at this stage:** benchmark two complementary tracks rather than crown one universal model:

- **V-JEPA 2 / 2.1:** high-capability video representation and physical-world understanding track.
- **LeWorldModel (LeWM):** compact action-conditioned latent dynamics and planning track.

I-JEPA is retained as a historical/static-image baseline. Agentic-JEPA is retained as an exploratory agent-reasoning prototype, not as a proven general-purpose world model.

## 1. Candidate comparison

| Candidate | Primary modality / task | Action conditioning | Scale / compute signal | License / artifact caution | A'Space disposition |
|---|---|---|---|---|---|
| **V-JEPA 2** | Video; motion understanding, anticipation, latent prediction | Base V-JEPA 2 is action-free; V-JEPA 2-AC adds action-conditioned latent world modelling | Published checkpoints include 300M, 600M and 1B parameters; official workflow recommends CUDA/GPU | Official repository code reports MIT; verify the exact checkpoint, dataset and third-party dependency terms separately | **Priority A** for video/world-state representation; use 2-AC only for action-conditioned experiments |
| **V-JEPA 2.1** | Dense video features with temporal consistency; representation backbone | Do not assume action conditioning from 2.1 alone; evaluate with a separate dynamics/predictor layer unless a specific artifact proves otherwise | Published checkpoints range from 80M to 2B parameters; B/L variants provide a lower-cost entry than G/Giant | Same repository-level MIT signal; checkpoint and data terms must be independently reviewed | **Priority A** for a representation benchmark; compare B/L before larger variants |
| **LeWorldModel (LeWM)** | Pixels to compact latent state; next-state prediction and control | Yes: predictor consumes current latent plus action | Authors report ~15M trainable parameters and single-GPU training in hours; benchmark claims up to 48× faster planning than a foundation-model world-model comparator | Official repository reports MIT; verify each Hugging Face checkpoint and dataset card independently | **Priority A** for the lightweight Cube Farm / toy-control pilot |
| **I-JEPA** | Static images; predicts masked-region representations from visible context | No temporal action-conditioned dynamics in the reference method | ViT-H / ViT-g checkpoints; useful representation baseline, not a sequential action model | Official repository is archived; repository metadata says archived and its LICENSE is CC BY-NC 4.0. Non-commercial restriction makes it unsuitable as an assumed commercial dependency | **Priority C**: research/reference baseline only; do not make it a commercial runtime dependency |
| **Agentic-JEPA** | Code/task trajectories; latent action evaluation and afterstate prediction prototype | Candidate actions are scored in latent space; README says action proposals currently come externally | README describes a research prototype trained/evaluated on CodeActInstruct using a single Colab T4 | Repository metadata reports MIT; verify model weights, data provenance, dependencies and reproducibility independently | **Priority B/C**: inspect for agentic planning ideas; not a validated replacement for Fugu or a physical world model |

### Important distinctions

1. V-JEPA 2 and V-JEPA 2.1 are not interchangeable: 2.1's dense, temporally consistent representation objective does not by itself prove action-conditioned planning.
2. V-JEPA 2-AC is the relevant V-JEPA branch when testing action-conditioned latent dynamics.
3. LeWM is especially interesting because its public implementation exposes an action-conditioned latent predictor and environment-level planning/evaluation workflows.
4. A repository's code license does not automatically license pretrained weights, datasets, derived artifacts or all dependencies.
5. Parameter count is not a sufficient proxy for VRAM, throughput or latency. Measure actual peak VRAM, batch size, resolution, sequence length and end-to-end latency on the target hardware.

## 2. Evidence register

| Candidate | Primary source | Evidence captured | Open verification |
|---|---|---|---|
| V-JEPA 2 / 2.1 | https://github.com/facebookresearch/vjepa2 | Official repository describes V-JEPA 2, V-JEPA 2-AC and V-JEPA 2.1; lists checkpoints and model sizes; repository LICENSE is MIT | Exact checkpoint terms; per-artifact license; hardware profile; supported inference path; 2.1-to-action-predictor compatibility |
| V-JEPA 2 research | https://ai.meta.com/research/publications/v-jepa-2-self-supervised-video-models-enable-understanding-prediction-and-planning/ | Meta reports video pretraining and a post-trained action-conditioned V-JEPA 2-AC robotics demonstration | Reproduce only claims relevant to A'Space; distinguish paper results from our benchmark |
| LeWorldModel | https://github.com/lucas-maes/le-wm | Official code; paper link; action encoder + latent predictor; environment-specific pretrained checkpoints; repository LICENSE is MIT | Checkpoint/data licenses; exact hardware and runtime; independent reproduction of planning speed/quality |
| LeWorldModel paper/site | https://le-wm.github.io/ | Authors describe end-to-end pixel-to-latent training, action-conditioned next-embedding prediction and compact model | Validate claims against the paper, configs and benchmark scripts |
| I-JEPA | https://github.com/facebookresearch/ijepa | Official archived repository; static-image masked-region latent prediction; repository LICENSE is CC BY-NC 4.0 | Confirm any downstream use restrictions before reuse |
| Agentic-JEPA | https://github.com/pu-suo/Agentic-JEPA | README calls it a research prototype; describes CodeBERT encoder, afterstate predictor, ACT and externally proposed candidate actions | Independent reproduction, benchmark quality, dataset rights, model-weight license and generalization |

## 3. Fit to A'Space V5

| A'Space target | Required capability | Candidate(s) to test | What not to assume |
|---|---|---|---|
| Cube Farm / 3D world | Visual state encoding; temporal transition prediction; optional action-conditioned rollout | LeWM first; V-JEPA 2-AC second; V-JEPA 2.1 as encoder | A video encoder alone is not a complete simulator |
| A'Space visual campus / spatial interface | Scene and motion representations; object/occupancy changes | V-JEPA 2.1 and V-JEPA 2 | Visual feature quality does not equal persistent spatial memory |
| Agent-office workflows | Predict task/agent/environment state transitions | LeWM on a controlled environment; Agentic-JEPA as a separate code-agent hypothesis | Code trajectory results do not prove physical or organizational world modelling |
| Life OS / Areas OS | State snapshots, scenario alternatives and consequences | Symbolic state model + existing predictive models; JEPA only if the state is genuinely visual/temporal | Do not force JEPA into text/tabular workflows where deterministic models are better |
| Business / Neuro-Tabular Wargame | Numeric forecasts, uncertainty, economic scenarios | Existing TabFM/Mitra/Chronos/TimesFM/PathFM stack; JEPA is complementary only where observations are video/spatial | A latent embedding is not a substitute for calibrated numeric forecasts |
| Fugu / agent orchestration | Route capability calls and verify outputs | Fugu remains the orchestrator; candidate models are workers/services | JEPA does not replace policy, tool permissions, memory or verifier logic |

## 4. Benchmark plan — same environment, same budget

### Benchmark 0 — Reproducibility and artifact audit

For every candidate, record:

- Paper version, official repository commit/tag and checkpoint identifier.
- Code license, weight license, dataset license and dependency licenses separately.
- Model card, training data disclosure, modality, input resolution and context/sequence limits.
- Hardware, driver, CUDA/PyTorch/runtime versions, peak VRAM and cold-start time.
- Inference API, output tensor contract, deterministic/reproducible settings and known limitations.
- Security review, provenance and whether artifacts can be stored and executed in the approved A'Space environment.

**Pass condition:** a clean, repeatable setup and an explicit artifact-rights decision. No weight download until this gate is passed.

### Benchmark 1 — Toy state-transition environment

Use a deterministic visual environment with known state and action transitions.

Compare:
- Persistence / no-change baseline.
- Symbolic transition oracle (upper-bound reference, not a learned competitor).
- Small learned pixel/latent baseline.
- LeWM.
- V-JEPA 2-AC if the required action interface and compute are available.
- V-JEPA 2.1 representation + a separately specified dynamics head, as a distinct experiment.

Metrics:
- One-step and multi-step state prediction error.
- Rollout degradation by horizon.
- Action ranking / goal-reaching success where supported.
- Calibration or uncertainty quality where implemented.
- Out-of-distribution transition detection.
- Peak VRAM, throughput, p50/p95 latency and energy/compute cost.

### Benchmark 2 — Cube Farm micro-world

Only after Benchmark 1 passes, model a bounded subset:
- Occupancy and object state.
- Agent location / pose at a defined abstraction.
- Task state transitions.
- A small action vocabulary.
- Explicit reset and deterministic replay.

Compare learned predictions against the simulation's authoritative state. Keep all outputs read-only; no agent receives execution authority from the benchmark.

### Benchmark 3 — A'Space workflow simulation

Only after the visual/control benchmark:
- Define one synthetic or approved workflow with observable states and explicit transitions.
- Use symbolic workflow logic as the ground truth.
- Test whether imagined branches improve option coverage without increasing unsupported claims.
- Keep numeric forecasts in the existing specialist forecasting stack.
- Fugu routes; Verifier adjudicates; canonical memory remains read-only.

## 5. Scoring rubric

Do not assign subjective composite scores before measurements exist. Record raw results first, then score each dimension from 0–5 with evidence links.

| Dimension | Weight | Acceptance question |
|---|---:|---|
| Task fit | 20% | Does the candidate model the target modality and state transitions we actually need? |
| Multi-step predictive quality | 20% | Does it beat persistence and simple learned/symbolic baselines at the required horizon? |
| Action-conditioned planning | 15% | Are actions part of the learned predictor, and does planning improve measured goal success? |
| Runtime feasibility | 15% | Does it fit the approved hardware, memory, latency and energy budget? |
| Reproducibility / observability | 10% | Can results be repeated, traced and compared across versions? |
| Licensing / data provenance | 10% | Are code, weights, data and dependencies cleared for the intended use? |
| Robustness / uncertainty | 10% | Does it fail visibly and remain calibrated under distribution shift? |

**Hard gates:** licensing/provenance, security and runtime feasibility cannot be compensated by a high aggregate score. A failure on any hard gate blocks adoption.

## 6. Provisional ranking — research priority, not a winner

1. **LeWorldModel:** first lightweight experiment for the Cube Farm/toy environment because its published design explicitly combines pixel encoding, action-conditioned latent prediction and planning, with a compact reported parameter budget.
2. **V-JEPA 2-AC:** second action-conditioned comparison, with stronger foundation-model scale and a robotics demonstration; expect a materially heavier hardware profile.
3. **V-JEPA 2.1:** representation track, especially if dense temporal features improve state extraction; pair with a separately benchmarked dynamics model.
4. **Agentic-JEPA:** inspect as an agent-reasoning research prototype, isolated from production agent authority.
5. **I-JEPA:** historical static-image baseline only; archived and non-commercial license flag.

This ordering is optimized for **A'Space learning value per unit of compute and integration risk**, not for general research prestige.

## 7. Exit criteria and next artifacts

- [ ] Ratify this matrix as a research plan.
- [ ] Confirm target GPU/VRAM and approved execution environment before any install or download.
- [ ] Complete per-artifact license and data provenance checks.
- [ ] Select the toy environment and define its state/action schema.
- [ ] Freeze baseline implementations and evaluation seeds.
- [ ] Produce a benchmark report with raw metrics and failure cases.
- [ ] Decide whether to proceed to read-only shadow evaluation.
- [ ] If a candidate passes, create a separate implementation ADR before any Runtime integration.

## 8. Canonical research rule

**A'Space will not select a JEPA because it can imagine a convincing future. It will select a model only when it predicts a bounded world better than a transparent baseline, under an explicit compute budget, with rights and provenance cleared.**
