---
name: refactoring
description: >-
  Remove dead code and duplicates and simplify for clarity while preserving
  behavior, in small reversible steps guarded by tests. Load when asked to
  clean up, de-duplicate, or simplify existing code. Do not use during active
  feature work, before a deploy, or on code without test coverage.
metadata:
  short-description: Safe dead-code removal and simplification
---

# Refactoring

Refactoring changes structure without changing behavior. If you cannot state
how behavior is preserved, you are editing, not refactoring.

## When to use

- Removing unused exports, files, dependencies, or commented-out code.
- Consolidating duplicate implementations.
- Simplifying recently modified code for clarity and consistency.

Do not use it during active feature development, right before a deploy, on code
you do not understand, or where there is no test net.

## How to run

1. **Establish the net first.** Confirm the relevant tests exist and pass. If a
   shell is bound, run them; otherwise ask the user for a green baseline before
   touching anything.
2. **Detect dead code.** If a shell is bound, run the project's analyzers
   (`knip`, `depcheck`, `ts-prune`, `vulture`, or the linter's unused rules);
   otherwise grep the shared code for references.
3. **Classify by risk**: SAFE (unused export or dep), CAREFUL (dynamic imports,
   reflection, string-based lookups), RISKY (public API, serialized names).
4. **Remove one category at a time**: deps → exports → files → duplicates.
5. **Grep for references**, including dynamic and string patterns, before
   deleting.
6. **Run tests after each batch** and keep each change small and reversible.
7. **Simplify** only where the result is demonstrably easier to maintain:
   extract deeply nested logic, use early returns, replace nested ternaries,
   consolidate duplication. Never change behavior to look clever.

## Quick reference

```text
SAFE     unused export, unused dependency, unreferenced file
CAREFUL  dynamic import, reflection, config/registry string, DI binding
RISKY    public API, DB/JSON field names, serialized enum values
```

```text
Order:  deps  →  exports  →  files  →  duplicates
Rule:   analyze → grep → remove small → test → commit → repeat
```

## Pitfalls

- "Unused" per a tool can still be called dynamically or from another package.
- Deleting a duplicate before updating all imports breaks the build.
- Rewriting behavior under the banner of "cleanup" — that is a feature change.
- Large single-shot refactors that are hard to review or revert.
- Removing code with no tests as the safety net; be conservative when in doubt.
- Unwinding over-abstracted single-use helpers can help, but do not churn code
  that the team deliberately structured.

## Verification

Build and tests must pass after each batch. If you cannot run them, list exactly
which files changed and have the user run the suite before merging. Name the
commands you would run and the expected green result.

<!-- adapted from affaan-m/ECC: agents/refactor-cleaner.md, agents/code-simplifier.md -->
