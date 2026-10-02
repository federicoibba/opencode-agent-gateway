---
name: planning
description: >-
  Turn a feature request into a phased plan: requirements, codebase tracing,
  steps with file paths and risks, testing strategy, and success criteria. Load
  when asked to plan or break down work before implementation. Do not use for
  executing the change or for product-level "should we build this".
metadata:
  short-description: Phased implementation plans
---

# Planning

A plan is a sequence of verifiable, independently mergeable steps with exact
paths and the risks called out up front.

## When to use

- The user asks for a plan, breakdown, or approach before coding.
- A change spans multiple files, services, or migrations.
- Scoping is unclear or the request needs clarifying questions.
- Refactoring a feature whose existing behavior must be preserved.

Not for "should this exist?" (use spec-writing) or for making the edits.

## How to run

1. Restate the requirement and list assumptions and constraints. Ask at most a
   few blocking questions; mark unknowns instead of inventing answers.
2. Trace the codebase: find entry points, follow the call chain, and note where
   data is transformed and errors are handled. If a repo is bound, read the
   files and grep for the symbols; otherwise ask the user to share them.
3. Identify the layers touched and reuse existing patterns and utilities.
   Prefer extending over rewriting.
4. Break the work into phases, each independently deliverable: types/interfaces,
   core logic, integration, edge cases, then docs. Order by dependency.
5. For each step give the exact file path, action, why, dependency, and risk
   (low/med/high). No step may require all prior steps just to be testable.
6. Define the testing strategy: unit targets, integration flows, and the one
   end-to-end journey that proves the feature.
7. List risks with mitigations, and success criteria as checkboxes.

## Quick reference

```markdown
# Implementation Plan: <Feature>
## Overview
<2-3 sentences>
## Requirements
- <requirement / assumption>
## Implementation Steps
### Phase 1: <name>
1. **<step>** (File: path/to/file)
   - Action / Why / Depends on / Risk
## Testing Strategy
- Unit: <files>  - Integration: <flows>  - E2E: <journey>
## Risks & Mitigations
- **Risk**: <...>  - Mitigation: <...>
## Success Criteria
- [ ] <observable outcome>
```

Sizing: Phase 1 = smallest valuable slice; Phase 2 = complete happy path;
Phase 3 = errors and edge cases; Phase 4 = performance and observability.

## Pitfalls

- Steps without file paths or with vague actions ("update backend").
- A single mega-phase that cannot ship until everything is done.
- Hidden dependencies between supposedly independent steps.
- No testing strategy, or tests deferred to a final phase.
- Inventing requirements instead of surfacing open questions.

## Verification

Point to the plan's success criteria and name the first step you would execute.
Confirm the traced file paths exist; if you had no repo access, say the plan is
based on the user's description and still needs path verification.

<!-- adapted from affaan-m/ECC: agents/planner.md, agents/code-explorer.md, skills/plan-canvas -->
