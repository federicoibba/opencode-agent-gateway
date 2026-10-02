---
name: code-review
description: >-
  Review a diff, PR, or set of files for correctness, security, and
  maintainability, filtering findings by confidence so only real issues are
  reported. Load when the user shares code or a diff and asks for a review.
  Do not use to implement the change or run the code under review.
metadata:
  short-description: High-signal review of shared diffs
---

# Code Review

Review the change in front of you, not the whole repository: aim for a small number of defensible findings plus a clear verdict.

## When to use

- The user shares a diff, PR, patch, or files and asks "review this".
- A change is about to merge and needs a quality and security pass.
- You are asked whether code is safe to ship.

Do not use it to author the feature, to execute the code, or to demand a stack
change the project did not ask for.

## How to run

1. **Establish scope.** Identify which files changed and what feature or fix
   they belong to. If a repo and shell are bound, run `git diff` and
   `git diff --staged`; otherwise ask the user to paste the diff or files.
2. **Read the surrounding code.** Read the full files and their callers, imports,
   and tests. Many apparent bugs are already handled one frame up.
3. **Work the checklist** from CRITICAL to LOW (see Quick reference).
4. **Apply the pre-report gate** to every candidate finding (below).
5. **Report by severity** and end with the summary table and verdict.

## Pre-report gate

Drop or demote a finding unless all four hold:

1. **Exact line** — you can name file and line. "Somewhere in auth" is dropped.
2. **Concrete failure mode** — name the input, state, and bad outcome.
3. **Context read** — callers, guards, types, and tests were checked.
4. **Defensible severity** — a missing comment is LOW; an unhandled `any` in a
   fixture is not CRITICAL.

Every HIGH/CRITICAL finding needs the snippet, the failure scenario, and why
existing guards do not catch it; otherwise demote or drop. Zero findings is valid.

## Quick reference

| Severity | Examples | Verdict impact |
|----------|----------|----------------|
| CRITICAL | Hardcoded secrets, injection, auth bypass, path traversal | Block |
| HIGH | Missing error handling, N+1, missing timeouts, no authz check | Warn |
| MEDIUM | Inefficient algorithm, missing caching, unclear error messages | Info |
| LOW | Naming, TODOs without tickets, formatting | Note |

Finding format:

```text
[SEVERITY] Short title
File: path:line
Issue: what is wrong and the concrete failure mode.
Fix: the specific change, with a before/after snippet when short.
```

## Pitfalls

- Skip stylistic nits and unchanged code unless a CRITICAL security issue.
- Consolidate repeats; do not flag patterns a caller, framework, or type handles.
- Do not manufacture findings; a clean APPROVE is expected. Match project
  conventions rather than suggesting a rewrite.

## Verification

State the verdict (APPROVE / WARNING / BLOCK) with the severity counts that
justify it. If you could not read the callers or tests, say which findings are
therefore unverified and ask the user for those files.

<!-- adapted from affaan-m/ECC: agents/code-reviewer.md -->
