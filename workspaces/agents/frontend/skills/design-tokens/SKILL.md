---
name: design-tokens
description: Define and apply a consistent design token system.
---

# Design tokens

Keep visual decisions in one place: colour, spacing, type, radius, shadow and
motion as named tokens, consumed by components instead of hard-coded values.

## When to use

Use this when adding or refactoring styles, theming, or when the user asks to
"clean up the styles", "add a dark theme", or "make spacing consistent".

## How to run

1. **Inventory.** Collect the literal values already in the codebase
   (`#1a1a1a`, `16px`, `0.25rem`, `12px`). Group them; duplicates are the point.
2. **Name by role, not value.** `--color-text-muted`, not `--grey-500`. A token
   survives a rebrand; a value-named token does not.
3. **Define a scale.** Spacing on a fixed step (`4px` base), a type scale with a
   small number of sizes, and a radius/shadow set with 2–3 steps.
4. **Theme by aliasing.** Light and dark themes redefine the same semantic tokens;
   components never branch on the theme.
5. **Migrate in one pass per component.** Replace literals with tokens, then
   delete the orphaned values.

## Quick reference

```css
:root {
  --color-surface: #ffffff;
  --color-text: #1a1a1a;
  --color-text-muted: #5c5c5c;
  --space-1: 4px;
  --space-2: 8px;
  --space-4: 16px;
  --radius-sm: 4px;
  --radius-md: 8px;
}
[data-theme="dark"] {
  --color-surface: #111111;
  --color-text: #f5f5f5;
}
```

## Pitfalls

- Too many tokens is the same problem as no tokens. If a scale has 14 spacing
  values, it is a list, not a system.
- Do not name a token after its current colour; it will lie after a redesign.
- Keep tokens in one file per theme layer so the override order is obvious.

## Verification

Point at the token file and one component that now reads only from tokens, and
confirm both themes render without hard-coded values left behind.
