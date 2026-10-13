export interface ToastMessage { id: string; title: string; kind: 'error' | 'success'; durationMs: number }
let sequence = 0;
// Keep the latest few messages; an error stays a little longer than a confirmation.
export function addToast(list: readonly ToastMessage[], kind: ToastMessage['kind'], title: string): ToastMessage[] {
  return [...list.slice(-2), { id: `toast-${++sequence}`, title, kind, durationMs: kind === 'error' ? 7000 : 4000 }];
}
