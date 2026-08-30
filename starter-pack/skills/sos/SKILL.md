---
name: sos
description: Select the minimum relevant Skill bundle for a task and return one route, result, proof, and gate.
---

# SOS — Skill Operating System

Use `SOS` for the cheapest sufficient route. First frame through ProblemOS, then select only Skills justified by a concrete requirement. Report selected, rejected, unavailable, gate, and proof. Default to one route/execute/proof pass with at most five specialists. Do not auto-promote to SOS1 or SOS2 and do not invoke every installed Skill for volume.

## Contract

1. Parse outcome, artifact, constraints, owner, external gate, and proof.
2. Select the minimum Skill set that covers those requirements.
3. Explain briefly why each selected Skill is needed; list materially tempting but rejected Skills.
4. Execute one bounded route using one owner and one source of truth.
5. Verify the resulting artifact from the authoritative surface.
6. Return the result/blocker, proof, and continued numbered actions.

Stop expanding when another Skill, agent, or round would not add new evidence, remove a blocker, or change a decision. `SOS` is orchestration depth, not permission and not a request to produce more text.

Return `depth_level=STANDARD`, selected/rejected/unavailable Skills, result, proof, remaining gate, and next owner.
