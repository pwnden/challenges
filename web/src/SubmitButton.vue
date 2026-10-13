<script setup lang="ts">
import { FormSubmit } from './sectile';
// The submit button of a sectile form. It takes the shared button classes through `variant`.
defineProps<{ variant?: 'primary' | 'danger'; small?: boolean; disabled?: boolean }>();
</script>
<template>
  <FormSubmit as-child><button type="submit" :class="[variant, { small }]" :disabled="disabled"><slot /></button></FormSubmit>
</template>
