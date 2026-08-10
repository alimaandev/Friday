export type ToastKind = 'success' | 'error' | 'warning' | 'info'

export interface ToastItem {
  id: number
  kind: ToastKind
  message: string
}

type Listener = (toasts: ToastItem[]) => void

let nextId = 1
const listeners = new Set<Listener>()
let current: ToastItem[] = []

function notify() {
  listeners.forEach(l => l(current))
}

export function clearToasts() {
  current = []
  notify()
}

export function toast(kind: ToastKind, message: string, ttl = 4500) {
  const item: ToastItem = { id: nextId++, kind, message }
  current = [...current, item]
  notify()
  setTimeout(() => {
    current = current.filter(t => t.id !== item.id)
    notify()
  }, ttl)
}

export function dismissToast(id: number) {
  current = current.filter(t => t.id !== id)
  notify()
}

export function getToasts(): ToastItem[] {
  return current
}

export function subscribeToasts(listener: Listener) {
  listeners.add(listener)
  return () => { listeners.delete(listener) }
}