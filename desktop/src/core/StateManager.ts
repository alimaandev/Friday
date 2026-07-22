import { create } from 'zustand'
import type { OrbState, Session, Message, SystemMetrics } from '../types'
import { EventBus } from './EventBus'

interface AppState {
  orb: OrbState
  sessions: Session[]
  activeSessionId: string
  sidebarCollapsed: boolean
  commandPaletteOpen: boolean
  voiceOutputEnabled: boolean
  wakeWordEnabled: boolean
  voiceLanguage: string
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

const initialState: AppState = {
  orb: 'idle',
  sessions: [{ id: 'default', title: 'New session', messages: [], createdAt: Date.now() }],
  activeSessionId: 'default',
  sidebarCollapsed: false,
  commandPaletteOpen: false,
  voiceOutputEnabled: false,
  wakeWordEnabled: false,
  voiceLanguage: 'en-US',
  loading: false,
  metrics: DEFAULT_METRICS,
}

export const useStore = create<AppState>()(() => initialState)

/* ─── Imperative API (backward-compatible singleton) ─── */
class StateManager {
  get(): AppState {
    return useStore.getState()
  }

  get activeSession(): Session {
    const s = useStore.getState()
    return s.sessions.find(ses => ses.id === s.activeSessionId) || s.sessions[0]
  }

  set(partial: Partial<AppState>) {
    useStore.setState(partial)
  }

  updateMessages(fn: (msgs: Message[]) => Message[]) {
    const s = useStore.getState()
    const active = s.sessions.find(ses => ses.id === s.activeSessionId) || s.sessions[0]
    active.messages = fn(active.messages)
    useStore.setState({
      sessions: s.sessions.map(x => x.id === active.id ? active : x),
    })
  }

  setOrb(orb: OrbState) {
    useStore.setState({ orb })
    EventBus.get().emit('orb:state', orb)
  }

  setLoading(v: boolean) {
    useStore.setState({ loading: v })
  }

  setMetrics(partial: Partial<SystemMetrics>) {
    const current = useStore.getState().metrics
    useStore.setState({ metrics: { ...current, ...partial } })
  }

  setVoiceLanguage(lang: string) {
    useStore.setState({ voiceLanguage: lang })
  }
}

export const state = new StateManager()