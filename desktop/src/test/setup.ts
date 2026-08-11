import '@testing-library/jest-dom'

class LocalStorageMock {
  private store: Record<string, string> = {}
  clear() { this.store = {} }
  getItem(key: string) { return this.store[key] ?? null }
  setItem(key: string, value: string) { this.store[key] = value }
  removeItem(key: string) { delete this.store[key] }
  get length() { return Object.keys(this.store).length }
  key(index: number) { return Object.keys(this.store)[index] ?? null }
}

if (!globalThis.localStorage) {
  globalThis.localStorage = new LocalStorageMock()
}

if (!HTMLElement.prototype.scrollIntoView) {
  HTMLElement.prototype.scrollIntoView = () => {}
}
