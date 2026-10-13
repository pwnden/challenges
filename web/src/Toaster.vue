<script setup lang="ts">
import { ToastClose, ToastProvider, ToastRoot, ToastTitle, ToastViewport } from '@sectile/vue/toast';
import type { ToastMessage } from './toasts';
// A notification that appears at the top of the page, announces itself and closes by itself.
const props = defineProps<{ toasts: readonly ToastMessage[] }>();
const emit = defineEmits<{ 'update:toasts': [toasts: readonly ToastMessage[]] }>();
// The provider reports the list it still holds after a timeout or a close; every item came from this list.
const keep = (items: readonly { id: string }[]) => emit('update:toasts', props.toasts.filter(toast => items.some(item => item.id === toast.id)));
</script>
<template>
  <ToastProvider :toasts="toasts" :default-duration-ms="5000" close-label="알림 닫기" @update:toasts="keep" v-slot="{ toasts: items }">
    <ToastViewport class="toaster" label="알림">
      <ToastRoot v-for="item in items" :key="item.id" :value="item.id" class="toast">
        <ToastTitle class="toast-title">{{ item.title }}</ToastTitle>
        <slot name="extra" :item="item" />
        <ToastClose class="toast-close">닫기</ToastClose>
      </ToastRoot>
    </ToastViewport>
  </ToastProvider>
</template>
<style>
/* Zero height and sticky: below the page header at the top, pinned to the viewport edge once the page scrolls. */
.toaster { position: sticky; z-index: 10; top: 0.75rem; display: grid; gap: 0.5rem; width: min(34rem, 100%); height: 0; margin: 0 auto; padding: 0; overflow: visible; list-style: none; pointer-events: none; }
.toast { display: flex; flex-wrap: wrap; align-items: center; gap: 0.25rem 0.75rem; padding: 0.7rem 0.9rem; color: var(--ink); background: var(--paper); border: 1px solid var(--line-strong); border-radius: 0.5rem; box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25); pointer-events: auto; word-break: keep-all; overflow-wrap: break-word; }
.toast[data-kind='error'] { color: var(--danger); background: var(--danger-tint); border-color: var(--danger); }
.toast[data-kind='success'] { color: var(--success); background: var(--success-tint); border-color: var(--success); }
.toast-title { flex: 1 1 auto; font-weight: 650; }
.toast a { color: inherit; font-weight: 650; }
.toast-close { height: 2rem; padding: 0 0.6rem; color: inherit; background: transparent; border: 1px solid currentColor; border-radius: 0.4rem; font-size: 0.85rem; font-weight: 600; }
.toast-close:hover { background: rgba(0, 0, 0, 0.08); }
</style>
