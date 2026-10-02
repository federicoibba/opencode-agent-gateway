---
name: Review Code
description: Review the current changes for correctness, quality and silent failures.
tags: [review, quality]
---

Review the code I share, in this order:

1. **Correctness** — does it do what it claims? Edge cases, error paths, nulls.
2. **Silent failures** — load the `silent-failures` skill and apply it.
3. **Quality** — load the `code-review` skill and apply its severity gates.

For each finding: file/line, the concrete failure mode, severity and the smallest
fix. End with the one change you would make first and what you could not verify.
