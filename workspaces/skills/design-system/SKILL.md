---
name: design-system
description: >-
  Design and audit a component design system: tokens and scales, theming,
  component API and variant design, and component documentation. Load it when
  defining or reviewing a UI library; not for one-off styling fixes (use
  design-tokens) or cross-app state (use frontend-patterns).
metadata:
  short-description: Component system and variant design
---

# Design system

A design system is a small set of primitives, tokens and rules that make many
screens feel like one product. Favour fewer, better-defined parts over a large
undocumented surface.

## When to use

- Starting a component library or design system from an existing codebase.
- Auditing visual consistency before a redesign, or when UI "looks off".
- Designing a component's props, slots and variants.
- Reviewing a PR that adds or changes shared components.

Not for one-off style cleanup; load `design-tokens` for that.

## How to run

1. **Extract before inventing.** Scan CSS/Tailwind for existing colours, type,
   spacing, radii and shadows. Duplicates show where a token is needed; do not
   introduce a parallel palette.
2. **Three token layers.** Primitive (`--blue-500`), semantic (`--color-text`),
   component (`--button-bg`). Components reference semantic tokens; themes
   remap semantic tokens and never branch in code.
3. **Scales, not values.** A 4px-based spacing scale, a short type scale
   (5–7 steps), 2–3 radius/shadow steps. 14 spacing values is a list, not a
   system.
4. **Component API.** Props are the public contract: variants
   (`primary`/`secondary`/`ghost`), sizes, and states (`disabled`, `loading`,
   `invalid`). Prefer a small closed set over free-form style props; expose
   slots for content, not chrome. Document defaults.
5. **One variant mechanism.** Pick Tailwind Variants/CVA or a class map and use
   it everywhere; do not mix ad-hoc conditional classes with a variant system.
6. **States are part of the component.** Every interactive component defines
   default, hover, focus-visible, active, disabled, loading and error.
7. **Document with the code.** Each component needs a short purpose, the props
   table, variants, and one live example that is easy to update.

## Quick reference

```css
:root {
  --blue-500: #2563eb;              /* primitive */
  --color-action: var(--blue-500);  /* semantic  */
  --color-surface: #ffffff;
  --space-2: 8px;
  --radius-md: 8px;
}
[data-theme="dark"] {
  --color-surface: #111111;
  --color-action: #60a5fa;
}
```

```ts
type ButtonProps = {
  variant?: 'primary' | 'secondary' | 'ghost' // default 'primary'
  size?: 'sm' | 'md' | 'lg'                   // default 'md'
  disabled?: boolean
  loading?: boolean
}
```

## Pitfalls

- Tokens named after a value (`--grey-500`) lie after a rebrand; name by role.
- A free-form `style` prop re-opens the sprawl the system was meant to close.
- Missing `focus-visible` or dark-mode values leave the UI looking unfinished.
- Undocumented components get re-implemented per screen; document or delete.
- Gratuitous gradients, glass cards and excessive motion are a consistency
  smell; remove unless the brand calls for them.

## Verification

Name the component you inspected and the variants/states you rendered (light
and dark, keyboard focus). Ask for the token file and component source when
none are bound, and say which breakpoints or themes you could not verify.

<!-- adapted from affaan-m/ECC: skills/design-system -->
