---
name: Review UI
description: Run an accessibility and design review over the current UI.
---

Review the UI I am about to describe or share, using this order:

1. **Correctness** — does the markup do what it claims? Any broken states,
   missing loading/empty/error handling?
2. **Accessibility** — semantics, keyboard reachability, focus visibility,
   labels, contrast. Load the `accessibility-audit` skill and follow it.
3. **Design system** — are spacing, colour and type coming from tokens? Load the
   `design-tokens` skill if they are not.
4. **Performance** — obvious re-render or layout-thrash risks only; skip
   micro-optimisations.

For each finding give: the element or line, why it is a problem, and the smallest
fix. End with the one change you would make first and what you could not verify
from what I gave you.
