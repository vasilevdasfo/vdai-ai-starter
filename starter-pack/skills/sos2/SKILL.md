---
name: sos2
description: Maximum useful SOS mode with at least three alternatives, bounded dialectic review, judge synthesis, execution, and independent proof.
---

# SOS2 — Maximum Useful Depth

Use only when the user explicitly says `SOS2`. Produce at least three materially different routes; keep generator, advocate, skeptic, evidence auditor, and judge roles separate; run two to three adversarial rounds; preserve minority objections; synthesize one result; execute only safe work; verify independently. Use at most ten relevant specialists and return `depth_level=MAX`. More tokens without new evidence or a changed decision do not count as depth.

## Maximum-depth protocol

1. Frame one decision packet: outcome, evidence, unknowns, constraints, owner, gate, and acceptance proof.
2. Generate at least three routes that differ in mechanism, risk, cost, or reversibility—not merely wording.
3. Round 1: advocates state their strongest case and required evidence independently.
4. Round 2: skeptics attack assumptions, failure modes, customer interpretation, and the opposite hypothesis.
5. Evidence audit: distinguish verified fact, source-backed inference, unsupported claim, and unknown.
6. Optional Round 3 only if a contradiction remains capable of changing the choice.
7. Judge synthesis: select, combine, or reject routes using explicit criteria; preserve the strongest minority objection.
8. Execute only the safe authorized portion and obtain independent readback.

Stop when additional debate repeats prior claims or cannot change the decision. Return `depth_level=MAX`, route matrix, evidence ledger, decision ledger, judge result, minority objection, executed artifact, independent proof, remaining human gate, and next owner.
