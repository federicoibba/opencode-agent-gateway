---
name: performance-web
description: >-
  Improve web performance for Vue 3 and Nuxt: Core Web Vitals targets, bundle
  analysis, route-level code splitting and lazy loading, image optimisation,
  and hydration/SSR cost. Load it for slow loads or interactions; not for
  micro-optimisations without a measurement, and not for React or Next.js.
metadata:
  short-description: Vue and Nuxt web performance
---

# Web performance (Vue / Nuxt)

Measure first, change one thing, measure again. Vite and Nuxt already do a lot;
your job is to remove the work that should not ship, not to micro-optimise.

## When to use

- Diagnosing slow page loads, slow interactions, or high main-thread CPU.
- Auditing bundle size or a Lighthouse/Core Web Vitals regression.
- Deciding what to code-split, lazy-load, or lazy-hydrate.
- Reviewing a PR that adds a heavy dependency or above-the-fold work.

Not for optimisation without a profile, and not for React/Next.js.

## How to run

1. **Set targets, then measure.** Aim for LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1
   on a mid-tier mobile profile. Profile with Lighthouse and the Performance
   panel; record a baseline before touching code.
2. **Cut bundle size.** Find the culprit with `rollup-plugin-visualizer` or
   `npx vite-bundle-visualizer`. Import directly instead of via barrel files,
   replace heavy dependencies, and lazy-load heavy components with
   `defineAsyncComponent` / Nuxt's `Lazy` prefix, guarded by `v-if`.
3. **Split at routes, not everywhere.** Nuxt already code-splits pages; make
   route boundaries meaningful before splitting leaf components. Load
   below-the-fold or non-critical UI only when it enters view.
4. **Optimise images.** Serve modern formats (AVIF/WebP) at the rendered size
   with `srcset`/`sizes`, set explicit `width`/`height` (or `aspect-ratio`) to
   avoid CLS, lazy-load below-the-fold images, and prioritise the LCP image with
   `fetchpriority="high"` and no lazy loading.
5. **Reduce hydration/SSR cost.** Hydrate only what is interactive; use Nuxt
   lazy hydration (`hydrate-on-visible`, `hydrate-on-idle`) for heavy islands.
   Keep server payloads shallow with `pick`, and keep first-render data small.
6. **Trim work per interaction.** Virtualise long lists, debounce expensive
   input handlers, and defer non-urgent updates. Reach for `v-memo`,
   `v-once`, `shallowRef` or `KeepAlive` only when a profile shows the cost.

## Quick reference

```text
Core Web Vitals targets (field, p75)
  LCP <= 2.5s    largest image/text block
  INP <= 200ms   interaction latency
  CLS <= 0.1     layout stability

Budget checks
  per-route JS: aim < 170 KB gzip
  LCP image:    eager, fetchpriority="high", dimensions set
  third-party:  load after hydration or on interaction

Vue/Nuxt levers           use when
  route split / Lazy       non-critical route or component
  defineAsyncComponent     heavy client-only widget
  lazy hydration           below-the-fold interactive island
  virtual list             hundreds+ rows
  v-memo / shallowRef      measured re-render or big-object cost only
```

## Pitfalls

- Optimising without a profile; you cannot tell signal from noise.
- Lazy-loading the LCP image or above-the-fold content — it delays LCP.
- Missing image dimensions; the reserve-less image shifts layout (CLS).
- Splitting every component into its own chunk; request overhead beats the win.
- Deeply reactive `ref` on huge immutable data; use `shallowRef` when replaced
  wholesale — with a measured reason.
- Third-party scripts in `<head>` blocking the first paint.

## Verification

Name the metric you changed and the before/after measurement (or the bundle
delta from the analyser). If no repo or shell tool is bound, ask for the
Lighthouse report and the relevant components; name what you could not verify,
such as field data or a device-specific result.

<!-- adapted from affaan-m/ECC: skills/react-performance (Vercel agent-skills, MIT), adapted to Vue/Nuxt -->
