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
  persona: string
  loading: boolean
  metrics: SystemMetrics
  zen: boolean
  handsFree: boolean
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
  persona: (() => { try { return localStorage.getItem('friday_persona') || 'friday' } catch { return 'friday' } })(),
  loading: false,
  metrics: DEFAULT_METRICS,
  zen: (() => { try { return (localStorage.getItem('friday_ui_zen') || '1') !== '0' } catch { return true } })(),
  handsFree: (() => { try { return localStorage.getItem('friday_hands_free') === '1' } catch { return false } })(),
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

  setPersona(key: string) {
    useStore.setState({ persona: key })
    try { localStorage.setItem('friday_persona', key) } catch {}
  }

  setZen(zen: boolean) {
    useStore.setState({ zen })
    try { localStorage.setItem('friday_ui_zen', zen ? '1' : '0') } catch {}
  }

  toggleZen() {
    this.setZen(!useStore.getState().zen)
  }

  setHandsFree(v: boolean) {
    useStore.setState({ handsFree: v })
    try { localStorage.setItem('friday_hands_free', v ? '1' : '0') } catch {}
  }

  toggleHandsFree() {
    this.setHandsFree(!useStore.getState().handsFree)
  }
}

export const state = new StateManager()