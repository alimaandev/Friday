import { describe, it, expect, vi, beforeEach } from 'vitest'
import { EventBus } from '../core/EventBus'

describe('EventBus', () => {
  let bus: EventBus

  beforeEach(() => {
    bus = new EventBus()
  })

  it('should be a singleton via get()', () => {
    const a = EventBus.get()
    const b = EventBus.get()
    expect(a).toBe(b)
  })

  it('should register and emit events', () => {
    const fn = vi.fn()
    bus.on('test', fn)
    bus.emit('test', 'a', 'b')
    expect(fn).toHaveBeenCalledWith('a', 'b')
  })

  it('should return an unsubscribe function', () => {
    const fn = vi.fn()
    const unsub = bus.on('test', fn)
    unsub()
    bus.emit('test')
    expect(fn).not.toHaveBeenCalled()
  })

  it('should handle off()', () => {
    const fn = vi.fn()
    bus.on('test', fn)
    bus.off('test', fn)
    bus.emit('test')
    expect(fn).not.toHaveBeenCalled()
  })

  it('should not throw when emitting unregistered event', () => {
    expect(() => bus.emit('nonexistent')).not.toThrow()
  })

  it('should support multiple listeners', () => {
    const fn1 = vi.fn()
    const fn2 = vi.fn()
    bus.on('test', fn1)
    bus.on('test', fn2)
    bus.emit('test')
    expect(fn1).toHaveBeenCalledOnce()
    expect(fn2).toHaveBeenCalledOnce()
  })

  it('should work with shared singleton across modules', () => {
    const fn = vi.fn()
    EventBus.get().on('shared', fn)
    EventBus.get().emit('shared', 42)
    expect(fn).toHaveBeenCalledWith(42)
  })

  it('listenerCount should track registered listeners', () => {
    expect(bus.listenerCount('test')).toBe(0)
    bus.on('test', vi.fn())
    bus.on('test', vi.fn())
    expect(bus.listenerCount('test')).toBe(2)
    bus.emit('test')
    expect(bus.listenerCount('test')).toBe(2)
  })

  it('listenerCount should return 0 after unsubscribe', () => {
    const unsub = bus.on('test', vi.fn())
    expect(bus.listenerCount('test')).toBe(1)
    unsub()
    expect(bus.listenerCount('test')).toBe(0)
  })

  it('eventNames should list registered events', () => {
    expect(bus.eventNames()).toEqual([])
    bus.on('alpha', vi.fn())
    bus.on('beta', vi.fn())
    bus.on('gamma', vi.fn())
    expect(bus.eventNames()).toContain('alpha')
    expect(bus.eventNames()).toContain('beta')
    expect(bus.eventNames()).toContain('gamma')
  })

  it('eventNames should not include unregistered events', () => {
    bus.on('alpha', vi.fn())
    expect(bus.eventNames()).not.toContain('nonexistent')
  })
})
