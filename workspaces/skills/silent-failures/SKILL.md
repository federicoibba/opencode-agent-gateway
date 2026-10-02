---
name: silent-failures
description: >-
  Hunt for errors that are swallowed, logged without context, given dangerous
  fallbacks, or stripped of stack traces, plus missing timeouts and rollbacks.
  Load when reviewing error handling or debugging hard-to-reproduce bugs. Do
  not use to design the happy path or write new features from scratch.
metadata:
  short-description: Find swallowed errors and bad fallbacks
---

# Silent Failures

Silent failures turn a clear crash into a mystery: find where errors vanish or are masked, then prescribe an explicit failure path.

## When to use

- Reviewing `try/catch`, promise chains, retries, or error middleware.
- A bug is intermittent or "worked yesterday" and the logs are unhelpful.
- Adding network, file, database, or transaction code.
- The user shares a diff that touches error handling.

Do not use it to write net-new features or to argue for a logging framework the
project does not use.

## How to run

1. **Collect the code.** With a repo and shell, grep for `catch`, `except`,
   `.catch(`, `rescue`, `ignore`, and `return null`; otherwise ask for the files.
2. **Classify each hit** against the hunt targets below.
3. **Trace the consequence** — for each swallowed error, name what the caller or
   user now believes that is false.
4. **Report** with location, severity, impact, and a fix.
5. **Recommend one explicit path** per finding: handle, re-throw with context, or
   fail the operation.

## Hunt targets

- **Empty catch blocks** — `catch {}`, `except: pass`, errors returned as
  `null`/`[]` with no signal.
- **Inadequate logs / lost traces** — logs missing the error object or
  correlation id; `throw new Error(e.message)` that drops the cause.
- **Dangerous fallbacks** — `.catch(() => [])`, default values that hide a real
  failure, "graceful" paths that make downstream bugs harder to diagnose.
- **Missing timeouts / rollback** — network, file, and DB calls with no timeout;
  transactional work with no rollback on partial failure.

## Quick reference

```text
Finding
  Location: path:line
  Severity: CRITICAL | HIGH | MEDIUM | LOW
  Issue:    the swallowed or masked error
  Impact:   the wrong state or false success that results
  Fix:      handle, re-throw with context, or fail loudly

Severity guide
  CRITICAL  money/data integrity: ignored write error, no rollback
  HIGH      user-visible feature silently returns wrong or empty data
  MEDIUM    diagnosability lost: context or cause dropped from logs
  LOW       noisy log level or missing correlation id
```

## Pitfalls

- A `try/catch` at a boundary that logs and re-throws is not a silent failure.
- Fire-and-forget telemetry or logging is often intentional; check for a comment.
- Do not recommend catching everything; prefer letting errors propagate.
- Retrying non-idempotent writes without a guard can duplicate side effects, and
  adding a timeout creates a new failure mode; call both out.

## Verification

For each finding, the fix should make the failure observable: a thrown error, a
logged cause, a non-zero exit, or a rolled-back transaction. If you cannot reach
the code to confirm the runtime path, ask the user to share the relevant file or
the log line that shows the failure went missing.

<!-- adapted from affaan-m/ECC: agents/silent-failure-hunter.md, skills/error-handling/SKILL.md -->
