---
name: vue
description: >-
  Write and review Vue 3 components with the Composition API: reactivity,
  props/emits/slots contracts, composable cleanup, template security, list
  keys, render performance and SSR safety. Load it for .vue files, Pinia or
  Vue Router work; not for React, Svelte or plain TypeScript with no Vue.
metadata:
  short-description: Vue 3 Composition API patterns
---

# Vue 3

Build and review Vue 3 components using the Composition API and modern
tooling, keeping to the conventions already in the project.

## When to use

- The user shares a `.vue` file, a diff touching one, or a Vue component library.
- Questions about reactivity (`ref`/`reactive`/`computed`/`watch`), `<script setup>`,
  composables, props/emits/slots, Pinia or Vue Router.
- Reviewing template security (`v-html`, dynamic `:href`/`:src`) or SSR safety.

Do not load this for React, Svelte, or TypeScript with no Vue imports.

## How to run

1. **`<script setup lang="ts">` + typed surface.** Use `defineProps`,
   `defineEmits`, `defineModel` and `defineSlots`; type the public API. Keep the
   Options API only in files that already use it.
2. **One-way data flow.** Never mutate a prop: use `defineModel()` for two-way
   bindings and typed emits otherwise. Destructured props are reactive in Vue
   3.5+, but `watch(count)` still fails — wrap the getter: `watch(() => count)`.
3. **Reactivity.** `ref` for primitives and replaceable state, `reactive` for
   objects mutated in place, `computed` for derived values. Watch the value
   (`watch(() => myRef.value)`), never the ref object.
4. **Composables.** Prefix `use`, return refs/computeds, accept reactive input
   via `MaybeRef`/`toValue`. No module-scope side effects; clean up timers,
   listeners and requests in `onUnmounted` or `onWatcherCleanup`.
5. **Lists and keys.** Key `v-for` with a stable id, never the index when the
   list can reorder. Never put `v-if` and `v-for` on one element; filter in a
   `computed`.
6. **Security.** Never bind user input to `v-html` without an allowlist
   sanitizer at the same call site. Validate URL schemes on dynamic `:href`/
   `:src` so `javascript:`/`data:` cannot execute.
7. **Performance and SSR.** Split components before micro-optimising; reach for
   `v-memo`/`v-once`/`shallowRef` only with a measured reason. Keep `window`,
   `document` and `localStorage` out of top-level setup — guard them behind
   `onMounted`, `import.meta.client` or `<ClientOnly>`.

## Quick reference

```vue
<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{ items: string[] }>()
const emit = defineEmits<{ select: [value: string] }>()

const query = ref('')
const matches = computed(() =>
  props.items.filter((item) => item.includes(query.value)),
)
</script>

<template>
  <ul>
    <li v-for="item in matches" :key="item">
      <button type="button" @click="emit('select', item)">{{ item }}</button>
    </li>
  </ul>
</template>
```

## Pitfalls

- Destructuring a `reactive` object loses reactivity; use `toRefs` or a `ref`.
- Replacing a `reactive` object wholesale breaks it; mutate or `Object.assign`.
- A `watch` that writes the value it watches loops; use `computed` instead.
- Watchers without cleanup leak and race; use `onCleanup`/`onWatcherCleanup`.
- Index keys attach state to the wrong row when a list reorders.
- `v-model` on a computed with no setter silently drops input.

## Verification

Name the component plus one test or manual path that exercises it (mount and
assert the emitted event, or walk the route). Ask for the diff or files when
none are bound, and name what you could not verify — SSR-only behaviour,
runtime store data, or a live API response.

<!-- adapted from affaan-m/ECC: skills/vue-patterns, agents/vue-reviewer.md; base: workspaces/agents/frontend-vue/skills/vue -->
