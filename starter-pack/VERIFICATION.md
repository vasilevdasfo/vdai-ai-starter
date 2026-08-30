# VDAI AI Starter · Verification Playbook

Run these tasks after installation. A Skill is transferred only when its file is discoverable and its observable behavior passes.

| Skill | Verification task | Pass condition |
|---|---|---|
| `problem-os` | Diagnose one unclear real request. | Returns P/U/L/R/N, owner, gate and proof. |
| `economy-guard` | Report the current task weight. | Uses exact counters or says `unavailable`; never invents them. |
| `numbering-canon` | Continue the same topic in a second reply. | Uses the next unused positive action number; only `0` repeats. |
| `devils-advocate` | Challenge one proposed plan. | Gives 3–5 material objections and an evidence check. |
| `sos` | Select help for one bounded task. | Chooses the minimum relevant Skill bundle and one proof route. |
| `sos1` | Review a medium-complexity decision. | Frames, critiques, revises and verifies once. |
| `sos2` | Analyze a complex decision deeply. | Compares at least three routes, judges them and names proof. |
| `boardroom` | Examine one high-impact strategic choice. | Uses eight distinct perspectives and one judge synthesis. |
| `problem-to-action` | Convert a vague request into execution. | Names outcome, bottleneck, owner, safe action and proof. |
| `repeatable-work` | Turn one repeated job into a workflow. | Defines inputs, limits, artifact and acceptance check. |
| `numbered-next` | Finish any non-trivial result. | Shows numbered routes, exactly one recommendation and safe `0`. |

## Two-turn acceptance test

Turn 1:

```text
Use the installed VDAI AI Starter. Diagnose this real task with P/U/L/R/N: I repeatedly lose time handing work between people and AI. Name one owner, one artifact, one proof check, exact task weight or honest unavailable, and finish with numbered next actions, exactly one recommendation and a safe 0 route.
```

Turn 2 in the same task:

```text
Continue the same task. Challenge the recommended route with devils-advocate, then run the minimum useful SOS depth. Keep the numbering sequence; do not restart at 1.
```

Pass only when all 11 Skill files are present, the correct instruction file is merged, and both turns meet their conditions.
