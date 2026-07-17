import type { OrbState, Session, Message, SystemMetrics } from '../types'
import { EventBus } from './EventBus'

interface AppState {
  orb: OrbState
  sessions: Session[]
  activeSessionId: string
  sidebarCollapsed: boolean
  settingsOpen: boolean
  commandPaletteOpen: boolean
  voiceActive: boolean
  loading: boolean
  metrics: SystemMetrics
}

const DEFAULT_METRICS: SystemMetrics = {
  cpu: 12,
  memory: 34,
  latency: 0,
  contextWindow: 4096,
  tokenUsage: 0,
  model: 'openrouter/free',
  provider: 'OpenRouter',
}

class StateManager {
  private state: AppState
  private listeners = new Set<() => void>()
  private pending = false

  constructor() {
    this.state = {
      orb: 'idle',
      sessions: [{ id: 'default', title: 'New session', messages: [], createdAt: Date.now() }],
      activeSessionId: 'default',
      sidebarCollapsed: false,
      settingsOpen: false,
      commandPaletteOpen: false,
      voiceActive: false,
      loading: false,
      metrics: DEFAULT_METRICS,
    }
  }

  get(): AppState {
    return this.state
  }

  get activeSession(): Session {
    return this.state.sessions.find(s => s.id === this.state.activeSessionId) || this.state.sessions[0]
  }

  set(partial: Partial<AppState>) {
    Object.assign(this.state, partial)
    this.schedule()
  }

  updateMessages(fn: (msgs: Message[]) => Message[]) {
    const s = this.activeSession
    s.messages = fn(s.messages)
    this.state.sessions = this.state.sessions.map(x => x.id === s.id ? s : x)
    this.schedule()
  }

  setOrb(state: OrbState) {
    this.state.orb = state
    EventBus.get().emit('orb:state', state)
    this.schedule()
  }

  setLoading(v: boolean) {
    this.state.loading = v
    this.schedule()
  }

  setMetrics(partial: Partial<SystemMetrics>) {
    Object.assign(this.state.metrics, partial)
    this.schedule()
  }

  subscribe(fn: () => void): () => void {
    this.listeners.add(fn)
    return () => this.listeners.delete(fn)
  }

  private schedule() {
    if (this.pending) return
    this.pending = true
    requestAnimationFrame(() => {
      this.pending = false
      this.listeners.forEach(fn => fn())
    })
  }
}

export const state = new StateManager()
