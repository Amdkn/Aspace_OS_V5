# JEPA Toy World V1 — Research Harness

This directory contains an isolated deterministic research environment. It is not part of the A'Space production Runtime.

## Environment contract

- Python standard library only; no package installation required.
- 12×12 logical world rendered as a 192×192 RGB byte frame.
- Candidate-facing reset/step return an RGB observation and empty info.
- Evaluator state snapshots are private harness operations and must never be passed to candidate code.
- The transition function is deterministic; PCG32 is used only to select one of four immutable seed-indexed layout templates.
- The persistence baseline repeats the last RGB observation.
- The symbolic oracle is evaluator-only and computes exact transitions.

## Run conformance tests

From the repository root:

```bash
python -m unittest discover -s research/jepa_toy_world/tests -t . -v
```

## Run baseline smoke evaluation

```bash
python -m research.jepa_toy_world.evaluator.baseline_smoke
```

The smoke report compares the persistence baseline with the symbolic oracle at H1/H3/H5/H10 across four deterministic layouts. It is only a plumbing and correctness check. It is not a model benchmark, not a statistical result, and not evidence that a JEPA candidate outperforms persistence.

## Versioned contracts

See spec/ for the canonical state, action and layout schemas, transition order, PCG32 seed protocol, renderer specification and hand-authored transition fixtures.

No model weights, checkpoints or external dependencies are downloaded or executed by this harness.
