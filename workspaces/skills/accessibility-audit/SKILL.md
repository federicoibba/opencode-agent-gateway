---
name: accessibility-audit
description: >-
  Audit a UI against WCAG 2.2 AA: semantics, keyboard operability, accessible
  names and roles, focus management and appearance, contrast, form errors,
  reduced motion and native feel. Load it for "check accessibility" or a
  component review; not for a full legal conformance certification.
metadata:
  short-description: WCAG 2.2 AA UI audit
---

# Accessibility audit

Review an interface against the parts of WCAG 2.2 AA that apply to component
code, and report findings a developer can act on.

## When to use

- The user asks to "check accessibility", "audit this component", "is this
  keyboard accessible", or shares markup for review.
- Building or reviewing forms, modals, dropdowns, tooltips or tabs.
- Fixing a11y lint or code-review findings.

Not for a formal legal conformance statement; automated scans cover only about
a third of issues.

## How to run

1. **Semantics first.** Replace generic elements with the correct one (`button`,
   `a`, `nav`, `main`, `ul`, `label`). A `div` with `onClick` is a finding
   unless it also has a role, a tab stop and key handling.
2. **Keyboard.** Every interactive element is reachable in a logical order,
   operable with `Enter`/`Space` (buttons) or `Enter` (links), and never traps
   focus. Custom widgets follow the ARIA Authoring Practices keyboard pattern;
   modals trap and restore focus, and `Escape` closes.
3. **Names and roles.** Every control has an accessible name — `<label for>`,
   `aria-label` (icon-only controls), or visible text; `aria-labelledby` when a
   visible label exists. Match the control to its role; do not put `aria-label`
   on a non-interactive `div`.
4. **Focus.** Never remove the focus ring without a visible, high-contrast
   replacement (`:focus-visible`). WCAG 2.2 adds Focus Appearance (2.4.11),
   Focus Not Obscured (2.4.12), and 24×24 CSS px minimum Target Size (2.5.8).
5. **Contrast and reflow.** Body text ≥ 4.5:1, large text ≥ 3:1, UI boundaries
   and icons ≥ 3:1. Content reflows to 320px and survives 400% zoom without
   loss or horizontal scrolling.
6. **Forms and errors.** Label every field; errors are announced (live region),
   tied to the field with `aria-describedby`, marked `aria-invalid`, and not
   conveyed by colour alone. Avoid redundant entry (WCAG 3.3.7) and keep native
   `autocomplete` on.
7. **Motion, media and native feel.** Respect `prefers-reduced-motion`; never
   auto-play audio/video. Decorative images get `alt=""`, meaningful images get
   real text alternatives, icon-only buttons get a text alternative. Prefer
   native `<select>`/`<input>`/`<dialog>` unless the design truly needs a custom
   widget — then build it to feel native.

## Quick reference

| Check | Failure looks like |
| --- | --- |
| Clickable `div`/`span` | no role, no tabindex, no key handler |
| Missing label | placeholder used as the only label |
| Focus ring removed | `outline: none` with no `:focus-visible` style |
| Icon-only button | no `aria-label` and no visually hidden text |
| Low contrast | grey text on a light grey background |
| Error not linked | red text with no `aria-describedby`/`aria-invalid` |
| Tiny target | adjacent controls under 24×24 CSS px |
| Motion not gated | animation ignores `prefers-reduced-motion` |

```html
<label for="email">Email <span aria-hidden="true">*</span></label>
<input id="email" type="email" aria-required="true" aria-invalid="true"
       aria-describedby="email-error" autocomplete="email" />
<p id="email-error" role="alert">Enter a valid email address.</p>
```

## Pitfalls

- Automated tools catch roughly a third of issues; a clean scan is not a pass.
- Wrong ARIA is worse than none; prefer native semantics.
- `aria-label` on a non-interactive element does nothing.
- `aria-hidden="true"` on a focusable element traps keyboard users.
- `tabindex="0"` on everything is worse than leaving DOM order alone.

## Verification

Name one concrete check you ran (keyboard walk-through, contrast measurement, or
an element-by-element role review) and one thing you could not verify, such as
screen-reader output on a device you cannot run.

<!-- adapted from affaan-m/ECC: skills/frontend-a11y, agents/a11y-architect.md; base: workspaces/agents/frontend/skills/accessibility-audit -->
