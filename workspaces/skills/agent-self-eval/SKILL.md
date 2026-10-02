---
name: agent-self-eval
description: >-
  Self-assess a just-finished answer on five axes — accuracy, completeness,
  clarity, actionability, conciseness — with evidence per score, or produce a
  structured scorecard when the user asks for an assessment. Load after a
  non-trivial task. Do not use to gate delivery or re-argue design.
metadata:
  short-description: Five-axis self-evaluation scorecard
---

# Agent Self-Evaluation

A short reflection after a non-trivial task catches omissions and overconfidence
before the user does. It rates the delivered output, not the effort behind it.

## When to use

- After a task spanning 3+ files, 50+ lines, or a multi-step workflow.
- After a debugging session with several failed attempts.
- When the user asks "how good was that?" or requests a scorecard.

Do not turn it into a pass/fail gate, penalize scope the user never requested,
or use it to relitigate decisions already made.

## How to run

1. **Collect the material**: the original request, the final output, and any
   verifying evidence (test output, grep results, file existence).
2. **Score each axis independently** 1–5. Do not average first and backfill.
3. **Cite evidence for every score below 5.** "Could be better" is not evidence;
   name the exact gap.
4. **Apply the evidence rule**: a 5 needs proof there is nothing to improve.
5. **Fix cheap gaps now** (under 30s) and flag the rest explicitly.
6. **Ask the self-check**: "Would the user agree with this assessment?"

## Quick reference

| Axis | Question | Catches |
|------|----------|---------|
| Accuracy | Are the claims correct? | Hallucinated APIs, false claims |
| Completeness | Did it cover what was asked? | Missed edges, skipped subtasks |
| Clarity | Is it understandable? | Jargon, missing structure |
| Actionability | Can the user act now? | Vague steps, no deliverable |
| Conciseness | Minimum words needed? | Filler, repetition, meta-commentary |

```text
5 exceptional   4 good   3 adequate   2 weak   1 poor
```

Scorecard format:

```text
Summary: Overall X.X/5 across 5 axes.
  Accuracy       5/5  + evidence
  Completeness   4/5  + covered / -> missing X
  Clarity        5/5  + structure
  Actionability  4/5  + deliverable / -> follow-up
  Conciseness    5/5  + density
  OVERALL        X.X/5
Critical (<=2): ...   Top improvements: 1. ... 2. ...
Verdict: deliver / fix N / redo
```

## Pitfalls

- All-5s with no evidence is self-congratulation, not evaluation.
- Scoring against features the user did not ask for (scope-creep penalty).
- Using the evaluation to re-argue a design choice after delivery.
- Subjective preference ("I don't like this") is not a gap; cite a concrete
  readability, testability, or correctness concern.
- Evaluating process length instead of the delivered output.

## Verification

The scorecard is trustworthy only when each non-5 cites a specific line, missing
file, or tool output. If you have no independent evidence (no tests, no diff to
inspect), say so and mark those scores provisional rather than asserting a 5.

<!-- adapted from affaan-m/ECC: skills/agent-self-evaluation/SKILL.md, agents/agent-evaluator.md -->
