---
name: TDD Workflow
description: Drive a change test-first through Red, Green, Refactor.
tags: [testing, tdd]
---

Guide this change test-first with the `tdd` skill:

1. **Red** — write the smallest failing test that pins the behaviour.
2. **Green** — implement only enough to pass.
3. **Refactor** — clean up with the tests still green.

Call out the edge cases to cover (null, empty, invalid, boundary, error paths,
concurrency) and where mocks are needed. Name the coverage you expect.
