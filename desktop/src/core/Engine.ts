type TickFn = (dt: number, time: number) => void

class Engine {
  private ticks = new Set<TickFn>()
  private raf: number | null = null
  private last = 0
  private running = false

  start() {
    if (this.running) return
    this.running = true
    this.last = performance.now()
    const loop = (now: number) => {
      if (!this.running) return
      const dt = Math.min((now - this.last) / 1000, 0.05)
      this.last = now
      this.ticks.forEach(fn => fn(dt, now))
      this.raf = requestAnimationFrame(loop)
    }
    this.raf = requestAnimationFrame(loop)
  }

  stop() {
    this.running = false
    if (this.raf !== null) cancelAnimationFrame(this.raf)
    this.raf = null
  }

  on(fn: TickFn): () => void {
    this.ticks.add(fn)
    return () => this.ticks.delete(fn)
  }
}

export const engine = new Engine()
