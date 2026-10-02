---
name: vite
description: >-
  Configure and debug Vite projects: config, plugins, env vars, dev proxy,
  dependency pre-bundling, manual chunks, library mode and SSR externals, plus
  Rolldown migration notes. Load it for vite.config.ts or build/dev-server
  problems; not for webpack, Turbopack or Nuxt-only config.
metadata:
  short-description: Vite config, plugins and builds
---

# Vite

Vite serves native ESM in dev and bundles with Rolldown (v7+) / Rollup (v5–v6)
for production, with Oxc minification. Prefer its conventions over custom
tooling.

## When to use

- Editing `vite.config.ts`, adding a plugin, or debugging HMR/dev-server errors.
- Setting up env vars, a dev proxy, or a lib build (`build.lib`).
- Optimising chunks, dependency pre-bundling, or SSR externals.
- Confirming a prod bundle with `vite build && vite preview`.

Not for webpack/Turbopack, or for Nuxt config (load `nuxt`).

## How to run

1. **Config.** Use `defineConfig` for types; the function form
   (`({ command, mode }) => ...`) when dev and build differ.
   `loadEnv(mode, root, ['VITE_'])` reads env in config — never `''`, which
   exposes every secret to `define`.
2. **Plugins.** Start from the ecosystem: `@vitejs/plugin-vue`,
   `vite-tsconfig-paths`, `vite-plugin-checker` (Vite does not type-check),
   `rollup-plugin-visualizer`. Author a plugin only when none fits; give it a
   unique `name` and scope it with `enforce`/`apply`.
3. **Env vars.** Only `VITE_` vars reach the client, statically inlined — treat
   them as public and keep secrets server-side. Keep `build.sourcemap: false`
   unless uploading to an error tracker.
4. **Proxy.** Route API calls in dev with `server.proxy`; add `changeOrigin`
   for virtual-hosted backends and `ws: true` for WebSockets.
5. **Build.** Split vendors with `build.rolldownOptions.output.manualChunks`
   (object form, a few named groups; avoid one-chunk-per-package). In library
   mode externalise every peer dep and emit types with `vite-plugin-dts`.
6. **SSR and migration.** Move a broken dep between `ssr.external` (require) and
   `ssr.noExternal` (force-bundle). Vite 7+ uses `build.minify: 'oxc'` and the
   `hotUpdate` hook — update plugins still on `esbuild`/`handleHotUpdate`.

## Quick reference

```ts
// vite.config.ts
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), ['VITE_'])
  return {
    plugins: [vue()],
    define: { __API_URL__: JSON.stringify(env.VITE_API_URL) },
    server: command === 'serve'
      ? { proxy: { '/api': { target: 'http://localhost:8080', changeOrigin: true } } }
      : undefined,
    build: { rolldownOptions: { output: { manualChunks: { vue: ['vue', 'vue-router', 'pinia'] } } } },
  }
})
```

## Pitfalls

- `vite build` transpiles but does not type-check; run `vue-tsc --noEmit` or
  `vite-plugin-checker` in CI or type errors ship.
- `vite preview` is a smoke test, not a production server; deploy `dist/`.
- Stale `node_modules/.vite` causes phantom errors — clear it after dep changes.
- Barrel re-exports and implicit import extensions slow the dev server.
- Dev transforms differ from the build; verify with `vite build && preview`.

## Verification

Name the config change and the command you ran (`vite build && vite preview`, or
a dev-server check). Ask for the Vite version and the build output; bind a shell
only if you have one, and say which errors you could not reproduce.

<!-- adapted from affaan-m/ECC: skills/vite-patterns -->
