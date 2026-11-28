# JEPA Toy World — Renderer Contract V1

Status: Proposed, normative for visual observation Track A/B.

## 1. Output contract
- Image dimensions: exactly 192 × 192 pixels.
- Pixel format: RGB, 8 bits per channel, 3 bytes per pixel.
- Color mode: opaque RGB; no alpha channel, palette mode, color profile conversion or post-processing.
- Grid: 12 columns × 12 rows, exactly 16 × 16 pixels per cell.
- Origin: top-left. Cell (x, y) occupies pixels [16x, 16x+15] × [16y, 16y+15].
- Camera: fixed, orthographic, no camera motion, scaling, antialiasing, texture, lighting, gradients or randomness.
- Encoding for stored artifacts: PNG, lossless, with metadata stripped. The in-memory canonical observation is the decoded RGB byte array, not PNG file bytes.

## 2. V1 palette
All values are literal RGB triples.

| Element | RGB |
|---|---|
| Floor | (238, 240, 232) |
| Wall | (52, 61, 66) |
| Grid line | (210, 216, 207) |
| Agent body | (35, 105, 190) |
| Agent facing marker | (245, 245, 245) |
| Crate | (171, 111, 54) |
| Crate inset | (112, 70, 36) |
| Manual gate closed | (155, 55, 55) |
| Manual gate open | (205, 220, 205) |
| Pressure gate closed | (115, 65, 145) |
| Pressure gate open | (205, 190, 220) |
| Plate inactive | (125, 130, 125) |
| Plate active | (235, 190, 55) |
| Goal | (55, 155, 95) |

## 3. Draw order and geometry
Render in this order, back to front:
1. Floor fill for every cell.
2. Wall fills.
3. Goal marker: centered 10 × 10 pixel square.
4. Pressure plates: centered 8 × 8 pixel square; active/inactive palette according to state.
5. Gates: centered 12 × 4 pixel horizontal rectangle; use mode/state palette. Gate cell is still one grid cell.
6. Crates: inset 2 pixels from cell bounds (12 × 12); draw 2-pixel inset border using crate-inset color.
7. Agent: centered 10 × 10 pixel square; facing marker is a 4 × 4 pixel square positioned in the center of the leading edge.
8. Grid lines: 1-pixel lines on cell boundaries, excluding the outermost image border.

If an entity shares a cell in an invalid state, rendering must not conceal the invalidity: the simulator/layout validator rejects the state before rendering.

## 4. Deterministic encoding
- Render from canonical state plus immutable layout only.
- No font, text, timestamps, IDs, debug overlays or evaluator annotations appear in candidate-visible pixels.
- No random variation, animation, sub-pixel coordinates or interpolation.
- Identical state/layout/renderer version must produce byte-identical RGB arrays.
- Renderer identity is toy-world.renderer.v1; any geometry, palette, draw-order or encoding change requires a version bump.

## 5. Golden reference

For the canonical V1 seed-42 generated layout and initial state, renderer identity toy-world.renderer.v1 must produce RGB byte SHA-256:

- Seed: 42
- Layout: layout-03
- SHA-256: 84d27dff64030f19d0fd2739b17f4bbf390bc88821c92a85f3853481f8a48564

This digest is over the raw row-major RGB byte array, not the PNG encoding.

## 6. Tests
Required tests:
- Exact dimensions, channel count and dtype.
- Golden RGB byte hashes for at least one fixture containing each drawable element and gate state.
- Repeated render equality.
- Candidate observation contains pixels only; no state object, layout object, hash, seed, episode metadata or evaluator receipt is attached.
