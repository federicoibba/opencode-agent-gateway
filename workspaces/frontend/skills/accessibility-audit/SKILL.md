---
name: accessibility-audit
description: Audit a UI for accessibility and keyboard support.
---

# Accessibility audit

Review an interface against the parts of WCAG 2.2 AA that apply to component
code, and report findings that a developer can act on.

## When to use

Use this when the user asks to "check accessibility", "audit this component",
"is this keyboard accessible", or shares markup for review.

## How to run

1. **Semantics first.** Replace generic elements with the correct one
   (`button`, `a`, `nav`, `main`, `ul`, `label`). A `div` with an `onClick` is a
   finding unless it also has a role, a tab stop and key handling.
2. **Keyboard.** Tab through the interface. Every interactive element must be
   reachable, operable with `Enter`/`Space` (buttons) or `Enter` (links), and
   must not trap focus. Custom widgets follow the ARIA Authoring Practices
   keyboard pattern.
3. **Names and roles.** Every control has an accessible name: a `<label for>`, an
   `aria-label`, or visible text. Icons need a text alternative; decorative
   images get `alt=""`.
4. **Focus visibility.** Never remove the focus ring without a visible
   replacement. Check `:focus-visible`.
5. **Contrast and motion.** Body text is at least 4.5:1, large text 3:1, UI
   boundaries 3:1. Respect `prefers-reduced-motion`.
6. **Forms and errors.** Errors are announced (live region), tied to the field,
   and not conveyed by colour alone.

## Quick reference

| Check | Failure looks like |
| --- | --- |
| Clickable `div`/`span` | no role, no tabindex, no key handler |
| Missing label | placeholder used as the only label |
| Focus ring removed | `outline: none` with no `:focus-visible` style |
| Icon-only button | no `aria-label` and no visually hidden text |
| Low contrast | grey text on a light grey background |

## Pitfalls

- Automated tools catch roughly a third of issues; do not treat a clean scan as a
  pass. Manual keyboard and screen-reader checks still matter.
- `aria-label` on a non-interactive element does nothing; put it on the control.
- `tabindex="0"` on everything is worse than leaving the DOM order alone.

## Verification

Name one concrete check you ran (keyboard walk-through, contrast measurement, or
an element-by-element role review) and one thing you could not verify.
