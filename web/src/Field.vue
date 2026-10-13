<script setup lang="ts">
import { useId } from 'vue';
import { TextField } from './sectile';
// A labeled text input or text area. Other attributes such as name, maxlength or required go to the input.
defineOptions({ inheritAttrs: false });
defineProps<{ label: string; multiline?: boolean; disabled?: boolean; id?: string }>();
const model = defineModel<string>();
const generated = useId();
</script>
<template>
  <label :for="id ?? generated">{{ label }}
    <TextField v-bind="$attrs" :id="id ?? generated" v-model="model" :multiline="multiline" :disabled="disabled" />
  </label>
</template>
