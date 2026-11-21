# JEPA Toy World — Transition Rules V1

Status: Proposed, paired with state, action and layout schemas; PRNG, renderer and fixture contracts.

## 1. Coordinate and map rules

- World dimensions are 12 columns × 12 rows.
- Origin is top-left; x increases east, y increases south.
- Static walls, floor, spawn cells and fixed landmarks belong to an immutable, versioned layout artifact identified by `layout_id` and `layout_hash`.
- The layout hash is SHA-256 over canonical layout serialization.
- The outer boundary is blocked; no entity may occupy a wall or out-of-bounds cell.
- At episode reset, all entity positions must be unique except where a future version explicitly defines a permitted overlap.

## 2. Action and movement rules

One action is applied per tick.

- `NOOP`: agent does not move.
- `MOVE_N/S/E/W`: attempt to move one cell in the specified direction; update facing even if movement is blocked.
- If the destination is empty floor, move the agent there.
- If the destination contains a crate, attempt to push it one cell in the same direction.
- A crate push succeeds only if the crate's destination is in bounds, non-wall, not occupied by another crate, not occupied by the agent, and not blocked by a closed gate.
- If movement or pushing is blocked, the agent remains in place; no entity is moved.
- Moving into a closed gate is blocked.
- A movement action never pushes multiple crates.

## 3. Interaction rules

- `INTERACT` checks the cell immediately in front of the agent, using its current facing.
- If that cell contains a manual gate, toggle its `open` value.
- If it contains no manual gate, the action has no effect.
- Pressure gates cannot be toggled directly; their state is derived from their linked pressure plate.
- Invalid or ineffective actions still consume one tick.

## 4. Pressure plate rules

- Each pressure plate references exactly one gate through `controls_gate_id`.
- A pressure plate is active when the agent or any crate occupies its cell.
- After movement/push resolution, recompute plate activity.
- A pressure gate is open if and only if its linked plate is active.
- A manual gate retains its explicitly toggled state.
- A plate may control only one pressure gate in V1; no gate may be controlled by multiple plates.
- Layout validation must reject missing gate references and mode mismatches.

## 5. Tick ordering

For state (S_t) and action (a_t), compute (S_{t+1}=T_{v1}(S_t,a_t)) in this exact order:

1. Validate action record and episode/tick identity.
2. Apply facing update for directional movement actions.
3. Resolve movement or crate push against the current collision map.
4. Resolve `INTERACT` against the post-movement agent position and facing only when the action is INTERACT.
5. Recompute pressure-plate occupancy.
6. Derive pressure-gate open/closed state.
7. Evaluate goal reached (agent occupies goal cell).
8. Set terminal equal to goal reached.
9. Increment tick by one and emit the new state.

The environment does not accept another action after terminal=true; caller must reset.

## 6. Determinism and replay

- Transition logic contains no random sampling.
- Randomness is restricted to episode/layout generation and must use an explicitly versioned PRNG and seed manifest.
- Given identical canonical state, action and transition version, output state bytes and state hash must be identical.
- Every action receipt includes prior-state hash and resulting-state hash.
- Canonical serialization sorts crates, gates and plates by stable ID.
- Floating-point values are not used in canonical state or transition logic.

## 7. Layout and state invariants

- Agent, crates, gates, plates, walls and goal obey occupancy constraints defined by the layout validator.
- All entity IDs are unique within their entity type and stable for the episode.
- Every pressure plate references an existing pressure-mode gate.
- Every pressure-mode gate has exactly one linked plate.
- Manual gates have no pressure-plate controller.
- A closed gate blocks agent and crate movement.
- Goal position is static for the episode.
- Terminal is true if and only if goal.reached is true.

## 8. Versioned supporting contracts

- Layout structure: [layout-schema.v1.json](layout-schema.v1.json).
- Seeded episode generation: [prng-spec.v1.md](prng-spec.v1.md).
- Candidate-visible pixels: [renderer-spec.v1.md](renderer-spec.v1.md).
- Hand-authored expected transitions: [transition-fixtures.v1.json](transition-fixtures.v1.json).

The immutable layout owns positions of walls, gates, pressure plates and the goal. The dynamic state stores entity identity and changing properties; gate and plate coordinates are resolved by stable ID through the episode layout. The layout artifact is canonicalized before SHA-256 hashing and is never sent to candidate models.

## 9. Remaining implementation gates

- [ ] Implement and validate the layout canonical serializer and hash.
- [ ] Implement PCG32 and publish known-answer vectors.
- [ ] Implement the renderer and golden RGB hashes.
- [ ] Convert every fixture into executable transition tests.
- [ ] Ratify the combined contracts before simulator implementation.
