---
type: Architecture Decision Record
id: a0-cognitive-architecture-jepa-v1
title: "A0 Cognitive Architecture — JEPA, Generative Imagination, Predictive Wargame & Epistemic Verification"
status: Proposed
created: "2026-11-20"
updated: "2026-11-20"
owners: ["A0 Amadeus", "S1 Rick"]
tags: [cognitive-architecture, jepa, world-model, generative-imagination, predictive-wargame, fugu, epistemic-verification]
---

# ADR — A0 Cognitive Architecture: JEPA + Generative + Predictive + Verification

## 0. Executive decision

**Decision proposed:** evolve A'Space V5 from a predominantly language-generation-centred agent model toward a modular, evidence-grounded **Cognitive World Intelligence** architecture.

Do **not** replace predictive modelling with hallucination. Preserve predictive models as a first-class capability. Introduce controlled generative imagination for hypothesis and solution exploration, investigate JEPA-family models as a learned latent-state/world-modelling capability, and make epistemic verification a mandatory cross-cutting control.

Transformers remain a valuable computational substrate for language, sequence modelling, attention and (in some implementations) JEPA encoders/predictors. They are not declared the sole or universal foundation of every cognitive function.

This ADR is a design decision proposal, not an authorization to replace production inference, download model weights, alter the runtime, or change existing OS topology. Research and interface design may proceed; production integration requires benchmark evidence and a separate implementation gate.

## 1. Context and problem

The current V5 architecture already separates several useful capabilities:

- **Language and multimodal inference:** LFM3-Omni and the local/free-cloud inference routes documented by the Runtime and Fugu concepts.
- **Fast typed decisions:** Needle / typed tool routing and deterministic decision paths.
- **Quantitative prediction:** Mitra-v2, TabFM, Chronos-2, TimesFM and PathFM in the Neuro-Tabular Wargame concept.
- **Emergent and social simulation:** MiroFish / OASIS.
- **Orchestration:** Sakana Fugu with Thinker / Worker / Verifier roles.
- **Shared memory and provenance:** the existing Memory / Runtime architecture.

The gap is not simply a lack of another LLM. It is the absence of a clearly specified, reusable contract for representing the current state of a domain, predicting how that state may evolve, exploring counterfactual futures, and comparing imagined outcomes with observed outcomes.

Autoregressive LLM token prediction is useful for language generation, but token likelihood alone is not a sufficient objective for physical, operational, social, economic or personal world modelling. Conversely, latent prediction does not automatically provide planning, causal understanding, reliable action models or factual grounding. Those capabilities must be engineered and evaluated.

## 2. Terminology — do not conflate the objectives

| Capability | What it predicts or produces | Intended use |
|---|---|---|
| Autoregressive language modelling | Next token / token sequence | Language, code, structured text |
| JEPA-family latent prediction | Target representation from context representation | Learn task-relevant structure while avoiding unnecessary pixel/token reconstruction |
| Predictive modelling | Future values, labels, distributions or trajectories | Forecasts, risk, planning inputs |
| Generative modelling | Samples, content, plans or candidate constructions | Create alternatives and candidate solutions |
| Generative imagination | Explicitly labelled hypotheses and counterfactual scenarios | Explore possibilities beyond the most likely future |
| Verification | Evidence-backed assessment of claims and outputs | Calibration, safety, provenance and decision gates |

**Hallucination is not an architecture objective.** It describes generated content that is unsupported, fabricated or incorrectly presented as fact. A'Space may deliberately generate speculative hypotheses, but must label them as hypotheses and must never silently promote them to observations or verified knowledge.

Preferred term: **Generative Imagination** (controlled exploration), not “hallucination engine”.

## 3. Decision and architecture

Adopt a modular Cognitive Engine coordinated by Fugu. The four capabilities below are peers; none is a universal replacement for the others.

### 3.1 Four cooperating capabilities

1. **World Model / JEPA Research Track**
   - Encode observations into state representations.
   - Predict future or target latent representations.
   - Where supported by the selected model, condition predictions on actions, time, environment and agent state.
   - Expose uncertainty, model/version identity and the scope of training/evaluation.
   - Do not claim that a generic JEPA checkpoint is an action-conditioned world model unless its architecture and training support that claim.

2. **Generative Imagination**
   - Produce candidate hypotheses, designs, plans and counterfactual scenarios.
   - Explore likely, alternative, edge and disruptive possibilities.
   - Attach assumptions, preconditions, expected consequences and falsification conditions.
   - Keep speculative output separate from observed facts and durable memory.

3. **Predictive Wargame**
   - Preserve specialist quantitative models for tabular, temporal, probabilistic and trajectory forecasting.
   - Preserve MiroFish/OASIS for agent-based and social simulation.
   - Return distributions, quantiles, confidence/calibration information and baseline comparisons where supported.
   - Never replace deterministic calculations or specialist forecasts with an LLM's narrative confidence.

4. **Epistemic Verification**
   - Check claims against source evidence, deterministic rules, tool results, observed state and independent model outputs.
   - Detect contradictions, unsupported claims, stale observations and out-of-domain predictions.
   - Enforce policy, permissions, provenance and human approval boundaries.
   - Return explicit verdicts: verified, supported, uncertain, contradicted, stale or unverified.

### 3.2 Cognitive loop

```text
OBSERVE
  -> ENCODE / UPDATE STATE
  -> MODEL (latent state and domain state)
  -> IMAGINE (candidate futures and interventions)
  -> PREDICT (quantitative outcomes and uncertainty)
  -> PLAN / ARBITRATE
  -> VERIFY (evidence, constraints, permissions, risk)
  -> ACT (only within granted authority)
  -> OBSERVE OUTCOME
  -> COMPARE PREDICTION WITH REALITY
  -> UPDATE MEMORY / CALIBRATION / MODEL EVALUATION
```

The loop is recursive, but model updates are not automatically performed after every interaction. Runtime state updates, memory writes, adapter training and foundation-model retraining are distinct operations with separate permissions and validation.

### 3.3 Logical topology

```text
A0 AMADEUS — intent, strategy, meta-cognition and arbitration
  |
  +-- FUGU — orchestration / Thinker / Worker / Verifier / dispatch
        |
        +-- World Model capability (JEPA-family candidates)
        +-- Generative Imagination capability (LLM / generative models)
        +-- Predictive Wargame capability (tabular / time-series / agents)
        +-- Epistemic Verification capability (evidence / rules / provenance)
        |
        +-- Shared State & Memory contracts
        |
        +-- Existing Tech OS -> Life OS -> Areas OS agents and tools
```

This is a capability topology, not a new operating system and not a new layer of Holons. It does not alter the canonical three-OS dependency or the documented 13 + 43 + 522 = 578 Holon topology.

## 4. Integration with existing V5 assets

| Existing V5 asset | Preserved responsibility | Proposed relationship |
|---|---|---|
| LFM3-Omni / language models | Language, multimodal interpretation, tool interaction | Generative interface and reasoning component; not the sole world model |
| Needle / typed routing | Fast typed decisions and dispatch | Deterministic routing and action contracts |
| Fugu / TRINITY | Thinker, Worker, Verifier orchestration | Cognitive control plane and capability router |
| MiroFish / OASIS | Multi-agent and social simulation | Scenario simulation backend |
| Mitra-v2 / TabFM | Tabular inference | Quantitative state and outcome estimates |
| Chronos-2 / TimesFM | Time-series forecasting | Temporal forecast services |
| PathFM | Trajectory and rollout research | Trajectory candidate service, subject to benchmark |
| Memory / provenance | Shared state, durable knowledge and traceability | Stores verified observations, decisions and model receipts; speculative content remains segregated |

The existing 90% deterministic / 10% contextual-judgment rule in the Neuro-Tabular Wargame remains a **domain-specific economic/business governance policy**. It must not be generalized as a universal ratio for all cognition, creativity, research or simulation.

## 5. Capability contracts (provider-neutral)

The first implementation milestone is an interface contract, not a model deployment. Providers can be local models, remote services or deterministic software.

### 5.1 Common request envelope

```json
{
  "request_id": "stable-idempotency-key",
  "domain": "life|areas|tech|business|environment",
  "task": "state_encode|latent_predict|imagine|forecast|verify",
  "as_of": "ISO-8601 timestamp",
  "state_ref": "reference-to-versioned-state",
  "context_refs": [],
  "constraints": [],
  "authority": "read_only|propose|execute_scoped",
  "trace_id": "trace-id"
}
```

### 5.2 Common response envelope

```json
{
  "request_id": "same-request-id",
  "provider": "provider-and-model-id",
  "model_version": "immutable-version-or-checkpoint",
  "result_type": "observation|latent|hypothesis|forecast|decision|verification",
  "payload_ref": "typed-payload-reference",
  "uncertainty": {
    "kind": "calibrated|estimated|not_available",
    "value": null,
    "notes": []
  },
  "assumptions": [],
  "evidence_refs": [],
  "created_at": "ISO-8601 timestamp"
}
```

These envelopes are illustrative contracts. Before implementation, define JSON Schema / typed language equivalents, units, time semantics, versioning, error taxonomy, payload limits and compatibility tests. Never treat the illustrative null uncertainty as a numeric confidence score.

### 5.3 Required capability semantics

- `state_encode`: returns a versioned representation and its observation/source references.
- `latent_predict`: returns a predicted representation, prediction horizon, conditioning inputs and model limitations.
- `imagine`: returns one or more explicitly speculative candidates with assumptions and falsification conditions.
- `forecast`: returns forecast values/distributions, horizon, baseline and calibration metadata where available.
- `verify`: returns a verdict plus evidence references and unresolved gaps.

No capability may silently change the authority level of a request. A proposal is not an execution grant.

## 6. Epistemic and safety invariants

1. **Evidence classes stay distinct:** observed, retrieved, computed, predicted, simulated, imagined and verified are separate labels.
2. **No hallucination laundering:** generated hypotheses cannot become factual memory without verification and provenance.
3. **Uncertainty is explicit:** do not invent confidence percentages; preserve unknown / unavailable.
4. **Prediction is not truth:** forecast outputs are evaluated against later observations and baselines.
5. **JEPA is not magic:** latent prediction alone does not prove causal understanding, planning competence or real-world grounding.
6. **World state is versioned:** each prediction identifies the state snapshot and time it used.
7. **Actions remain gated:** execution requires scoped authority, policy checks and any required human ratification.
8. **Human sovereignty is preserved:** the A0 / S0 human authority and existing S1 veto remain intact.
9. **Security is cross-cutting:** least privilege, data minimization, local-first routing where appropriate, and no uncontrolled model or data egress.
10. **Memory is curated:** only eligible, provenance-bearing results become durable knowledge; speculative branches remain in a sandbox.
11. **Failure is explicit:** timeout, out-of-domain, missing evidence and provider failure must not be converted into fabricated answers.
12. **Model replacement is evidence-driven:** no production model is removed solely because a new paradigm is promising.

## 7. Evaluation and acceptance gates

A JEPA or world-model candidate cannot enter production based on a compelling demo alone.

### Gate A — Research reproducibility
- Identify the exact paper, repository, license, checkpoint, modality and intended task.
- Record hardware, runtime dependencies, data requirements and reproducible setup.
- Review security, provenance, data rights and local deployment feasibility.

### Gate B — Domain benchmark
- Define at least one bounded environment and a versioned evaluation dataset.
- Compare against persistence / naive baselines, existing specialist models and relevant LLM-only baselines.
- Measure representation or prediction quality, rollout error over horizon, calibration where applicable, latency, memory, compute, failure rate and out-of-distribution behaviour.
- Test whether action conditioning is genuinely supported if action-conditioned planning is claimed.
- Record negative results and known limitations.

### Gate C — Shadow integration
- Run read-only beside existing V5 services.
- No autonomous production actions and no writes to canonical memory.
- Compare predicted states with later observations and track drift.
- Require Verifier review of all promoted claims.

### Gate D — Scoped pilot
- Enable only a bounded domain and explicit permissions.
- Keep rollback path and incumbent models.
- Require human approval for consequential actions.
- Promote only after benchmark thresholds are specified and met.

### Gate E — Production decision
A separate ADR must approve the model, data, hardware, operational owner, SLOs, security review, rollback plan and ongoing evaluation process.

## 8. Initial experiment proposal

Start with a low-risk, observable environment rather than attempting to model all of A'Space at once.

Recommended sequence:

1. **Toy visual or state-transition environment:** test representation prediction and multi-step rollout against known transitions.
2. **Agent-office / Cube Farm simulation:** test whether a learned latent state predicts occupancy, task-state transitions or bounded agent/environment dynamics better than a simple symbolic baseline.
3. **One Areas OS workflow:** test scenario generation and quantitative evaluation using synthetic or approved data, while preserving the existing workflow and human approval.
4. **Cross-domain research:** only after the above, examine whether shared latent representations transfer usefully across domains. Do not assume one universal latent space is desirable.

Each experiment must answer a falsifiable question, for example: “Does candidate X reduce multi-step state prediction error over baseline Y at horizon H under the same observation and compute budget?” A “yes” requires a recorded benchmark, not a subjective impression.

## 9. Consequences

### Positive
- Separates language generation from world-state prediction and quantitative forecasting.
- Makes imagination useful without treating unsupported output as fact.
- Reuses existing V5 predictive, simulation, memory and orchestration assets.
- Creates provider-neutral contracts and measurable adoption gates.
- Allows model diversity without fragmenting the three-OS architecture.

### Costs and risks
- Additional model-serving, data, evaluation and observability complexity.
- Latent representations can be difficult to interpret and may fail under distribution shift.
- Long-horizon rollout errors can compound.
- JEPA research checkpoints may not support action-conditioned world modelling or the desired modalities.
- More orchestration can increase latency and operational failure modes.

Mitigations: start read-only, benchmark against simple baselines, preserve specialist predictors, version state and models, expose uncertainty, and gate all consequential actions.

## 10. Non-goals

This ADR does not:
- Replace Transformers, LLMs, Fugu, Needle, MiroFish or the Predictive Wargame.
- Declare hallucination desirable as a truth-producing mechanism.
- Assert that JEPA alone provides reasoning, agency, causal models or a complete world model.
- Add a fourth OS or change the Tech OS -> Life OS -> Areas OS dependency.
- Change the 578-Holon topology or agent identities.
- Authorize model downloads, weight changes, training, fine-tuning, production deployment or autonomous execution.
- Mandate one universal model, one latent space or one fixed predictive/generative percentage.

## 11. Research references

Use these as starting points; verify current repository state, license, model card and checkpoint details before adoption.

- I-JEPA (Meta): https://github.com/facebookresearch/ijepa
- V-JEPA 2 (Meta): https://github.com/facebookresearch/vjepa2
- LeWorldModel: https://github.com/gaoyuezhou/LeWorldModel
- Agentic-JEPA: https://github.com/pu-suo/Agentic-JEPA
- A'Space V5 — Neuro-Tabular Wargame: https://github.com/Amdkn/Aspace_OS_V5/blob/master/00_Memoire/bundle/concepts/neuro-tabular-wargame.md
- A'Space V5 — Sakana Fugu Inference: https://github.com/Amdkn/Aspace_OS_V5/blob/master/00_Memoire/bundle/concepts/sakana-fugu-inference.md
- A'Space V5 — Three-OS Holonic Architecture: https://github.com/Amdkn/Aspace_OS_V5/blob/master/00_Memoire/bundle/concepts/aspace-3os-holons.md
- A'Space V5 — Runtime Fusion Principles: https://github.com/Amdkn/Aspace_OS_V5/blob/master/01_Forkable/FKB00_Runtime/principes-fusion-runtime.md

## 12. Implementation work queue

- [ ] Review and ratify this ADR (A0 / S1 / human authority as applicable).
- [ ] Define JSON Schemas and typed interfaces for the five capability tasks.
- [ ] Create a JEPA candidate matrix (I-JEPA, V-JEPA 2 and other candidates) with modality, task, license, checkpoint, hardware and action-conditioning support.
- [ ] Select one bounded benchmark environment and establish naive/symbolic/LLM baselines.
- [ ] Build a read-only evaluation harness with traceable state snapshots and prediction receipts.
- [ ] Define promotion rules for verified observations and durable memory.
- [ ] Submit a separate implementation ADR before any production Runtime integration.

---

**Canonical principle:** A'Space does not replace prediction with hallucination. It combines grounded perception, latent world modelling, controlled imagination, quantitative prediction, epistemic verification and permissioned action — while keeping every claim's epistemic status visible.
