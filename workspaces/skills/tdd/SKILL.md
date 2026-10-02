---
name: tdd
description: >-
  Drive development with a failing test first (Red/Green/Refactor), covering
  boundary and error cases with unit, integration, and e2e tests. Load when
  writing a feature or bugfix or when told to test-first. Do not use to retrofit
  tests after code is frozen, or for throwaway spikes.
metadata:
  short-description: Red/Green/Refactor test-first workflow
---

# Test-Driven Development

Write the test that describes the behavior before the code. The test is the
spec; the implementation is the smallest thing that satisfies it.

## When to use

- Adding a feature, fixing a bug, or refactoring.
- The user says "test first", "TDD", or shares a plan with acceptance criteria.
- Wiring an endpoint, parser, or component whose contract is known.

Do not use it for pure exploration spikes or when you cannot run tests in the
current environment — state that and agree on a fallback first.

## How to run

1. **Restate the contract** in one sentence: input → behavior → output.
2. **RED** — write a failing test that asserts the contract. If a shell is
   bound, run it and confirm it fails for the right reason; otherwise produce
   the test and say it is unrun.
3. **GREEN** — write the minimum code to pass. No speculative features.
4. **Run again** — confirm green. If not, fix the code, not the assertion.
5. **REFACTOR** — remove duplication and improve names; tests stay green.
6. **Cover the edges** before moving on (see Quick reference).
7. **Check coverage as a floor**, not a target. Match the project's existing
   threshold; 80% is a common baseline, not proof of correctness.

## Quick reference

| Type | Tests | Scope |
|------|-------|-------|
| Unit | one function or class in isolation | fast, always |
| Integration | API plus DB plus wiring | always for endpoints |
| E2E | critical user journeys | few, high-value |

Edges to test every time:

```text
null / undefined input      empty string / empty array
invalid type                min / max boundary
error path (DB, network)    concurrent / duplicate calls
large input (10k+)          special chars (Unicode, SQL metacharacters)
```

```text
Red   → test fails for the expected reason
Green → minimal code, test passes
Refactor → behavior unchanged, tests still pass
```

## Pitfalls

- Testing implementation details (private state) instead of behavior.
- Tests that share mutable state or depend on execution order.
- Assertions that pass on empty or null output; assert the specific value.
- Not mocking external services (DB, cache, LLM, payment) — tests become flaky.
- Chasing a coverage number with trivial tests instead of edge cases.
- Mocking so much that the test only proves the mocks work.

## Verification

The strongest check is a test that fails before the change and passes after.
If tests cannot be run here, hand the user the exact command (`npm test`,
`pytest -q`) and the expected result, and label the suite as unverified.

<!-- adapted from affaan-m/ECC: agents/tdd-guide.md, skills/tdd-workflow/SKILL.md -->
