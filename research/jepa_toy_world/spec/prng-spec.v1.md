# JEPA Toy World — PRNG and Seed Protocol V1

Status: Proposed, normative for V1 episode generation.

## 1. Scope
The transition function is deterministic and consumes no random values. Randomness is used only by the versioned layout/episode generator. This document freezes the generator so a seed has a portable meaning independent of Python's random module or runtime version.

## 2. Algorithm
Use PCG-XSH-RR 64/32 (PCG32), with unsigned 64-bit state arithmetic and unsigned 32-bit output.

- Multiplier: 6364136223846793005 (0x5851F42D4C957F2D).
- Increment: 1442695040888963407 (0x14057B7EF767814F), a fixed odd V1 stream selector.
- State arithmetic wraps modulo 2^64.

One output step:
1. Save oldstate = state.
2. Set state = oldstate * multiplier + increment (mod 2^64).
3. Compute xorshifted = (((oldstate >> 18) XOR oldstate) >> 27) & 0xffffffff.
4. Compute rot = (oldstate >> 59) & 31.
5. Return rotate-right-32(xorshifted, rot).

Initialization from an unsigned 64-bit seed:
1. Set state to zero.
2. Advance once using the state update (discard output).
3. Add seed modulo 2^64 to state.
4. Advance once more (discard output).

The seed domain is integer [0, 2^64 - 1]. Reject values outside this range; do not silently mask or coerce negative seeds.

## 3. Bounded integers
For a uniform integer in [0, bound), require 1 <= bound <= 2^32. Use rejection sampling with threshold (2^32 - bound) % bound: draw 32-bit values until value >= threshold, then return value % bound. Do not use modulo-only sampling.

## 4. Stream consumption contract
- The V1 default layout generator consumes exactly one bounded draw, randbelow(4), to select one of four immutable layout templates in index order. No other random values are consumed.
- Candidate inference and simulator transitions never share or advance the generator.
- Adding a new random choice changes the generator protocol and requires a new version or an explicitly versioned generator substream.
- A seed manifest records prng: "pcg32-xsh-rr-v1", the unsigned seed, layout-generator version, layout ID and canonical layout hash.
- No reliance on language-level hash randomization, unordered set iteration or platform-dependent iteration order is permitted.

## 5. Conformance
The implementation must publish known-answer tests covering initialization and at least ten successive outputs for seeds 0, 1 and 42, plus bounded-integer rejection cases. These vectors are implementation acceptance evidence and must be committed with simulator tests before dataset manifests are frozen.

## 7. Versioning
Any change to constants, initialization, output transformation, bounded sampling or consumption order requires a new PRNG protocol version. V1 benchmark manifests are immutable once frozen.
