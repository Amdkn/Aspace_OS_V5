---
type: Benchmark Specification
id: jepa-toy-world-benchmark-v1
title: "A0 JEPA Toy World — Deterministic State-Transition Benchmark"
status: Proposed
created: "2026-11-20"
parent_adr: "a0-cognitive-architecture-jepa-v1"
parent_matrix: "jepa-world-model-research-matrix-v1"
tags: [jepa, world-model, benchmark, gymnasium, cube-farm, reproducibility]
---

# A0 JEPA Toy World — Benchmark Specification V1

## 0. Purpose and boundary

Build the first falsifiable experiment for A'Space V5 Cognitive World Intelligence.

The benchmark asks one question:

> Given rendered observations and a known sequence of actions, can a candidate model predict the next world state — and maintain useful accuracy over multiple steps — better than transparent baselines under the same evaluation conditions?

This is a **research specification only**. It does not authorize package installation, checkpoint downloads, training, fine-tuning, model serving, Runtime integration, agent actuation or writes to canonical memory.

The environment is a deterministic visual micro-world. Its simulator owns the ground-truth symbolic state. Candidate models receive only the observation/action interface declared for their track. The evaluator alone reads ground truth.

## 1. Experimental design

### 1.1 World geometry

- Grid: 12 × 12 logical cells.
- Render: 192 × 192 RGB image, nearest-neighbour cell rendering, fixed camera and fixed palette.
- Static elements: walls, floor, goal markers and fixed landmarks.
- Dynamic elements: one agent, zero to two movable crates, one to two toggle gates and one to two pressure plates.
- State changes are discrete and deterministic.
- No physics engine, networking, external API or real-world actuation.

The geometry is intentionally small enough for symbolic ground truth and rich enough to test object persistence, occlusion, action effects, interaction and multi-step consequences.

### 1.2 Action vocabulary

| Action | Semantics |
|---|---|
| `NOOP` | Advance one tick without intentional movement |
| `MOVE_N` | Attempt one-cell north movement |
| `MOVE_S` | Attempt one-cell south movement |
| `MOVE_E` | Attempt one-cell east movement |
| `MOVE_W` | Attempt one-cell west movement |
| `INTERACT` | Toggle an adjacent interactable gate or activate a context-defined mechanism |

Invalid actions are still recorded and produce a deterministic no-op or blocked transition according to the environment rules. The exact rule is part of the versioned transition specification, not left to model interpretation.

### 1.3 State schema

The evaluator's canonical state is versioned JSON:

```json
{
  "schema_version": "toy-world.state.v1",
  "episode_id": "seed-000042-layout-01",
  "layout_id": "layout-01",
  "layout_hash": "sha256:<64-hex-digest>",
  "tick": 12,
  "agent": {"x": 3, "y": 8, "facing": "N"},
  "crates": [{"id": "crate-01", "x": 4, "y": 8}],
  "gates": [{"id": "gate-01", "mode": "pressure", "open": false}],
  "plates": [{"id": "plate-01", "controls_gate_id": "gate-01", "active": false}],
  "goal": {"x": 9, "y": 2, "reached": false},
  "terminal": false
}
```

Rules:
- Coordinates use integer grid positions with origin at the top-left.
- Entity IDs remain stable within an episode.
- Arrays are sorted by stable entity ID before serialization and hashing.
- The state hash is computed from canonical serialization.
- Observation metadata never leaks hidden evaluator fields.
- Every transition records prior state hash, action, resulting state hash and transition-spec version.

### 1.4 Observation tracks

**Track A — Full visual observation**
- One RGB frame per tick.
- Candidate gets the current frame and the action history required by its declared interface.
- No symbolic coordinates or hidden state fields are exposed.

**Track B — Short visual context**
- A fixed window of the last four RGB frames and the subsequent action sequence.
- Used for models whose published inference interface expects temporal context.

**Track C — Optional partial observation**
- A bounded field-of-view variant with some cells occluded.
- Only enabled after Track A/B is stable; never mix its results with fully observed scores.

Each track is a separate benchmark result. Do not compare scores across tracks as if the input information were identical.

## 2. Transition mechanics

The simulator applies exactly one action per tick in a documented order:

1. Validate the action against the action vocabulary.
2. Resolve movement or interaction intent.
3. Apply collision and occupancy constraints.
4. Update pressure-plate and gate state according to the frozen rule order.
5. Evaluate goal and terminal conditions.
6. Increment tick.
7. Emit the rendered observation and evaluator-only state receipt.

The transition function must be pure with respect to a given state, action and environment version:

[
S_{t+1} = T_v(S_t, a_t)
]

For seeded episode generation, the same seed and environment version must produce the same initial state, layout, action sequence and ground-truth trace.

## 3. Dataset and split protocol

Initial protocol proposal:

| Split | Layout families | Episodes | Purpose |
|---|---:|---:|---|
| Train / development | 8 | 100 | Debugging and optional model-specific adaptation only if separately approved |
| Validation | 4 held-out combinations | 50 | Select settings; no final reporting |
| Test IID | 8 familiar families, unseen seeds | 100 | Generalization to new episodes |
| Test OOD | New combinations of known mechanics | 100 | Compositional generalization |

- Freeze all seeds and split manifests before candidate evaluation.
- No test episode may be used for training, tuning, prompt design or checkpoint selection.
- Keep an immutable manifest containing episode ID, seed, split, world version and action-sequence hash.
- Publish the exact action sequences for reproducibility after evaluation, not before a blind test if sequence leakage is a concern.
- A later benchmark revision may increase sample counts; never silently alter V1 test manifests.

## 4. Prediction tasks and horizons

For each episode, capture a sequence of observations and actions. Evaluate predictions at horizons:

- H1: next transition.
- H3: three transitions ahead.
- H5: five transitions ahead.
- H10: ten transitions ahead.

At each prediction point the model receives the declared observation context and the future action sequence for the horizon. This isolates **world transition prediction** from action selection. A separate planning benchmark may later ask a planner to choose actions.

The candidate must declare whether it returns:
- a latent embedding only;
- a latent embedding plus a learned state probe;
- a decoded image;
- a structured state estimate;
- or multiple outputs.

Do not pretend that a latent vector is a symbolic state. If a model has no native state decoder, use a separately trained and documented probe, fit only on the permitted training split. Report latent-space metrics and probe-based state metrics separately.

## 5. Baselines and candidate tracks

### Baselines — mandatory

1. **Persistence baseline:** predict that the world remains unchanged.
2. **Symbolic transition oracle:** exact simulator transition; an upper-bound reference, never a learned competitor.
3. **Small learned visual baseline:** a modest CNN/temporal predictor trained only on the approved training split, if training is authorized.
4. **Optional random predictor:** diagnostic floor only; not a meaningful adoption comparator.

### JEPA candidate tracks

- **LeWorldModel:** first candidate for pixel-to-latent action-conditioned prediction, subject to artifact/license/hardware gate.
- **V-JEPA 2-AC:** action-conditioned video-world-model comparison, subject to compatible input/action contract and hardware gate.
- **V-JEPA 2.1 + dynamics head:** separate experiment. The dynamics head is an additional learned component; do not label the base encoder itself action-conditioned.
- **Agentic-JEPA:** excluded from the physical Toy World leaderboard initially; it may be evaluated in a separate software-agent task after this benchmark.
- **I-JEPA:** static-image representation reference only, not a temporal action-conditioned candidate.

A candidate is marked **not applicable** when its published interface cannot support the task without an unapproved architectural change. Do not silently build adapters that change the research question.

## 6. Metrics

Report each metric per split and per horizon. Include sample count and confidence intervals where statistically meaningful.

### 6.1 State transition quality

- Agent position exact-match accuracy.
- Crate position exact-match accuracy.
- Gate/plate state exact-match accuracy.
- Goal and terminal-state accuracy.
- Full structured-state exact match.
- Per-field error rate and confusion matrix.

### 6.2 Visual and latent quality

- Pixel reconstruction error only when a model actually produces a comparable decoded image.
- Latent cosine distance / representation similarity only with a clearly defined, version-stable target representation.
- Probe accuracy for decoded symbolic fields, with probe training data and capacity documented.
- Never compare raw latent distances across unrelated model embedding spaces.

### 6.3 Rollout robustness

- Error growth from H1 to H10.
- First divergence tick.
- Invalid/impossible-state rate.
- Collision and occupancy constraint violation rate.
- Recovery after a surprise or unexpected transition.

### 6.4 Operational cost

- Cold-start latency.
- Warm p50 / p95 inference latency.
- Peak VRAM and host RAM.
- Throughput at fixed batch and resolution.
- Model/checkpoint size and total artifact footprint.
- Energy or accelerator-time estimate when available.

### 6.5 Calibration and epistemic behaviour

If a candidate exposes uncertainty:
- evaluate calibration only when the uncertainty output has a documented statistical meaning;
- measure confidence against empirical error;
- record abstention / out-of-domain behaviour;
- do not convert arbitrary similarity scores into confidence percentages.

## 7. Execution protocol

1. Freeze simulator version, action semantics, renderer, seeds and test manifests.
2. Run deterministic simulator self-tests before any model evaluation.
3. Run persistence baseline and symbolic oracle.
4. Run each approved candidate with identical episode inputs and action sequences.
5. Store prediction receipts separately from ground-truth traces.
6. Compute metrics with a versioned evaluator.
7. Produce per-episode traces for every failure and a summary report.
8. Repeat a subset to verify deterministic inference where the candidate claims determinism.
9. Archive environment commit, candidate commit/checkpoint hash, configuration hash and dependency lockfile.
10. Keep all evaluation outputs read-only; do not write to A'Space canonical memory.

## 8. Prediction receipt contract

Every prediction must produce a receipt structurally equivalent to:

```json
{
  "receipt_version": "toy-world.prediction.v1",
  "episode_id": "seed-000042-layout-01",
  "source_observation_ids": ["obs-000011"],
  "action_sequence_hash": "sha256:...",
  "target_tick": 13,
  "candidate": {
    "name": "candidate-name",
    "model_version": "immutable-checkpoint-or-commit"
  },
  "prediction_type": "latent|decoded_state|structured_state|image",
  "prediction_ref": "artifact://prediction/...",
  "uncertainty": {
    "kind": "calibrated|estimated|not_available",
    "value": null
  },
  "assumptions": [],
  "created_at": "ISO-8601"
}
```

The evaluator adds the ground-truth receipt after inference. Candidate code must never receive the ground-truth state or future observations through logs, environment info, filenames or debug channels.

## 9. Acceptance gates

### Gate 0 — Environment correctness
- [ ] Same seed produces identical initial state and rendered observation.
- [ ] Same state/action/version produces identical next state.
- [ ] State hashes and action hashes are stable.
- [ ] Invalid actions and boundary collisions are tested.
- [ ] Ground-truth fields are absent from candidate-visible observations.
- [ ] Independent replay reproduces the same trace.

### Gate 1 — Baseline validity
- [ ] Persistence baseline executes on all splits.
- [ ] Symbolic oracle matches the simulator transition exactly.
- [ ] Metric implementation is tested against hand-authored fixtures.
- [ ] Horizon and split accounting are verified.

### Gate 2 — Candidate readiness
- [ ] Code, checkpoint, data and dependency licenses reviewed.
- [ ] Hardware and memory budget approved.
- [ ] Candidate input/output adapter documented.
- [ ] No unsupported action-conditioning claim.
- [ ] Reproducible execution environment approved.

### Gate 3 — Comparative result
- [ ] Candidate beats persistence on predeclared primary metrics.
- [ ] Multi-step quality is reported at H1/H3/H5/H10.
- [ ] OOD and failure cases are reported.
- [ ] Runtime cost is within a separately approved budget.
- [ ] Result is independently reproducible.

Passing this benchmark authorizes only consideration of a **read-only shadow evaluation**. It does not authorize production deployment or agent actions.

## 10. Machine-readable contracts and proposed implementation layout

The initial contracts and transition rules are committed alongside this specification:

- [Canonical evaluator state schema](../../../research/jepa_toy_world/spec/state-schema.v1.json)
- [Action record schema](../../../research/jepa_toy_world/spec/action-schema.v1.json)
- [Immutable layout schema](../../../research/jepa_toy_world/spec/layout-schema.v1.json)
- [Deterministic transition rules](../../../research/jepa_toy_world/spec/transition-rules.v1.md)
- [PRNG and seed protocol](../../../research/jepa_toy_world/spec/prng-spec.v1.md)
- [RGB renderer contract](../../../research/jepa_toy_world/spec/renderer-spec.v1.md)
- [Hand-authored transition fixtures](../../../research/jepa_toy_world/spec/transition-fixtures.v1.json)

Implementation remains isolated under research/jepa_toy_world. The contracts above are proposed and must pass executable conformance tests before the dataset manifests are frozen:

```text
research/
  jepa_toy_world/
    README.md
    spec/
      state-schema.v1.json
      action-schema.v1.json
      layout-schema.v1.json
      transition-rules.v1.md
      prng-spec.v1.md
      renderer-spec.v1.md
      transition-fixtures.v1.json
      benchmark-manifest.v1.json
    env/
      toy_world.py
      renderer.py
      fixtures/
    baselines/
      persistence.py
      symbolic_oracle.py
      small_visual_predictor.py
    adapters/
      candidate_contract.py
    evaluator/
      metrics.py
      replay.py
      receipts.py
    tests/
      test_seed_determinism.py
      test_transition_determinism.py
      test_no_ground_truth_leakage.py
      test_metric_fixtures.py
    reports/
```

This is a proposed layout, not a claim that these files or modules already exist.

## 11. Implementation order

1. Ratify the state schema, action vocabulary and transition order.
2. Implement the deterministic simulator and renderer.
3. Add seed/replay/state-hash tests and ground-truth isolation tests.
4. Implement persistence and symbolic oracle baselines.
5. Freeze dataset manifests and evaluator fixtures.
6. Run baseline-only benchmark and validate the report.
7. Complete candidate artifact and hardware gates.
8. Add one candidate adapter at a time.
9. Publish comparative results and failure traces.
10. Decide whether to proceed to read-only shadow evaluation.

## 12. Reference standards

- Gymnasium Env API: https://gymnasium.farama.org/main/api/env/
- Gymnasium custom environment guide: https://gymnasium.farama.org/introduction/create_custom_env/
- Gymnasium determinism checker: https://gymnasium.farama.org/main/_modules/gymnasium/utils/env_checker/
- LeWorldModel project: https://github.com/lucas-maes/le-wm
- V-JEPA 2 official repository: https://github.com/facebookresearch/vjepa2

## Canonical rule

**The simulator knows what happened. The model predicts what may happen. The evaluator decides how well the prediction matched reality. The agent has no authority to alter the benchmark world during inference.**
