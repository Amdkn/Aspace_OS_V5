# Toy World V1 — Baseline Smoke Report

Status: PASS — plumbing/correctness smoke only.

## Execution record

- Pull request: #55
- Branch: feat/jepa-cognitive-architecture-adr-v1
- Tested commit: e4eee98f5e16a7ee654ac8d41159f1cfad03ca93
- GitHub Actions run: 44862803347
- Python: 3.12
- Dependencies: Python standard library only
- Conformance suite: 18 tests passed
- Seeds: 0, 1, 42, 99
- Layouts: 4 deterministic templates
- Horizons: H1, H3, H5, H10
- Evaluations: 16

## Results

| Measure | Result |
|---|---:|
| Independent symbolic oracle — exact dynamic state | 100% |
| Independent symbolic oracle — exact rendered RGB | 100% |
| Persistence — mean pixel MAE across 16 evaluations | 0.2922453704 |

The oracle is implemented separately from the simulator transition function and is checked against both hand-authored transition fixtures and simulator rollouts. The exact oracle match establishes agreement between two implementations for this smoke corpus; it does not prove that every rule is correct or that the corpus is sufficiently broad.

Persistence repeats the initial RGB frame. Its non-zero aggregate MAE shows that some action sequences produce visible changes; zero-error rows are expected when the world remains visually unchanged at that horizon.

## Limits — do not over-interpret

- This is a four-layout smoke corpus, not the frozen train/validation/IID/OOD dataset.
- The fixed ten-action trace is not a statistically representative action distribution.
- The repeated replay check executes the same simulator twice; it is not yet an independent third-party replay implementation.
- No JEPA candidate, learned visual baseline, checkpoint or model weight was executed.
- No conclusion about JEPA performance, generalization, OOD robustness or production readiness can be drawn.

## Next gates

1. Expand hand-authored fixtures to every collision and mechanism edge case.
2. Add a separately implemented replay verifier and action-receipt hashing.
3. Validate all JSON Schemas and layout semantic invariants in CI.
4. Freeze dataset manifests only after those checks pass.
5. Run full persistence baseline across the frozen splits before candidate evaluation.
