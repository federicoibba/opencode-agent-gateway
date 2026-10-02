---
name: nuxt
description: >-
  Build and debug Nuxt 4 apps: app/ layout, auto-imports, useFetch and
  useAsyncData, server/api routes, middleware, route rules, runtimeConfig and
  hydration safety. Load it for Nuxt pages, server routes or hydration
  mismatches; not for plain Vue or a Vite-only SPA.
metadata:
  short-description: Nuxt 4 app patterns
---

# Nuxt 4

Nuxt is the full-stack Vue framework: file-based routing, auto-imports, Nitro
server routes and per-route rendering rules. Match existing conventions first.

## When to use

- The user shares a Nuxt page, component, `server/api` route or `nuxt.config.ts`.
- Debugging hydration mismatches, payload size, or SSR/client differences.
- Choosing a rendering strategy (SSR, SSG, ISR, SWR, client-only).
- Page/component data fetching with `useFetch`, `useAsyncData` or `$fetch`.

Not for vanilla Vue or a Vite SPA with no Nitro server.

## How to run

1. **Layout.** Source lives under `app/` (`pages`, `components`, `composables`,
   `layouts`, `middleware`), the server under `server/`; route handlers go in
   `server/api` and `server/routes`.
2. **Auto-imports.** `ref`, `computed`, `useFetch`, `useRoute` are auto-imported
   inside the app; import explicitly in plain `.ts` or tests where Nuxt context
   is absent.
3. **Data fetching.** `await useFetch()` for SSR-safe reads — data flows into
   the Nuxt payload so hydration does not refetch. Use `useAsyncData` for
   non-`$fetch` fetchers or composed sources with a stable key and a
   side-effect-free handler. Use `$fetch` only for user-triggered writes.
4. **Server and config.** Validate body/params/query with zod/valibot inside
   `defineEventHandler`; never trust the client. Keep server-only config out of
   `runtimeConfig.public`, which ships to the browser.
5. **Rendering and hydration.** Prefer `routeRules` per route group
   (`prerender`, `swr`, `isr`, `ssr: false`); name global middleware
   `*.global.ts` or opt in via `definePageMeta`. Keep the first render
   deterministic — no `Date.now()`/`Math.random()`/storage reads in SSR state;
   guard browser APIs behind `onMounted`, `import.meta.client`, `<ClientOnly>`
   or `.client.vue`.

## Quick reference

```ts
// app/pages/articles/[slug].vue
const route = useRoute()
const { data, status, error, refresh } = await useAsyncData(
  () => `article:${route.params.slug}`,
  () => $fetch(`/api/articles/${route.params.slug}`),
)
// nuxt.config.ts
export default defineNuxtConfig({
  routeRules: {
    '/': { prerender: true },
    '/products/**': { swr: 3600 },
    '/admin/**': { ssr: false },
  },
})
```

## Pitfalls

- `useAsyncData`/`useFetch` without a key duplicates requests and breaks cache
  dedup.
- Top-level `$fetch` in a page runs on server and client, causing a double fetch
  and hydration flicker.
- `ssr: false` is an escape hatch, not a default fix for mismatches.
- `window`/`process.client` in top-level setup crashes the server build.
- Secrets in `runtimeConfig.public` ship to the browser; keep them server-side.
- `<ClientOnly>` around SEO content hides it from crawlers.

## Verification

Name one page and the rendering mode you confirmed (SSR HTML, or a hydration
payload instead of a refetch). Ask for the Nuxt version and repo/shell access;
name what you could not verify, such as platform ISR or edge caching.

<!-- adapted from affaan-m/ECC: skills/nuxt4-patterns -->
