<script setup lang="ts">
import { FormSubmit } from './sectile';
// The submit button of a sectile form. Like Button it stays focusable while unavailable.
const props = defineProps<{ variant?: 'primary' | 'danger'; small?: boolean; disabled?: boolean }>();
const press = (event: MouseEvent) => { if (props.disabled) event.preventDefault(); };
</script>
<template>
  <FormSubmit as-child><button type="submit" :class="[props.variant, { small }]" :aria-disabled="disabled ? 'true' : undefined" @click="press"><slot /></button></FormSubmit>
</template>
