---
name: adr
description: >-
  When and how to record architecture decisions as short, numbered ADRs with
  context, decision, status, alternatives, and consequences. Load when the user
  picks between options, asks "why did we choose X", or says "ADR this". Do not
  use for trivial or easily reversible choices.
metadata:
  short-description: Record decisions with context
---

# Architecture Decision Records

An ADR captures one decision, the forces behind it, and what it costs — so the
next person does not relitigate it from memory.

## When to use

- The user says "record this", "ADR this", or "we decided to...".
- A choice is made between real alternatives (framework, DB, pattern, API).
- Someone asks "why is the codebase shaped this way?" (read ADRs first).
- During planning when an architectural trade-off is settled.

Do not record variable naming, formatting, or reversible local choices.

## How to run

1. If `docs/adr/` does not exist, ask before creating it, plus a `README.md`
   index and a `template.md`; do not create files unasked.
2. Extract the single decision and title it in the imperative or present tense:
   "Use PostgreSQL over MongoDB for the primary datastore".
3. Gather context: the problem, constraints, and forces (2-5 sentences max).
4. List the alternatives actually considered with pros, cons, and why rejected.
5. State consequences honestly: positive, negative, and risks with mitigations.
6. Assign the next number by scanning `docs/adr/` for `NNNN-short-title.md`.
7. Present the draft and write only after the user approves.
8. Append the row to the index `docs/adr/README.md`.

## Quick reference

```markdown
# ADR-0007: <Decision title>
**Date**: YYYY-MM-DD
**Status**: proposed | accepted | deprecated | superseded by ADR-NNNN

## Context
<problem, constraints, forces — 2-5 sentences>
## Decision
<1-3 sentences: what we will do>
## Alternatives Considered
### <Name>
- Pros: ... / Cons: ... / Why not: ...
## Consequences
### Positive
- ...
### Negative
- ...
### Risks
- <risk> — <mitigation>
```

Index row: `| [0007](0007-title.md) | Title | accepted | YYYY-MM-DD |`.

Lifecycle: `proposed -> accepted -> (deprecated | superseded by ADR-NNNN)`.
Supersede by writing a new ADR and updating the old status to point at it.

## Pitfalls

- Essays: if context exceeds ~10 lines it is too long; readable in 2 minutes.
- Omitting rejected alternatives, the rationale, or the negative consequences.
- Editing an accepted ADR instead of superseding it.
- Recording trivial decisions, or backfilling without the original date.

## Verification

Confirm the file path, the assigned number, and that the index row was added.
If you could not read `docs/adr/`, say so and ask the user to confirm the next
number rather than guessing.

<!-- adapted from affaan-m/ECC: skills/architecture-decision-records -->
