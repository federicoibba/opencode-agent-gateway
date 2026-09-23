---
name: vue
description: Write and review Vue 3 components with the Composition API.
---

# Vue 3

Build and review Vue 3 components using the Composition API and modern
tooling, keeping to the conventions already in the project.

## When to use

Use this when the user is writing or reviewing `.vue` files, a Vue component
library, or asks about reactivity, `<script setup>`, composables, Pinia or Vue
Router.

## How to run

1. **`<script setup>` + TypeScript.** Prefer `<script setup lang="ts">` with
   `defineProps`, `defineEmits` and `defineModel`. Type the public surface; do not
   reach for the Options API unless the file already uses it.
2. **Props and events.** One-way data flow: props down, events up. Do not mutate
   props; emit a typed event or use `defineModel` for two-way bindings.
3. **Composables.** Extract reusable stateful logic into `useXxx` composables
   returning refs. Keep them framework-agnostic where possible.
4. **Reactivity.** Use `ref` for primitives and `reactive` for object state;
   reach for `computed` over `watch` for derived values, and clean up watchers
   and listeners in `onUnmounted`.
5. **Keys and lists.** Always key `v-for` with a stable id, never the index when
   the list can reorder.
6. **Performance.** Use `v-once`/`v-memo` only with a measured reason; prefer
   splitting components over micro-optimising renders.

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

- Destructuring `reactive` loses reactivity; use `toRefs` or a `ref`.
- A `watch` that writes the value it watches loops; use `computed` instead.
- `v-if` and `v-for` on the same element is ambiguous; filter in a `computed`.
- Forgetting to remove a global listener in `onUnmounted` leaks across routes.

## Verification

Point at the component and one test or manual path that exercises it, and name
anything you could not verify (e.g. SSR-only behaviour or a store's runtime data).
