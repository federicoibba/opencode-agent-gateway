---
name: spec-writing
description: >-
  Turn a vague idea into a precise spec: problem framing, user stories,
  Given/When/Then acceptance criteria, scope and non-goals, success metrics, and
  edge cases. Load before planning or building a new capability. Do not use for
  implementation steps or architecture decisions.
metadata:
  short-description: Problem-first product specs
---

# Spec Writing

A spec fixes the problem, the actors, the promises, and what is explicitly out
of scope before any code is planned.

## When to use

- Converting a vague request, ticket, or idea into something buildable.
- Aligning on scope before planning or architecture work starts.
- A feature touches multiple surfaces and hidden constraints keep resurfacing.
- Reviewing whether acceptance criteria are actually testable.

Not for "should we build this?" validation or step-by-step implementation plans.

## How to run

1. Frame the problem in the user's words: who is affected, what hurts, how
   often, and what they do today. Do not start from a solution.
2. State the capability in one precise sentence: who gets what new ability, and
   what outcome changes because of it.
3. Write user stories as "As a <actor>, I want <capability>, so that <outcome>".
   Keep them outcome-oriented, not UI prescriptions.
4. Write acceptance criteria in Given/When/Then. Every criterion must be
   observable and testable, including failure and empty-state paths.
5. Fix scope: list non-goals explicitly and separate policy from preference.
6. Name success metrics that are not vibes: conversion, latency, error rate.
7. List edge cases and open questions. Mark unresolved product decisions instead
   of inventing truth; flag conflicts with existing constraints.

## Quick reference

```markdown
# <Capability>
## Problem
<who, pain, frequency, today's workaround>
## Capability
<one sentence>
## Stories & Acceptance Criteria
- As a <actor>, I want <capability>, so that <outcome>.
  - Given <context>, when <action>, then <observable result>.
  - Given <error/empty>, when <action>, then <safe result>.
## Scope
- In: ...
## Non-Goals
- ...
## Success Metrics
- <metric>: <target>
## Edge Cases & Open Questions
- ...
```

## Pitfalls

- Jumping to a solution or UI before stating the problem.
- Acceptance criteria that cannot be tested ("should be fast / intuitive").
- Missing non-goals, so scope creeps during implementation.
- Metrics like "more users" with no baseline or target.
- Inventing product truth where the user must decide; mark it open instead.
- Ignoring negative paths, permissions, and empty states.

## Verification

Read back one acceptance criterion and name the test or observation that would
prove it. List open questions explicitly, and state which requirements were
assumed rather than confirmed.

<!-- adapted from affaan-m/ECC: skills/product-lens, skills/product-capability -->
