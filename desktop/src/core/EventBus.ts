type Listener = (...args: any[]) => void

export class EventBus {
  private listeners = new Map<string, Set<Listener>>()
  private static instance: EventBus

  static get(): EventBus {
    if (!EventBus.instance) EventBus.instance = new EventBus()
    return EventBus.instance
  }

  on(event: string, fn: Listener): () => void {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set())
    this.listeners.get(event)!.add(fn)
    return () => this.listeners.get(event)?.delete(fn)
  }

  emit(event: string, ...args: any[]) {
    this.listeners.get(event)?.forEach(fn => fn(...args))
  }

  off(event: string, fn: Listener) {
    this.listeners.get(event)?.delete(fn)
  }
}
