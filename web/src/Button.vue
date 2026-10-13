<script setup lang="ts">
// A button that keeps keyboard focus while it is busy or unavailable: it is marked
// aria-disabled and ignores clicks instead of using the disabled attribute, which would drop focus.
const props = defineProps<{ variant?: 'primary' | 'danger'; small?: boolean; disabled?: boolean }>();
const emit = defineEmits<{ click: [event: MouseEvent] }>();
const press = (event: MouseEvent) => { if (props.disabled) event.preventDefault(); else emit('click', event); };
</script>
<template>
  <button type="button" :class="[variant, { small }]" :aria-disabled="disabled ? 'true' : undefined" @click="press"><slot /></button>
</template>
