import { describe, it, expect, beforeEach } from 'vitest'
import { useStore, state } from '../core/StateManager'

describe('StateManager', () => {
  beforeEach(() => {
    useStore.setState({
      orb: 'idle',
      sessions: [{ id: 'default', title: 'New session', messages: [], createdAt: Date.now() }],
      activeSessionId: 'default',
      sidebarCollapsed: false,
      commandPaletteOpen: false,
      voiceOutputEnabled: false,
      wakeWordEnabled: false,
      voiceLanguage: 'en-US',
      persona: 'friday',
      loading: false,
      metrics: { cpu: 12, memory: 34, latency: 0, contextWindow: 4096, tokenUsage: 0, model: 'openrouter/free', provider: 'OpenRouter' },
    })
  })

  it('should get current state', () => {
    const s = state.get()
    expect(s.orb).toBe('idle')
    expect(s.persona).toBe('friday')
  })

  it('should return active session', () => {
    const session = state.activeSession
    expect(session.id).toBe('default')
    expect(session.messages).toEqual([])
  })

  it('should set partial state', () => {
    state.set({ orb: 'thinking' })
    expect(useStore.getState().orb).toBe('thinking')
  })

  it('should update messages via callback', () => {
    state.updateMessages(msgs => [...msgs, { id: '1', role: 'user', content: 'hi' }])
    const msgs = state.activeSession.messages
    expect(msgs).toHaveLength(1)
    expect(msgs[0].content).toBe('hi')
  })

  it('should set orb state', () => {
    state.setOrb('speaking')
    expect(useStore.getState().orb).toBe('speaking')
  })

  it('should set loading state', () => {
    state.setLoading(true)
    expect(useStore.getState().loading).toBe(true)
  })

  it('should set metrics partially', () => {
    state.setMetrics({ cpu: 99, latency: 42 })
    const m = useStore.getState().metrics
    expect(m.cpu).toBe(99)
    expect(m.latency).toBe(42)
    expect(m.memory).toBe(34) // unchanged
  })

  it('should set voice language', () => {
    state.setVoiceLanguage('hi-IN')
    expect(useStore.getState().voiceLanguage).toBe('hi-IN')
  })

  it('should set persona and persist to localStorage', () => {
    state.setPersona('jarvis')
    expect(useStore.getState().persona).toBe('jarvis')
    expect(localStorage.getItem('friday_persona')).toBe('jarvis')
  })

  it('should handle empty sessions gracefully', () => {
    useStore.setState({ sessions: [], activeSessionId: '' })
    const session = state.activeSession
    expect(session).toBeUndefined()
  })
})
