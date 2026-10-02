---
name: error-handling
description: >-
  How this repo surfaces and propagates failures: no swallowed errors, wrapping
  with context, fail-fast vs fallback, timeouts/retries/backoff, and logging at
  boundaries. Load when reviewing error paths, retries, or a suspicious silent
  failure. Do not use for validation rules or API shape, which live elsewhere.
metadata:
  short-description: Predictable error propagation
---

# Error Handling

Errors are values and contract: carry enough context to diagnose and respond.

## When to use

- Reviewing a diff for catch/error branches, retries, or fallbacks.
- A feature "works" but fails quietly, or logs are too thin to debug.
- Wrapping a network, file, database, or external API call.
- Deciding whether to retry, fall back, or fail the request.

## How to run

1. Find every failure path: `_` discards, empty catches, `.catch(() => [])`,
   defaults that mask a real failure, and log-and-forget handlers.
2. Decide handle / wrap-and-return / propagate. Wrap with the operation and
   identifier: `fmt.Errorf("charge order %s: %w", id, err)`.
3. Keep the original error reachable; branch with `errors.Is`/`errors.As` (Go)
   or the typed-error hierarchy, not string matching.
4. Fail fast on programmer errors; use a fallback only when the caller tolerates
   absence, and log that the fallback fired.
5. Bound every external call with a `context` timeout. Retry only idempotent,
   transient failures, with exponential backoff, jitter, and a cap; never retry
   4xx or non-idempotent writes without an idempotency key.
6. Log once, at the boundary, with a request/correlation id and the full error;
   return a safe generic message to clients. Never log-and-rethrow at each layer.
7. If a repo or shell is bound, grep the user-provided diff; otherwise ask.

## Quick reference

```go
// Domain sentinels + wrapping
var ErrNotFound = errors.New("not found")
func (r *Repo) Find(ctx context.Context, id string) (*User, error) {
    u, err := r.db.Query(ctx, "select ... where id = $1", id)
    if errors.Is(err, sql.ErrNoRows) {
        return nil, fmt.Errorf("find user %s: %w", id, ErrNotFound)
    }
    if err != nil {
        return nil, fmt.Errorf("find user %s: %w", id, err)
    }
    return u, nil
}
// Handler maps errors to HTTP; logs unexpected detail once
switch {
case errors.Is(err, domain.ErrNotFound):
    writeError(w, 404, "not_found", "User not found")
default:
    slog.ErrorContext(ctx, "unexpected error", "err", err, "request_id", rid)
    writeError(w, 500, "internal_error", "An unexpected error occurred")
}
```

Retry: `maxAttempts=3`, base ~500ms, max ~10s, jitter, and a `retryIf` that
excludes 4xx. Timeouts always come from the incoming context.

## Pitfalls

- `catch {}`, `_ = f()`, or `.catch(() => [])` with no log or propagation.
- Wrapping without `%w`, so `errors.Is` silently stops matching.
- Retrying a non-idempotent write or a 400/401/404; retrying with no cap.
- Leaking stack traces, SQL, or internal IDs into the client response.

## Verification

Name one failure path you traced end to end and the response/log it produces.
Say whether a repo or shell let you inspect the diff; if not, ask for it.

<!-- adapted from affaan-m/ECC: skills/error-handling, agents/silent-failure-hunter.md -->
