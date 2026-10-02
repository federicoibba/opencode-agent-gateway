---
name: go
description: >-
  Idiomatic Go for services in this repo: error wrapping, interface design,
  concurrency and context, HTTP handlers, project layout, and testing hooks.
  Load when the user shares Go code, a Go design, or asks for a Go review. Do
  not use it for other languages or for API/database decisions owned elsewhere.
metadata:
  short-description: Idiomatic Go service patterns
---

# Go Service Patterns

Go favors boring, obvious code: explicit errors as values, small interfaces, and
concurrency that is easy to reason about. This skill covers that style plus the
tests a reviewer needs.

## When to use

- The user shares Go code, a diff, or a design for review or implementation.
- Touching goroutines, channels, `context.Context`, or shared state.
- Adding or reviewing HTTP handlers, repositories, or package boundaries.
- Designing package layout or deciding where an interface belongs.

## How to run

1. Ask for the Go files, the module path (`go.mod`), and the intended behavior.
   If a repo or shell is bound, run `go vet ./...`, `go test -race ./...`, and
   `staticcheck ./...` on the affected packages; otherwise ask for the diff.
2. Check placement: does the interface live where it is consumed, is
   `context.Context` the first parameter, are errors wrapped with `%w`.
3. Check concurrency: every goroutine has a cancellation path, channels are
   closed by the sender, shared state is mutex-guarded, `-race` is clean.
4. Check errors: no `_` discards, wrap with operation and identifier, use
   `errors.Is`/`errors.As` instead of `==`; panic only for programming bugs.
5. Check the boundary: handlers translate HTTP <-> domain, no concatenated SQL,
   resources closed with `defer` (not inside a loop).
6. Propose the smallest diff and list which tests to add or run.

## Quick reference

```go
// Wrap with context, unwrap with errors.Is
if err != nil {
    return nil, fmt.Errorf("load user %s: %w", id, err)
}
if errors.Is(err, domain.ErrNotFound) { /* 404 */ }

// Context first, cancellation always
func Fetch(ctx context.Context, id string) (*User, error) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    // ...
}

// Accept interfaces, return structs; define the port in the consumer
type UserStore interface { GetUser(ctx context.Context, id string) (*User, error) }
```

Layout: `cmd/<app>/main.go`, `internal/<feature>/{domain,service,repo,http}`,
`api/` for contracts, `testdata/` for golden files. Table-driven tests with
`t.Run`, `t.Helper`, `t.Cleanup`; run `go test -race -cover ./...`.

## Pitfalls

- Dropping an error returned from a goroutine; use `errgroup.WithContext`.
- Passing `context.Context` in a struct instead of as the first parameter.
- Unbuffered channel send with no receiver, or a `defer` inside a loop.
- Defining an interface next to the implementation rather than the consumer.
- Naked returns, ignored `Close()` errors, mixed value/pointer receivers.
- `time.Sleep` in tests; use channels or `t.Cleanup` instead.

## Verification

Name the package and the exact commands you would run (`go vet`, `go test
-race`, `staticcheck`). If no repo or shell is bound, say the diff was not
executed and ask the user to run those commands and paste the output.

<!-- adapted from affaan-m/ECC: skills/golang-patterns, agents/go-reviewer.md, skills/golang-testing -->
