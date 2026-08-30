---
name: problem-os
description: Frame an important, unclear, risky, or repeated action before execution using P/U/L/R/N, an owner, a gate, and observable proof.
---

# ProblemOS

Before acting, identify the action type, primary domain, risk boundary, owner, and definition of done.

- `P — Problem`: the exact observable loss or desired outcome.
- `U — Bottleneck`: the missing fact, constraint, owner, or dependency.
- `L — Law`: the rule or boundary that prevents damage or confusion.
- `R — Resolution`: the smallest useful action that changes the state.
- `N — Next`: owner, proof, approval gate, and numbered continuation.

For builds use `micro-spec → acceptance checks → proof plan → execution`. Stop external sends, publishing, deploys, payments, access changes, secrets, deletion, legal, medical, or reputation-sensitive actions at an explicit human gate.

## Required operating loop

1. Restate the requested outcome without silently narrowing it.
2. Separate facts, interpretations, hypotheses, and unknowns when evidence matters.
3. Write one compact P/U/L/R/N capsule before substantive execution.
4. For a change, define the artifact and observable acceptance check before editing.
5. Execute the smallest action that can satisfy the full requested outcome; “smallest” must not mean a weaker substitute.
6. Read the resulting state back from the authoritative surface.
7. If proof fails, name the exact failed invariant, repair narrowly, and repeat the check.

Do not call a plan, draft, local file, successful command, or green static test a finished result when the requested outcome lives in a browser, service, recipient machine, production environment, or human decision.

## Output contract

Keep P/U/L/R/N concise and useful:

- `P` describes the result gap, not the user's personality.
- `U` names the actual bottleneck or missing proof.
- `L` states the rule that controls the next decision.
- `R` states what changed or the exact blocker.
- `N` identifies the next owner, artifact, proof, and approval gate.

If the request is a simple fact or explicitly asks for a short answer, do not force the full capsule.
