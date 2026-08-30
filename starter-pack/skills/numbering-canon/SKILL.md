---
name: numbering-canon
description: Keep selectable actions in one task-local sequence and separate menu numbers, stable IDs, and counters.
---

# Numbering Canon

- A new topic starts at `1`.
- The same topic continues from the next unused positive number across replies and revisions.
- Every positive number already shown is consumed, even if it was not selected.
- Only `0` repeats. It means all currently visible safe actions and never bypasses a human gate.
- Menu routes use `N = action`; stable IDs always have prefixes such as `O-007`; counters include a word label.
- Do not reset numbering merely because a goal, branch, or continuation was created.
- Before the menu, state the observable result or exact blocker and mark exactly one recommended route with a reason.

## State rules

- Track numbering per task/topic, not per chat message.
- A revision of the same answer does not free or reuse its positive numbers.
- A genuine topic or project change starts a new local sequence at `1`; do not carry unrelated menu state across topics.
- Do not confuse phone numbers, chat IDs, dates, versions, counts, or ordered prose with selectable routes. Prefix stable identifiers and label counters.
- Use `N = action`, not `N.` or an em dash, for selectable routes.
- Keep exactly one starred recommendation and state `Почему:` on that route.
- Include one clearly labeled unconventional route only when it is meaningful, not as decoration.
- `0` executes all visible safe routes, but excludes any route still waiting for deploy, send, purchase, access, deletion, or another explicit approval.

When prior numbering cannot be recovered reliably, say that state is unavailable and ask for the last visible menu rather than guessing or silently resetting.
