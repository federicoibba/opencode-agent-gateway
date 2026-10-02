---
name: frontend-patterns
description: >-
  Cross-framework frontend architecture: component composition, state
  ownership, data-fetching boundaries, forms and validation, and explicit
  loading/empty/error states. Load it when structuring a feature or UI flow;
  not for framework syntax, which belongs to the vue or nuxt skills.
metadata:
  short-description: Frontend composition and state boundaries
---

# Frontend patterns

Architecture decisions that outlive any one framework: how data flows, who
owns state, and what the UI shows at every point in that flow.

## When to use

- Designing or refactoring a feature, page, or component tree.
- Deciding where state should live and how components communicate.
- Adding or reviewing forms, validation, and async UI states.
- The user says the UI "feels inconsistent" or the state "gets out of sync".

Not for language/framework syntax (load `vue` or `nuxt`) or design tokens
(load `design-tokens`).

## How to run

1. **Composition over inheritance.** Build compound components from small
   pieces (`Card`/`CardHeader`/`CardBody`) rather than flags that multiply
   variants. Slots/props are contracts, not escape hatches.
2. **Split container from presentational.** Containers own fetching, state and
   side effects; presentational components receive props and emit events. Keep
   API calls and store access out of leaf components.
3. **Own state at the lowest shared ancestor.** Local state stays local; push
   up only when a sibling needs it; use a store for genuinely global state.
   Derive values instead of storing duplicates that drift.
4. **Bound data fetching.** Fetch at route/container level, cache and dedupe
   with the project's data layer, and cancel or ignore stale responses on
   param changes. Never fetch in two components that need the same data.
5. **Model every async state.** For each fetch, render three explicit states —
   loading (skeleton, not blank), error (message plus retry), and empty
   (instruction, not an empty box). Success is the fourth.
6. **Forms.** Use a native `<form>` with `@submit.prevent`, a vetted validation
   layer, typed field values, and inline errors tied to fields. Disable submit
   only when disabled is safer than letting validation explain the problem.
7. **Adhere to the design system.** Reuse existing components and tokens before
   adding new CSS or dependency-level UI primitives.

## Quick reference

```text
Data flow choice
  same component ......... ref / local state
  child -> parent ........ props down, events up
  sibling / distant ...... lift state, or a store (Pinia)
  server data ............ data-layer composable (useFetch / query cache)
  theme, config, i18n .... provide / inject

Async UI states, always all three:
  loading -> skeleton with reserved height
  error   -> message + retry action
  empty   -> guidance + primary call to action
```

## Pitfalls

- Duplicated state that must be kept in sync; derive one from the other.
- Fetching the same resource in sibling components; centralise and dedupe.
- Storing derived values (totals, filtered lists) instead of computing them.
- Blank screens while loading, or empty states with no next action.
- Prop drilling five levels deep instead of composition, slots, or context.
- Reaching for a global store before local state stops working.

## Verification

Name the component or route you exercised and the states you saw (loading,
error, empty, success). Ask for a screenshot or running app when the flow is
visual; otherwise ask for the component files and say what you could not verify.

<!-- adapted from affaan-m/ECC: skills/frontend-patterns -->
